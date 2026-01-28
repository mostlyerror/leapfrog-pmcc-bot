"""
Tradier API wrapper for market data
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TradierAPI:
    """Tradier API client"""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        })

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for a symbol"""
        try:
            data = self._make_request('/markets/quotes', {'symbols': symbol})
            quotes = data.get('quotes', {}).get('quote')

            if not quotes:
                logger.warning(f"No quote data for {symbol}")
                return None

            # Handle single quote vs list of quotes
            if isinstance(quotes, list):
                quotes = quotes[0]

            return quotes
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None

    def get_options_chain(self, symbol: str, expiration: str) -> List[Dict[str, Any]]:
        """Get options chain for a symbol and expiration"""
        try:
            data = self._make_request('/markets/options/chains', {
                'symbol': symbol,
                'expiration': expiration,
                'greeks': 'true'
            })

            options = data.get('options', {}).get('option', [])
            if not isinstance(options, list):
                options = [options] if options else []

            return options
        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol} {expiration}: {e}")
            return []

    def get_options_expirations(self, symbol: str) -> List[str]:
        """Get available expiration dates for a symbol"""
        try:
            data = self._make_request('/markets/options/expirations', {
                'symbol': symbol,
                'includeAllRoots': 'true'
            })

            expirations = data.get('expirations', {}).get('date', [])
            if not isinstance(expirations, list):
                expirations = [expirations] if expirations else []

            return expirations
        except Exception as e:
            logger.error(f"Error fetching expirations for {symbol}: {e}")
            return []

    def get_option_quote(self, option_symbol: str) -> Optional[Dict[str, Any]]:
        """Get quote for an option symbol"""
        return self.get_quote(option_symbol)

    def find_options_by_criteria(self, symbol: str, expiration: str,
                                  option_type: str = 'call',
                                  min_strike: Optional[float] = None,
                                  max_strike: Optional[float] = None,
                                  min_delta: Optional[float] = None,
                                  max_delta: Optional[float] = None) -> List[Dict[str, Any]]:
        """Find options matching specific criteria"""
        chain = self.get_options_chain(symbol, expiration)

        # Filter by type
        filtered = [opt for opt in chain if opt.get('option_type') == option_type]

        # Filter by strike
        if min_strike is not None:
            filtered = [opt for opt in filtered if opt.get('strike', 0) >= min_strike]
        if max_strike is not None:
            filtered = [opt for opt in filtered if opt.get('strike', 0) <= max_strike]

        # Filter by delta (call delta should be positive)
        if min_delta is not None or max_delta is not None:
            greeks_filtered = []
            for opt in filtered:
                greeks = opt.get('greeks', {})
                if not greeks:
                    continue

                delta = greeks.get('delta', 0)
                # For calls, delta is positive (0 to 1)
                delta = abs(delta)

                if min_delta is not None and delta < min_delta:
                    continue
                if max_delta is not None and delta > max_delta:
                    continue

                greeks_filtered.append(opt)

            filtered = greeks_filtered

        return filtered

    def calculate_days_to_expiration(self, expiration: str) -> int:
        """Calculate days to expiration"""
        try:
            exp_date = datetime.strptime(expiration, '%Y-%m-%d')
            today = datetime.now()
            return (exp_date - today).days
        except ValueError:
            logger.error(f"Invalid expiration date format: {expiration}")
            return 0

    def get_expirations_by_dte_range(self, symbol: str,
                                      min_dte: int, max_dte: int) -> List[str]:
        """Get expirations within a DTE range"""
        all_expirations = self.get_options_expirations(symbol)

        filtered = []
        for exp in all_expirations:
            dte = self.calculate_days_to_expiration(exp)
            if min_dte <= dte <= max_dte:
                filtered.append(exp)

        return filtered

    def format_option_symbol(self, underlying: str, expiration: str,
                            option_type: str, strike: float) -> str:
        """Format option symbol in OCC format"""
        # Example: SPY260321C00730000
        exp_date = datetime.strptime(expiration, '%Y-%m-%d')
        exp_str = exp_date.strftime('%y%m%d')

        type_code = 'C' if option_type.lower() == 'call' else 'P'
        strike_str = f"{int(strike * 1000):08d}"

        return f"{underlying}{exp_str}{type_code}{strike_str}"

    def calculate_annualized_return(self, premium: float, cost_basis: float,
                                     dte: int) -> float:
        """Calculate annualized return on cost basis"""
        if cost_basis <= 0 or dte <= 0:
            return 0.0

        period_return = premium / cost_basis
        annualized = period_return * (365 / dte)
        return annualized * 100  # Return as percentage

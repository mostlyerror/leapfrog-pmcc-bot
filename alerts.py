"""
Alert monitoring and triggering logic
"""
from typing import List, Dict, Any
from datetime import datetime
import logging
from models import Database, ShortCall, Alert
from tradier import TradierAPI
import config

logger = logging.getLogger(__name__)


class AlertMonitor:
    """Monitor positions and trigger alerts"""

    def __init__(self, db: Database, api: TradierAPI):
        self.db = db
        self.api = api
        self.short_call_model = ShortCall(db)
        self.alert_model = Alert(db)

    def check_all_positions(self) -> List[Dict[str, Any]]:
        """Check all active positions and trigger alerts"""
        alerts_triggered = []
        active_positions = self.short_call_model.get_active()

        if not active_positions:
            logger.info("No active short call positions to monitor")
            return alerts_triggered

        logger.info(f"Monitoring {len(active_positions)} active short call positions")

        for position in active_positions:
            try:
                position_alerts = self._check_position(position)
                alerts_triggered.extend(position_alerts)
            except Exception as e:
                logger.error(f"Error checking position {position['id']}: {e}")

        return alerts_triggered

    def _check_position(self, position: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check a single position for alert conditions"""
        alerts = []

        # Get current option quote
        option_symbol = self._build_option_symbol(position)
        quote = self.api.get_option_quote(option_symbol)

        if not quote:
            logger.warning(f"No quote available for {option_symbol}")
            return alerts

        current_price = quote.get('ask', 0)  # Use ask to close (buy to close)
        if current_price <= 0:
            current_price = quote.get('last', 0)

        if current_price <= 0:
            logger.warning(f"Invalid price for {option_symbol}")
            return alerts

        # Calculate profit percentage
        entry_price = position['entry_price']
        profit_pct = (entry_price - current_price) / entry_price if entry_price > 0 else 0

        # Get underlying quote
        underlying_symbol = position['symbol'].split()[0]  # Extract SPY from "SPY Mar 21 2026 $730 Call"
        underlying_quote = self.api.get_quote(underlying_symbol)
        underlying_price = underlying_quote.get('last', 0) if underlying_quote else 0

        # Calculate DTE
        dte = self.api.calculate_days_to_expiration(position['expiration'])

        # Check alert conditions

        # 1. 50% profit alert
        if profit_pct >= config.PROFIT_THRESHOLD_LOW and profit_pct < config.PROFIT_THRESHOLD_HIGH:
            alert = self._create_alert(
                position['id'],
                'profit_50',
                f"🎯 Close candidate: {option_symbol}\n"
                f"Current: ${current_price:.2f} | Entry: ${entry_price:.2f}\n"
                f"Profit: {profit_pct*100:.1f}% (${(entry_price - current_price) * position['quantity'] * 100:.2f})"
            )
            alerts.append(alert)

        # 2. 80% profit alert
        if profit_pct >= config.PROFIT_THRESHOLD_HIGH:
            alert = self._create_alert(
                position['id'],
                'profit_80',
                f"💰 Strong close signal: {option_symbol}\n"
                f"Current: ${current_price:.2f} | Entry: ${entry_price:.2f}\n"
                f"Profit: {profit_pct*100:.1f}% (${(entry_price - current_price) * position['quantity'] * 100:.2f})"
            )
            alerts.append(alert)

        # 3. Strike proximity alert
        if underlying_price > 0:
            strike_distance_pct = abs(underlying_price - position['strike']) / position['strike']
            if strike_distance_pct <= config.STRIKE_PROXIMITY_PCT:
                alert = self._create_alert(
                    position['id'],
                    'strike_threatened',
                    f"⚠️ Strike threatened: {option_symbol}\n"
                    f"Underlying: ${underlying_price:.2f} | Strike: ${position['strike']:.2f}\n"
                    f"Distance: {strike_distance_pct*100:.1f}% | Evaluate roll"
                )
                alerts.append(alert)

        # 4. Low profit + expiration approaching
        if dte <= config.LOW_PROFIT_DTE_THRESHOLD and profit_pct < config.PROFIT_THRESHOLD_LOW:
            alert = self._create_alert(
                position['id'],
                'expiration_approaching',
                f"⏰ Expiration approaching: {option_symbol}\n"
                f"DTE: {dte} | Profit: {profit_pct*100:.1f}%\n"
                f"Consider roll or close"
            )
            alerts.append(alert)

        return alerts

    def _build_option_symbol(self, position: Dict[str, Any]) -> str:
        """Build option symbol from position data"""
        # Extract symbol from stored format "SPY Mar 21 2026 $730 Call"
        parts = position['symbol'].split()
        underlying = parts[0]

        return self.api.format_option_symbol(
            underlying,
            position['expiration'],
            'call',
            position['strike']
        )

    def _create_alert(self, short_call_id: int, alert_type: str,
                     message: str) -> Dict[str, Any]:
        """Create and store alert"""
        # Check if similar alert already exists recently (within 1 hour)
        existing_alerts = self.alert_model.get_unacknowledged()

        for alert in existing_alerts:
            if (alert['short_call_id'] == short_call_id and
                alert['alert_type'] == alert_type):
                # Check if alert is recent (within 1 hour)
                triggered_at = datetime.fromisoformat(alert['triggered_at'])
                if (datetime.now() - triggered_at).seconds < 3600:
                    logger.debug(f"Skipping duplicate alert: {alert_type} for position {short_call_id}")
                    return alert

        # Create new alert
        alert_id = self.alert_model.add(short_call_id, alert_type, message)
        logger.info(f"Alert triggered: {alert_type} for position {short_call_id}")

        return {
            'id': alert_id,
            'short_call_id': short_call_id,
            'alert_type': alert_type,
            'message': message,
            'triggered_at': datetime.now().isoformat()
        }

    def get_position_status(self, short_call_id: int) -> Dict[str, Any]:
        """Get detailed status of a position"""
        position = self.short_call_model.get_by_id(short_call_id)
        if not position:
            return {}

        option_symbol = self._build_option_symbol(position)
        quote = self.api.get_option_quote(option_symbol)

        if not quote:
            return {'error': 'No quote available'}

        current_price = quote.get('ask', quote.get('last', 0))
        entry_price = position['entry_price']
        profit_pct = (entry_price - current_price) / entry_price if entry_price > 0 else 0
        profit_dollars = (entry_price - current_price) * position['quantity'] * 100

        dte = self.api.calculate_days_to_expiration(position['expiration'])

        # Get underlying price
        underlying_symbol = position['symbol'].split()[0]
        underlying_quote = self.api.get_quote(underlying_symbol)
        underlying_price = underlying_quote.get('last', 0) if underlying_quote else 0

        return {
            'position': position,
            'current_price': current_price,
            'profit_pct': profit_pct,
            'profit_dollars': profit_dollars,
            'dte': dte,
            'underlying_price': underlying_price,
            'option_symbol': option_symbol
        }

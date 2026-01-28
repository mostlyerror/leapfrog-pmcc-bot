"""
Roll and new call scanning logic
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from models import Database, ShortCall, LeapsPosition
from tradier import TradierAPI
import config

logger = logging.getLogger(__name__)


class OptionScanner:
    """Scanner for roll candidates and new short calls"""

    def __init__(self, db: Database, api: TradierAPI):
        self.db = db
        self.api = api
        self.short_call_model = ShortCall(db)
        self.leaps_model = LeapsPosition(db)

    def find_roll_candidates(self, short_call_id: int,
                            top_n: int = 3) -> List[Dict[str, Any]]:
        """Find roll candidates for a short call"""
        position = self.short_call_model.get_by_id(short_call_id)
        if not position:
            logger.error(f"Short call {short_call_id} not found")
            return []

        underlying = position['symbol'].split()[0]
        current_strike = position['strike']
        current_expiration = position['expiration']

        logger.info(f"Scanning roll candidates for {underlying} {current_strike}C")

        candidates = []

        # Get current option quote for closing cost
        current_option_symbol = self.api.format_option_symbol(
            underlying, current_expiration, 'call', current_strike
        )
        current_quote = self.api.get_option_quote(current_option_symbol)
        close_cost = current_quote.get('ask', 0) if current_quote else 0

        # Scan different DTE options
        for dte_target in config.ROLL_DTE_OPTIONS:
            expirations = self.api.get_expirations_by_dte_range(
                underlying, dte_target - 5, dte_target + 5
            )

            for expiration in expirations[:2]:  # Limit to 2 expirations per DTE
                dte = self.api.calculate_days_to_expiration(expiration)

                # Scan different strike offsets
                for strike_offset in config.ROLL_STRIKE_OFFSETS:
                    new_strike = current_strike + strike_offset

                    # Get options chain
                    options = self.api.find_options_by_criteria(
                        underlying,
                        expiration,
                        option_type='call',
                        min_strike=new_strike - 0.5,
                        max_strike=new_strike + 0.5,
                        max_delta=config.ROLL_MAX_DELTA
                    )

                    for option in options:
                        bid = option.get('bid', 0)
                        if bid <= 0:
                            continue

                        # Calculate roll credit
                        roll_credit = bid - close_cost

                        delta = option.get('greeks', {}).get('delta', 0)
                        delta = abs(delta)

                        candidates.append({
                            'strike': option['strike'],
                            'expiration': expiration,
                            'dte': dte,
                            'bid': bid,
                            'delta': delta,
                            'roll_credit': roll_credit,
                            'close_cost': close_cost,
                            'net_credit': roll_credit * position['quantity'] * 100,
                            'symbol': option['symbol']
                        })

        # Rank candidates
        # Prefer positive credit, then lower delta
        candidates.sort(key=lambda x: (-x['roll_credit'], x['delta']))

        top_candidates = candidates[:top_n]

        logger.info(f"Found {len(candidates)} roll candidates, returning top {top_n}")
        return top_candidates

    def find_new_call_candidates(self, leaps_id: int,
                                 top_n: int = 5) -> List[Dict[str, Any]]:
        """Find new short call candidates for a LEAPS position"""
        leaps = self.leaps_model.get_by_id(leaps_id)
        if not leaps:
            logger.error(f"LEAPS {leaps_id} not found")
            return []

        underlying = leaps['symbol']
        leaps_strike = leaps['strike']

        # Get adjusted cost basis
        adjusted_cost = self.leaps_model.get_adjusted_cost_basis(leaps_id)

        logger.info(f"Scanning new call candidates for {underlying} LEAPS")

        candidates = []

        # Get expirations in target DTE range
        expirations = self.api.get_expirations_by_dte_range(
            underlying,
            config.TARGET_DTE_MIN,
            config.TARGET_DTE_MAX
        )

        for expiration in expirations[:3]:  # Limit to 3 expirations
            dte = self.api.calculate_days_to_expiration(expiration)

            # Find options with target delta range, above LEAPS strike
            options = self.api.find_options_by_criteria(
                underlying,
                expiration,
                option_type='call',
                min_strike=leaps_strike + 1,
                min_delta=config.TARGET_DELTA_MIN,
                max_delta=config.TARGET_DELTA_MAX
            )

            for option in options:
                bid = option.get('bid', 0)
                if bid <= 0:
                    continue

                delta = option.get('greeks', {}).get('delta', 0)
                delta = abs(delta)

                # Calculate annualized return
                premium = bid * leaps['quantity'] * 100
                ann_return = self.api.calculate_annualized_return(
                    premium / 100,  # Premium per contract
                    adjusted_cost,
                    dte
                )

                candidates.append({
                    'strike': option['strike'],
                    'expiration': expiration,
                    'dte': dte,
                    'bid': bid,
                    'delta': delta,
                    'premium': premium,
                    'annualized_return': ann_return,
                    'symbol': option['symbol']
                })

        # Rank by annualized return, then delta
        candidates.sort(key=lambda x: (-x['annualized_return'], x['delta']))

        top_candidates = candidates[:top_n]

        logger.info(f"Found {len(candidates)} new call candidates, returning top {top_n}")
        return top_candidates

    def format_roll_candidates(self, candidates: List[Dict[str, Any]]) -> str:
        """Format roll candidates for display"""
        if not candidates:
            return "No roll candidates found"

        output = "📊 *Roll Candidates*\n\n"

        for i, candidate in enumerate(candidates, 1):
            credit_indicator = "✅" if candidate['roll_credit'] > 0 else "⚠️"
            output += f"{i}. {credit_indicator} ${candidate['strike']:.0f} exp {candidate['expiration']}\n"
            output += f"   DTE: {candidate['dte']} | Δ: {candidate['delta']:.3f}\n"
            output += f"   Bid: ${candidate['bid']:.2f} | Close: ${candidate['close_cost']:.2f}\n"
            output += f"   Roll Credit: ${candidate['roll_credit']:.2f} (${candidate['net_credit']:.2f} total)\n\n"

        return output

    def format_new_call_candidates(self, candidates: List[Dict[str, Any]]) -> str:
        """Format new call candidates for display"""
        if not candidates:
            return "No new call candidates found"

        output = "📊 *New Short Call Candidates*\n\n"

        for i, candidate in enumerate(candidates, 1):
            output += f"{i}. ${candidate['strike']:.0f} exp {candidate['expiration']}\n"
            output += f"   DTE: {candidate['dte']} | Δ: {candidate['delta']:.3f}\n"
            output += f"   Premium: ${candidate['premium']:.2f}\n"
            output += f"   Ann. Return: {candidate['annualized_return']:.1f}%\n\n"

        return output

from typing import Optional


class ParameterCollector:
    """Generate natural language prompts for missing parameters"""

    PROMPTS = {
        'add_leaps': {
            'symbol': "Which stock symbol? (e.g., SPY, AAPL)",
            'strike': "What strike price? (e.g., 620, 730.50)",
            'expiration': "What expiration date? (e.g., 2027-01-17 or 'Jan 17 2027')",
            'price': "What price did you pay per contract? (e.g., 109.00)",
            'quantity': "How many contracts? (e.g., 2)"
        },
        'add_short': {
            'leaps_id': "Which LEAPS position? (Use /positions to see IDs)",
            'symbol': "Which stock symbol? (e.g., SPY)",
            'strike': "What strike price? (e.g., 730)",
            'expiration': "What expiration date? (e.g., 2026-03-21)",
            'price': "What credit did you receive per contract? (e.g., 6.50)",
            'quantity': "How many contracts? (e.g., 2)"
        },
        'close': {
            'short_call_id': "Which short call do you want to close? (Use /positions to see IDs)",
            'exit_price': "What price did you close at? (e.g., 3.25)"
        },
        'roll': {
            'short_call_id': "Which short call do you want to roll? (Use /positions to see IDs)"
        },
        'newcall': {
            'leaps_id': "For which LEAPS position? (Use /positions to see IDs)"
        }
    }

    def get_prompt(self, intent: str, param: str) -> Optional[str]:
        """Get the natural language prompt for a specific parameter"""
        if intent in self.PROMPTS and param in self.PROMPTS[intent]:
            return self.PROMPTS[intent][param]

        return f"Please provide {param}"

    def format_missing_params_message(self, intent: str, missing: list) -> str:
        """Format a message asking for multiple missing parameters"""
        if not missing:
            return ""

        if len(missing) == 1:
            return self.get_prompt(intent, missing[0])

        # Multiple params needed
        msg = "I need a few more details:\n\n"
        for i, param in enumerate(missing, 1):
            msg += f"{i}. {self.get_prompt(intent, param)}\n"

        return msg.strip()

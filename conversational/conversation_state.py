from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class ConversationStateManager:
    """Track multi-turn conversation state"""

    # Required parameters for each intent
    REQUIRED_PARAMS = {
        'add_leaps': ['symbol', 'strike', 'expiration', 'price', 'quantity'],
        'add_short': ['leaps_id', 'symbol', 'strike', 'expiration', 'price', 'quantity'],
        'close': ['short_call_id', 'exit_price'],
        'roll': ['short_call_id'],
        'newcall': ['leaps_id'],
    }

    def __init__(self):
        self.conversations: Dict[int, Dict[str, Any]] = {}
        self.timeout_minutes = 5

    def start_conversation(self, user_id: int, intent: str) -> None:
        """Start a new conversation for a user"""
        self.conversations[user_id] = {
            'intent': intent,
            'collected_params': {},
            'missing_params': self.REQUIRED_PARAMS.get(intent, []).copy(),
            'last_updated': datetime.now(),
            'turn_count': 0
        }

    def update_params(self, user_id: int, params: Dict[str, Any]) -> None:
        """Update conversation with newly extracted params"""
        if user_id not in self.conversations:
            return

        conv = self.conversations[user_id]

        # Add new params
        conv['collected_params'].update(params)

        # Remove from missing list
        for key in params.keys():
            if key in conv['missing_params']:
                conv['missing_params'].remove(key)

        conv['last_updated'] = datetime.now()
        conv['turn_count'] += 1

    def get_missing_params(self, user_id: int) -> List[str]:
        """Get list of parameters still needed"""
        if user_id not in self.conversations:
            return []

        return self.conversations[user_id]['missing_params']

    def get_collected_params(self, user_id: int) -> Dict[str, Any]:
        """Get all collected parameters so far"""
        if user_id not in self.conversations:
            return {}

        return self.conversations[user_id]['collected_params'].copy()

    def get_intent(self, user_id: int) -> Optional[str]:
        """Get the current conversation intent"""
        if user_id not in self.conversations:
            return None

        return self.conversations[user_id]['intent']

    def is_active(self, user_id: int) -> bool:
        """Check if user has an active conversation"""
        if user_id not in self.conversations:
            return False

        # Check timeout
        conv = self.conversations[user_id]
        elapsed = datetime.now() - conv['last_updated']

        if elapsed > timedelta(minutes=self.timeout_minutes):
            self.clear_conversation(user_id)
            return False

        return True

    def is_complete(self, user_id: int) -> bool:
        """Check if all required params are collected"""
        if user_id not in self.conversations:
            return False

        return len(self.conversations[user_id]['missing_params']) == 0

    def clear_conversation(self, user_id: int) -> None:
        """Clear conversation state for a user"""
        if user_id in self.conversations:
            del self.conversations[user_id]

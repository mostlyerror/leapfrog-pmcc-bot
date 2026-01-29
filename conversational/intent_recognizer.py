import re
from typing import Tuple, Optional


class IntentRecognizer:
    """Maps natural language to bot command intents"""

    PATTERNS = {
        'add_leaps': [
            r'\b(add|buy|new|open)\s+(a\s+)?leaps?\b',
            r'\bleaps?\s+(position|contract)\b',
        ],
        'add_short': [
            r'\b(sell|write|add|open)\s+(a\s+)?(short\s+)?calls?\b',
            r'\bshort\s+call\s+(position|contract)\b',
        ],
        'close': [
            r'\b(close|exit|buy\s+back)\b',
            r'\bclose\s+out\b',
        ],
        'roll': [
            r'\broll\b',
            r'\b(roll\s+up|roll\s+out|extend)\b',
        ],
        'newcall': [
            r'\b(new|another|find)\s+calls?\b',
            r'\bsell\s+another\s+call\b',
        ],
        'positions': [
            r'\b(show|display|list|my)\s+positions?\b',
            r'\bwhat\s+do\s+i\s+have\b',
            r'\bmy\s+portfolio\b',
        ],
        'summary': [
            r'\b(summary|cost\s+basis)\b',
            r'\bhow\s+much\s+premium\b',
        ],
        'help': [
            r'\bhelp\b',
            r'\bcommands?\b',
            r'\bwhat\s+can\s+you\s+do\b',
        ],
    }

    def recognize(self, text: str) -> Tuple[Optional[str], float]:
        """
        Recognize intent from natural language text.
        Returns: (intent, confidence)
        """
        text = text.lower().strip()

        # Check each intent's patterns
        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    confidence = 0.9  # High confidence for direct matches
                    return (intent, confidence)

        return (None, 0.0)

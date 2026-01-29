import re
from typing import Dict, Any, Optional
from datetime import datetime
import dateparser


class EntityExtractor:
    """Extract structured entities from natural language"""

    # Regex patterns
    SYMBOL_PATTERN = r'\b([A-Z]{1,5})\b'
    STRIKE_PATTERN = r'\$?(\d+(?:\.\d{1,2})?)'
    ID_PATTERN = r'#?(\d+)'
    QUANTITY_PATTERN = r'\b(\d+)\s*(?:contracts?|x)?\b'

    def extract(self, text: str) -> Dict[str, Any]:
        """Extract all entities from text"""
        entities = {}

        # Symbol (uppercase letters)
        symbol_match = re.search(self.SYMBOL_PATTERN, text)
        if symbol_match:
            entities['symbol'] = symbol_match.group(1)

        # Extract all numbers
        numbers = re.findall(r'\d+(?:\.\d{1,2})?', text)

        # Try to determine which number is what
        # Look for context clues like "at $X" or "strike X"

        # Strike (usually after "strike" keyword or with $ before call/put)
        strike_match = re.search(r'strike\s+\$?(\d+(?:\.\d{1,2})?)', text, re.IGNORECASE)
        if strike_match:
            entities['strike'] = float(strike_match.group(1))
        elif re.search(r'\$\d+\s*[cp]', text, re.IGNORECASE):
            # Pattern like "$730c"
            match = re.search(r'\$(\d+)', text)
            if match:
                entities['strike'] = float(match.group(1))

        # Price (usually after "at", "for", or with $ sign)
        price_match = re.search(r'(?:at|for|price)\s+\$?(\d+(?:\.\d{1,2})?)', text, re.IGNORECASE)
        if price_match:
            entities['price'] = float(price_match.group(1))

        # ID (usually with # or after "call", "position", "leaps")
        id_match = re.search(r'(?:#|call\s+|position\s+|leaps\s+)(\d+)', text, re.IGNORECASE)
        if id_match:
            entities['id'] = int(id_match.group(1))

        # Quantity
        qty_match = re.search(r'(\d+)\s*(?:contracts?|x)', text, re.IGNORECASE)
        if qty_match:
            entities['quantity'] = int(qty_match.group(1))

        # Date (flexible parsing)
        date_result = self._extract_date(text)
        if date_result:
            entities['expiration'] = date_result

        return entities

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract and normalize dates using dateparser"""
        # Try dateparser for flexible date parsing
        parsed = dateparser.parse(
            text,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': datetime.now()
            }
        )

        if parsed:
            return parsed.strftime('%Y-%m-%d')

        return None

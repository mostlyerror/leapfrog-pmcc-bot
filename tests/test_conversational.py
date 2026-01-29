import pytest
from conversational.intent_recognizer import IntentRecognizer
from conversational.entity_extractor import EntityExtractor
from conversational.conversation_state import ConversationStateManager
from conversational.parameter_collector import ParameterCollector


class TestIntentRecognizer:
    def test_add_leaps_intent(self):
        recognizer = IntentRecognizer()
        intent, conf = recognizer.recognize("add leaps SPY 620 Jan 2027")
        assert intent == 'add_leaps'
        assert conf > 0.7

    def test_close_intent(self):
        recognizer = IntentRecognizer()
        intent, conf = recognizer.recognize("close call 5 at $3.25")
        assert intent == 'close'
        assert conf > 0.7

    def test_positions_intent(self):
        recognizer = IntentRecognizer()
        intent, conf = recognizer.recognize("show my positions")
        assert intent == 'positions'
        assert conf > 0.7

    def test_no_match(self):
        recognizer = IntentRecognizer()
        intent, conf = recognizer.recognize("random gibberish xyz")
        assert intent is None
        assert conf == 0.0


class TestEntityExtractor:
    def test_extract_symbol(self):
        extractor = EntityExtractor()
        entities = extractor.extract("SPY 730 call")
        assert entities['symbol'] == 'SPY'

    def test_extract_strike(self):
        extractor = EntityExtractor()
        entities = extractor.extract("strike 730.50")
        assert entities['strike'] == 730.50

    def test_extract_price(self):
        extractor = EntityExtractor()
        entities = extractor.extract("at $6.50")
        assert entities['price'] == 6.50

    def test_extract_id(self):
        extractor = EntityExtractor()
        entities = extractor.extract("close call #5")
        assert entities['id'] == 5

    def test_extract_quantity(self):
        extractor = EntityExtractor()
        entities = extractor.extract("2 contracts")
        assert entities['quantity'] == 2


class TestConversationState:
    def test_start_conversation(self):
        manager = ConversationStateManager()
        manager.start_conversation(123, 'add_leaps')
        assert manager.is_active(123)
        assert manager.get_intent(123) == 'add_leaps'

    def test_update_params(self):
        manager = ConversationStateManager()
        manager.start_conversation(123, 'close')
        manager.update_params(123, {'short_call_id': 5})

        params = manager.get_collected_params(123)
        assert params['short_call_id'] == 5

    def test_is_complete(self):
        manager = ConversationStateManager()
        manager.start_conversation(123, 'close')
        assert not manager.is_complete(123)

        manager.update_params(123, {'short_call_id': 5, 'exit_price': 3.25})
        assert manager.is_complete(123)


class TestParameterCollector:
    def test_get_prompt(self):
        collector = ParameterCollector()
        prompt = collector.get_prompt('close', 'short_call_id')
        assert 'short call' in prompt.lower()

    def test_format_multiple_params(self):
        collector = ParameterCollector()
        msg = collector.format_missing_params_message('close', ['short_call_id', 'exit_price'])
        assert 'short call' in msg.lower()
        assert 'price' in msg.lower()

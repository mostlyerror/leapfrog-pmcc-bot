# Conversational Interface

## Overview

The PMCC Bot now supports natural language interaction in addition to traditional slash commands. Users can interact with the bot conversationally, and the bot will intelligently extract parameters and guide users through multi-turn conversations when information is missing.

## Features

- **Intent Recognition**: Understands natural language commands like "close call 5 at $3.25" or "show my positions"
- **Entity Extraction**: Automatically extracts symbols, strikes, prices, dates, and IDs from messages
- **Multi-Turn Conversations**: Asks for missing parameters in a friendly, natural way
- **Backward Compatible**: All slash commands continue to work exactly as before
- **No External APIs**: Uses regex and pattern matching only - fast and private

## Architecture

### Four Core Components

1. **IntentRecognizer** (`conversational/intent_recognizer.py`)
   - Maps natural language to bot intents
   - Supports: add_leaps, add_short, close, roll, newcall, positions, summary, help

2. **EntityExtractor** (`conversational/entity_extractor.py`)
   - Extracts structured data from text
   - Supports: symbols, strikes, prices, dates, quantities, IDs
   - Uses `dateparser` for flexible date parsing

3. **ConversationStateManager** (`conversational/conversation_state.py`)
   - Tracks partial information across messages
   - 5-minute timeout for inactive conversations
   - Maintains per-user conversation state

4. **ParameterCollector** (`conversational/parameter_collector.py`)
   - Generates natural language prompts for missing parameters
   - Context-aware prompts based on intent

## Usage Examples

### Complete Command in One Message
```
User: "close call 5 at $3.25"
Bot: ✅ Short Call Closed
     Position: SPY
     Entry: $6.50 | Exit: $3.25
     Profit: $3.25
```

### Multi-Turn Conversation
```
User: "close a call"
Bot: "Which short call do you want to close? (Use /positions to see IDs)"

User: "5"
Bot: "What price did you close at? (e.g., 3.25)"

User: "$3.25"
Bot: ✅ Short Call Closed
```

### Natural Language Variations
All of these work:
- "show my positions" → /positions
- "what do I have" → /positions
- "sell SPY call" → starts add_short flow
- "buy back call 5 at 3.25" → /close 5 3.25
- "roll call 5" → /roll 5

### Slash Commands Still Work
```
User: "/close 5 3.25"
Bot: ✅ Short Call Closed
```

## Supported Intents

| Intent | Natural Language Examples | Slash Command |
|--------|---------------------------|---------------|
| add_leaps | "add leaps", "buy leaps", "open leaps" | /add_leaps |
| add_short | "sell call", "write call", "short call" | /add_short |
| close | "close", "exit", "buy back" | /close |
| roll | "roll", "roll up", "roll out" | /roll |
| newcall | "new call", "find calls" | /newcall |
| positions | "show positions", "my positions" | /positions |
| summary | "summary", "cost basis" | /summary |
| help | "help", "commands" | /help |

## Entity Extraction Patterns

- **Symbols**: Uppercase letters (SPY, AAPL, TSLA)
- **Strikes**: Numbers with optional $ and decimals (730, $730.50)
- **Prices**: Usually after "at", "for", or "price"
- **Dates**: Flexible - "2027-01-17", "Jan 17 2027", "next Friday"
- **IDs**: Numbers after "#", "call", "position", or "leaps"
- **Quantities**: Numbers followed by "contracts" or "x"

## Conversation State

- **Timeout**: 5 minutes of inactivity
- **Storage**: In-memory (per-instance)
- **Per-user**: Each user has independent conversation state
- **Automatic cleanup**: Cleared after successful execution or timeout

## Testing

Run the conversational tests:
```bash
pytest tests/test_conversational.py -v
```

Run all tests:
```bash
pytest -v
```

## Implementation Details

### Message Handler Priority
1. Command handlers process first (slash commands)
2. MessageHandler processes non-command text
3. Ensures backward compatibility

### Parameter Mapping
The bot intelligently maps generic entities to specific parameters:
- `id` → `short_call_id` for close/roll intents
- `id` → `leaps_id` for newcall/add_short intents
- `price` → `exit_price` for close intent

### Error Handling
- Invalid commands show helpful message
- Missing parameters trigger prompts
- Failed extractions continue conversation
- Timeout shows fresh start message

## Configuration

No configuration needed - works out of the box. The conversational interface is always enabled alongside slash commands.

## Deployment

The conversational interface is automatically active when the bot runs. No special deployment steps required beyond normal bot deployment.

## Future Enhancements

Potential improvements (not currently implemented):
- Support for multiple positions in one command
- Undo last action
- Voice command transcription
- Learning from user patterns
- Custom intent definitions

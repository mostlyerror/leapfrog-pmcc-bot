# PMCC Bot

A Telegram bot for managing Poor Man's Covered Call (PMCC) options positions with automated monitoring and alerts.

## What It Does

- Track LEAPS and short call positions
- Monitor positions automatically during market hours
- Get alerts when profit targets are hit
- Adjust LEAPS cost basis as you collect premium
- Scan for roll and new call opportunities
- Daily portfolio summaries

## Quick Start

```bash
# Clone and install
git clone https://github.com/mostlyerror/leapfrog-pmcc-bot.git
cd leapfrog-pmcc-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python main.py
```

## Telegram Commands

```
/positions - Show positions
/summary - Cost basis summary
/add_leaps <symbol> <strike> <exp> <price> <qty>
/add_short <leaps_id> <symbol> <strike> <exp> <price> <qty>
/close <short_call_id> <exit_price>
/roll <short_call_id>
/newcall <leaps_id>
```

## Deploy to Railway

```bash
railway login
railway up
```

See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for full deployment guide.

## Configuration

Required environment variables:
- `TRADIER_API_KEY` - Get from [Tradier Developer](https://developer.tradier.com/)
- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather)
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID

## Testing

```bash
pytest                    # Run all tests
pytest --cov             # With coverage
```

See [TESTING.md](TESTING.md) for details.

## Documentation

- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Complete deployment guide
- [TESTING.md](TESTING.md) - Test suite documentation
- [tests/README.md](tests/README.md) - Detailed test guide

## Tech Stack

- Python 3.10+
- SQLite (local) / PostgreSQL (production)
- Tradier API for market data
- Telegram Bot API
- pytest for testing

## License

MIT

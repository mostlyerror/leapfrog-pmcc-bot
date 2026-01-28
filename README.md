# PMCC Bot - Poor Man's Covered Call Management

A Python bot for monitoring and managing PMCC (Poor Man's Covered Call) positions using the Tradier API and Telegram for alerts.

## Features

- 📊 **Position Tracking**: Track LEAPS and short call positions with cost basis adjustments
- 🔔 **Smart Alerts**: Get notified at 50% and 80% profit targets, strike proximity warnings, and expiration alerts
- 🔍 **Roll Scanner**: Find optimal roll candidates with credit analysis and delta filtering
- 📈 **New Call Scanner**: Discover profitable short call opportunities with annualized return calculations
- 💰 **Cost Basis Tracking**: Automatically adjust LEAPS cost basis as premium is collected
- 📱 **Telegram Integration**: All alerts and commands via Telegram bot
- ⏰ **Automated Monitoring**: Polls market data every 5 minutes during market hours
- 📊 **Daily Summary**: Get end-of-day position summaries with P&L and recommendations

## Technical Stack

- Python 3.11+
- SQLite for data persistence
- Tradier API for market data and options chains
- Telegram Bot API for alerts and commands
- Schedule library for background monitoring

## Project Structure

```
pmcc-bot/
├── config.py           # Configuration management
├── models.py           # Database models and operations
├── tradier.py          # Tradier API wrapper
├── alerts.py           # Alert monitoring logic
├── scanner.py          # Roll and new call scanning
├── bot.py              # Telegram bot handlers
├── main.py             # Entry point and scheduler
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (create from .env.example)
├── schema.sql          # Database schema reference
└── pmcc.db            # SQLite database (auto-created)
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11 or higher
- Tradier API account (sandbox or production)
- Telegram bot token and chat ID

### 2. Get API Credentials

#### Tradier API:
1. Sign up at [Tradier Developer](https://developer.tradier.com/)
2. Create a sandbox account for testing
3. Generate an API token from the dashboard

#### Telegram Bot:
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow prompts to create your bot
3. Save the bot token provided
4. To get your chat ID:
   - Message your bot anything
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your `chat_id` in the response

### 3. Installation

```bash
# Clone or download the project
cd pmcc-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 4. Configuration

Edit `.env` with your credentials:

```bash
# Required
TRADIER_API_KEY=your_tradier_api_key
TRADIER_BASE_URL=https://sandbox.tradier.com/v1
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Optional (defaults shown)
POLL_INTERVAL_MINUTES=5
PROFIT_THRESHOLD_LOW=0.50
PROFIT_THRESHOLD_HIGH=0.80
STRIKE_PROXIMITY_PCT=0.03
TARGET_DELTA_MIN=0.20
TARGET_DELTA_MAX=0.30
TARGET_DTE_MIN=30
TARGET_DTE_MAX=45
```

### 5. Run the Bot

```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python main.py
```

The bot will:
- Initialize the database (auto-seeds with example SPY positions on first run)
- Start the Telegram bot
- Begin monitoring positions every 5 minutes during market hours (9:30 AM - 4:00 PM ET)
- Send daily summaries at 4:30 PM ET

## Telegram Commands

### Position Management
- `/positions` - Show all current LEAPS and short call positions with P&L
- `/add_leaps <symbol> <strike> <exp> <price> <qty>` - Add a new LEAPS position
  - Example: `/add_leaps SPY 620 2027-01-17 109.00 2`
- `/add_short <leaps_id> <symbol> <strike> <exp> <price> <qty>` - Add short call
  - Example: `/add_short 1 SPY 730 2026-03-21 6.50 2`

### Monitoring & Analysis
- `/alerts` - Show current alert thresholds and monitoring status
- `/summary` - Get cost basis summary with premium collected
- `/roll <short_call_id>` - Get top 3 roll candidates for a position
  - Example: `/roll 1`
- `/newcall <leaps_id>` - Get top 5 new short call candidates
  - Example: `/newcall 1`

### Trading
- `/close <short_call_id> <exit_price>` - Log a closed short call and update cost basis
  - Example: `/close 1 3.25`

### Help
- `/help` - Show all available commands
- `/start` - Welcome message

## Alert Types

The bot monitors positions and sends these alerts:

| Alert | Trigger | Icon |
|-------|---------|------|
| Close Candidate | 50% profit reached | 🎯 |
| Strong Close Signal | 80% profit reached | 💰 |
| Strike Threatened | Underlying within 3% of strike | ⚠️ |
| Expiration Approaching | ≤7 DTE with <50% profit | ⏰ |

## Deployment Options

### Option 1: Local (Development/Testing)

Run directly on your machine:

```bash
python main.py
```

Keep the terminal open. Use `tmux` or `screen` for persistent sessions.

### Option 2: Systemd Service (Linux VPS)

Create `/etc/systemd/system/pmcc-bot.service`:

```ini
[Unit]
Description=PMCC Trading Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/pmcc-bot
Environment="PATH=/path/to/pmcc-bot/venv/bin"
ExecStart=/path/to/pmcc-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable pmcc-bot
sudo systemctl start pmcc-bot
sudo systemctl status pmcc-bot

# View logs
sudo journalctl -u pmcc-bot -f
```

### Option 3: Railway (Recommended for Cloud)

Railway provides free hosting with automatic restarts and logging.

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Initialize Project**:
   ```bash
   cd pmcc-bot
   railway init
   ```

3. **Add Environment Variables**:
   ```bash
   railway variables set TRADIER_API_KEY="your_key"
   railway variables set TRADIER_BASE_URL="https://sandbox.tradier.com/v1"
   railway variables set TELEGRAM_BOT_TOKEN="your_token"
   railway variables set TELEGRAM_CHAT_ID="your_chat_id"
   ```

4. **Create Procfile** (already included if you add it):
   ```
   web: python main.py
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

6. **Monitor**:
   - Visit [railway.app](https://railway.app) dashboard
   - View logs, metrics, and manage variables
   - Database persists in the deployment volume

### Option 4: Render

Similar to Railway, Render offers free tier with persistent storage.

1. Create account at [render.com](https://render.com)
2. Create new "Background Worker"
3. Connect your GitHub repo or upload code
4. Set environment variables in dashboard
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `python main.py`

### Option 5: Cron (Scheduled Execution)

If you prefer periodic execution without continuous running:

Edit crontab:
```bash
crontab -e
```

Add (runs every 5 minutes during market hours):
```bash
*/5 9-16 * * 1-5 cd /path/to/pmcc-bot && /path/to/pmcc-bot/venv/bin/python -c "from main import PMCCScheduler; PMCCScheduler().check_positions()"
```

**Note**: Cron approach requires modifying the bot to work without the continuous Telegram polling. The systemd or cloud options are recommended.

## Example Workflow

1. **Add your LEAPS position**:
   ```
   /add_leaps SPY 600 2027-01-15 115.50 1
   ```

2. **Find a short call to sell**:
   ```
   /newcall 1
   ```

3. **Add the short call position** (after executing in Robinhood):
   ```
   /add_short 1 SPY 710 2026-02-20 8.25 1
   ```

4. **Monitor automatically** - Bot alerts you at profit targets

5. **Check roll options** when alerted:
   ```
   /roll 1
   ```

6. **Close position** after buying to close in Robinhood:
   ```
   /close 1 4.10
   ```

7. **Check updated cost basis**:
   ```
   /summary
   ```

## Database Schema

The bot uses SQLite with four main tables:

- **leaps**: LEAPS positions with entry prices and quantities
- **short_calls**: Short call positions linked to LEAPS parents
- **alerts**: Historical alert triggers and acknowledgments
- **cost_basis_history**: Audit trail of cost basis adjustments

See `schema.sql` for full schema definition.

## Development

### Running Tests

```bash
pytest tests/
```

### Logs

Logs are written to stdout/stderr. Configure log level in `.env`:

```bash
LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR
```

### Extending

The modular structure makes it easy to extend:

- Add new alert types in `alerts.py`
- Add scanner strategies in `scanner.py`
- Add Telegram commands in `bot.py`
- Adjust thresholds in `config.py`

## Troubleshooting

### Bot not receiving messages
- Verify `TELEGRAM_CHAT_ID` is correct (number, not username)
- Message your bot first to establish chat
- Check bot token is valid

### No market data
- Confirm Tradier API key is valid
- Check if using sandbox vs production URL correctly
- Verify API rate limits (sandbox: 120 req/min)

### Database locked errors
- Only run one instance of the bot
- Check file permissions on `pmcc.db`

### Positions not monitoring
- Ensure current time is within market hours (9:30 AM - 4:00 PM ET, Mon-Fri)
- Check logs for API errors
- Verify option symbols are formatted correctly

## Security Notes

- Never commit `.env` file to version control
- Keep your Tradier API key and Telegram token private
- Use sandbox API for testing before production
- Database contains your trading history - secure the file

## Limitations

- **Monitoring only**: Bot does NOT execute trades, only provides alerts
- **Manual entry**: You must manually log positions after executing in Robinhood
- **Single underlying**: Designed for SPY but works with any optionable symbol
- **US market hours**: Monitors 9:30 AM - 4:00 PM ET, Monday-Friday
- **Tradier data**: Quote accuracy depends on Tradier API (sandbox has delayed data)

## Production Checklist

Before running with real money:

- [ ] Switch from sandbox to production Tradier API URL
- [ ] Test all Telegram commands with real positions
- [ ] Verify alert thresholds match your strategy
- [ ] Set up proper deployment with automatic restarts
- [ ] Configure proper logging and monitoring
- [ ] Backup database regularly
- [ ] Document your cost basis tracking for taxes

## Support

For issues, questions, or contributions:
- Review logs first (`LOG_LEVEL=DEBUG`)
- Check Tradier API status page
- Verify Telegram bot permissions
- Test with sandbox data before reporting issues

## License

MIT License - feel free to modify and use for your own trading.

## Disclaimer

This bot is for informational and monitoring purposes only. It does not provide investment advice. Options trading carries significant risk. Past performance does not guarantee future results. Use at your own risk.

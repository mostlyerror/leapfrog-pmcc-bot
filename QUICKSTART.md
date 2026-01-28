# Quick Start Guide

Get your PMCC Bot running in 5 minutes.

## Step 1: Install Dependencies

```bash
cd pmcc-bot
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Get API Credentials

### Tradier API (2 minutes)
1. Go to [https://developer.tradier.com/](https://developer.tradier.com/)
2. Click "Sign Up" → Create account
3. Dashboard → "Sandbox Account" → "Create Access Token"
4. Copy the token

### Telegram Bot (2 minutes)
1. Open Telegram, search for `@BotFather`
2. Send: `/newbot`
3. Follow prompts, save the token
4. Message your new bot anything (e.g., "hello")
5. Visit in browser: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
6. Find `"chat":{"id":123456789}` and copy that number

## Step 3: Configure

```bash
cp .env.example .env
nano .env  # or use any text editor
```

Fill in these 4 required values:
```bash
TRADIER_API_KEY=your_tradier_token_here
TRADIER_BASE_URL=https://sandbox.tradier.com/v1
TELEGRAM_BOT_TOKEN=your_telegram_token_here
TELEGRAM_CHAT_ID=your_chat_id_number_here
```

## Step 4: Test Connection

```bash
python test_connection.py
```

You should see:
- ✅ Tradier API connection successful
- ✅ Telegram Bot connection successful
- ✅ Test message in your Telegram

## Step 5: Run the Bot

```bash
python main.py
```

You should see:
```
INFO - Configuration validated
INFO - Database initialized
INFO - Example data seeded successfully
INFO - Tradier API client initialized
INFO - Telegram bot initialized
INFO - Starting PMCC Bot
```

## Step 6: Try Commands

Open Telegram and message your bot:

```
/start
/help
/positions
```

You should see your example SPY positions!

## Next Steps

- Add your real positions: `/add_leaps` and `/add_short`
- Try scanning: `/newcall 1` or `/roll 1`
- Check alerts: `/alerts`
- Get summary: `/summary`

## Troubleshooting

**"Configuration error"**
- Check your `.env` file has all 4 required values
- Make sure no spaces around the `=` signs
- Tokens should be in quotes if they contain special characters

**"Tradier API error"**
- Verify your API token is correct
- Check if you're using the right URL (sandbox vs production)
- Sandbox tokens only work with sandbox URL

**"Telegram Bot error"**
- Make sure you messaged your bot first before getting chat ID
- Check bot token is correct (starts with a number, contains `:`)
- Chat ID should be a number, not a username

**"No module named 'X'"**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Re-run: `pip install -r requirements.txt`

## Deploy to Cloud

Once working locally, deploy to Railway for free:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Add environment variables via dashboard
railway open
```

Then go to Variables and add your 4 API credentials.

---

**Still stuck?** Check the full [README.md](README.md) for detailed instructions.

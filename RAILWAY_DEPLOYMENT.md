# Railway Deployment Guide

## Overview
PMCC Bot now supports both SQLite (local development) and PostgreSQL (Railway production) databases with automatic detection.

## What Changed

### 1. Database Layer (`models.py`)
- ✅ Added PostgreSQL support with `psycopg2-binary`
- ✅ Auto-detects database type (Path = SQLite, string = PostgreSQL)
- ✅ Compatible SQL schema for both databases
- ✅ Dict-like row access works for both (sqlite3.Row and RealDictCursor)

### 2. Configuration (`config.py`)
- ✅ Added `DATABASE_URL` environment variable support
- ✅ Auto-detects mode: PostgreSQL if `DATABASE_URL` set, otherwise SQLite
- ✅ Logs which database type is being used

### 3. Dependencies (`requirements.txt`)
- ✅ Added `psycopg2-binary==2.9.9` for PostgreSQL support

### 4. Main Entry Point (`main.py`)
- ✅ Database initialization now uses either `DATABASE_URL` or `DB_PATH`
- ✅ Added database connection health check on startup

### 5. Railway Configuration (`railway.json`)
- ✅ Created Railway deployment config with auto-restart on failure

## Local Testing

### SQLite Mode (Default)
```bash
# Ensure DATABASE_URL is not set
unset DATABASE_URL

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run locally
python main.py
```

**Expected logs:**
```
INFO - Using SQLite database at /path/to/pmcc-bot/pmcc.db
INFO - Configuration validated
INFO - SQLite database initialized at /path/to/pmcc-bot/pmcc.db
INFO - Database initialized
INFO - Database connection verified
INFO - Starting PMCC Bot
```

### PostgreSQL Mode (Local Testing - Optional)
If you have PostgreSQL running locally:

```bash
# Set DATABASE_URL to local PostgreSQL
export DATABASE_URL="postgresql://username:password@localhost/pmcc_test"

# Run
python main.py
```

**Expected logs:**
```
INFO - Using PostgreSQL database
INFO - Configuration validated
INFO - PostgreSQL database initialized
INFO - Database initialized
INFO - Database connection verified
INFO - Starting PMCC Bot
```

## Railway Deployment Steps

### 1. Install Railway CLI (if not already installed)
```bash
npm install -g @railway/cli
# or
brew install railway
```

### 2. Login to Railway
```bash
railway login
```

### 3. Initialize Railway Project
```bash
cd /Users/benjaminpoon/dev/pmcc-bot
railway init
```
- Select: **Create new project**
- Name: **pmcc-bot**

### 4. Add PostgreSQL Database
```bash
railway add
```
- Select: **PostgreSQL**
- This automatically creates and sets the `DATABASE_URL` environment variable

### 5. Set Environment Variables
```bash
railway variables set TRADIER_API_KEY="your_actual_tradier_api_key"
railway variables set TRADIER_BASE_URL="https://sandbox.tradier.com/v1"
railway variables set TELEGRAM_BOT_TOKEN="your_actual_bot_token"
railway variables set TELEGRAM_CHAT_ID="your_actual_chat_id"
railway variables set LOG_LEVEL="INFO"
```

**Important:** Replace the placeholder values with your actual credentials.

### 6. Verify Environment Variables
```bash
railway variables
```

Expected output should show:
- `DATABASE_URL` (auto-set by PostgreSQL plugin)
- `TRADIER_API_KEY`
- `TRADIER_BASE_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `LOG_LEVEL`

### 7. Deploy to Railway
```bash
railway up
```

This will:
- Build your application using Nixpacks
- Install dependencies from `requirements.txt`
- Run database migrations automatically
- Start the bot with `python main.py`

### 8. Monitor Deployment Logs
```bash
railway logs --follow
```

**Look for these success indicators:**
```
✅ "Using PostgreSQL database"
✅ "Configuration validated"
✅ "PostgreSQL database initialized"
✅ "Database initialized"
✅ "Database connection verified"
✅ "Starting PMCC Bot"
✅ "Scheduler thread started"
```

### 9. Verify Database Tables Created
```bash
railway connect PostgreSQL
```

In the PostgreSQL shell:
```sql
\dt
```

You should see:
- `leaps`
- `short_calls`
- `alerts`
- `cost_basis_history`

Exit with:
```sql
\q
```

### 10. Test Telegram Bot
Send test commands to your Telegram bot:
- `/start` - Should receive welcome message
- `/help` - Should receive help text
- `/positions` - Should show empty positions (initially)
- `/summary` - Should show portfolio summary

## Verifying Persistence

### Test 1: Data Persistence After Restart
1. Create a test position via Telegram (if you have commands for this)
2. Restart the Railway service:
   ```bash
   railway restart
   ```
3. Send `/positions` - Your data should still be there

### Test 2: Database Inspection
```bash
# Connect to database
railway connect PostgreSQL

# Check data
SELECT * FROM leaps;
SELECT * FROM short_calls;
```

## Troubleshooting

### Issue: "DATABASE_URL is not set"
**Solution:** Make sure PostgreSQL plugin is added:
```bash
railway add
# Select: PostgreSQL
```

### Issue: "psycopg2 module not found"
**Solution:** Railway should auto-install from `requirements.txt`. Check build logs:
```bash
railway logs --build
```

### Issue: "Database connection failed"
**Solutions:**
1. Check DATABASE_URL is set correctly:
   ```bash
   railway variables get DATABASE_URL
   ```
2. Verify PostgreSQL service is running:
   ```bash
   railway status
   ```

### Issue: Bot not responding to Telegram commands
**Solutions:**
1. Verify environment variables are set:
   ```bash
   railway variables
   ```
2. Check bot logs for errors:
   ```bash
   railway logs --follow
   ```
3. Verify Telegram bot token is valid

### Issue: "Configuration errors: ..."
**Solution:** Set all required environment variables:
```bash
railway variables set TRADIER_API_KEY="..."
railway variables set TELEGRAM_BOT_TOKEN="..."
railway variables set TELEGRAM_CHAT_ID="..."
```

## Rolling Back

### Option 1: Rollback via Railway CLI
```bash
# List deployments
railway deployments list

# Rollback to specific deployment
railway rollback <deployment-id>
```

### Option 2: Git Revert
```bash
git revert HEAD
git push
railway up
```

### Option 3: Emergency SQLite Mode
⚠️ **WARNING:** Data won't persist with SQLite on Railway (ephemeral filesystem)

```bash
# Remove DATABASE_URL
railway variables delete DATABASE_URL

# Redeploy
railway up
```

## Production Checklist

Before going to production:

- [ ] Switch `TRADIER_BASE_URL` to production API:
  ```bash
  railway variables set TRADIER_BASE_URL="https://api.tradier.com/v1"
  ```
- [ ] Use production Tradier API key
- [ ] Verify PostgreSQL database backups are enabled in Railway
- [ ] Set up monitoring/alerting for the Railway service
- [ ] Test all critical bot commands
- [ ] Verify scheduled jobs execute correctly
- [ ] Document your deployment date and version

## Important Notes

1. **Example Data Seeding:** The `seed_example_data()` function in `main.py` (lines 106-139) will add example positions on first run. Consider disabling this for production:
   ```python
   # Comment out in main.py line 166:
   # seed_example_data(db)
   ```

2. **Database Migrations:** Currently, schema changes require manual migration. For future schema updates, consider using a migration tool like Alembic.

3. **Backups:** Railway provides automatic daily backups for PostgreSQL. Verify backup settings in Railway dashboard.

4. **Cost:** Monitor Railway usage. Free tier has limits. PostgreSQL plugin may require paid plan.

5. **Environment Isolation:** Local development uses SQLite, production uses PostgreSQL. They are completely separate databases.

## Quick Reference Commands

```bash
# Deploy
railway up

# View logs
railway logs --follow

# View variables
railway variables

# Set variable
railway variables set KEY="value"

# Restart service
railway restart

# Connect to database
railway connect PostgreSQL

# Check status
railway status

# List deployments
railway deployments list
```

## Success Indicators

After deployment, you should see:

✅ Railway service status: **Active**
✅ PostgreSQL service status: **Active**
✅ Bot logs show: "Using PostgreSQL database"
✅ Bot logs show: "Database connection verified"
✅ Bot logs show: "Starting PMCC Bot"
✅ Telegram bot responds to commands
✅ Database tables exist (check with `\dt`)
✅ Data persists after Railway restart

## Next Steps

1. Monitor the bot for 24-48 hours to ensure stability
2. Test all critical features (position management, alerts, scheduled jobs)
3. Verify scheduled jobs execute at correct times
4. Set up external monitoring (e.g., UptimeRobot) to ping bot health endpoint
5. Document any production-specific configurations or gotchas

---

**Deployment Date:** _TBD_
**Deployed By:** _Your Name_
**Railway Project:** pmcc-bot
**Database:** PostgreSQL (Railway-managed)

## Auto-Deployment Status

✅ Connected to GitHub repository
✅ Auto-deployments enabled
✅ Deploys automatically on push to main branch

Railway will now automatically deploy whenever you push changes to the main branch.


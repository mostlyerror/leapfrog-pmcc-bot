# PMCC Bot - Project Structure

## Overview

This document describes the complete project structure and file organization.

## Directory Tree

```
pmcc-bot/
├── Core Application Files
│   ├── main.py              # Entry point & scheduler
│   ├── config.py            # Configuration management
│   ├── models.py            # Database models (SQLite)
│   ├── tradier.py           # Tradier API wrapper
│   ├── alerts.py            # Alert monitoring logic
│   ├── scanner.py           # Roll & new call scanning
│   └── bot.py               # Telegram bot handlers
│
├── Configuration
│   ├── .env.example         # Environment variables template
│   ├── .env                 # Your credentials (git-ignored)
│   └── .gitignore          # Git ignore rules
│
├── Documentation
│   ├── README.md            # Main documentation
│   ├── QUICKSTART.md        # 5-minute setup guide
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── PROJECT_STRUCTURE.md # This file
│
├── Database
│   ├── schema.sql           # Database schema reference
│   └── pmcc.db             # SQLite database (auto-created)
│
├── Testing & Utilities
│   ├── test_connection.py   # Connection test script
│   └── setup.sh            # Automated setup script
│
├── Deployment Files
│   ├── requirements.txt     # Python dependencies
│   ├── Procfile            # Railway/Heroku process
│   ├── runtime.txt         # Python version spec
│   ├── Dockerfile          # Docker image definition
│   ├── docker-compose.yml  # Docker Compose config
│   └── pmcc-bot.service    # Systemd service template
│
└── Runtime (auto-created)
    ├── venv/               # Python virtual environment
    ├── data/               # Docker volume mount
    └── __pycache__/        # Python bytecode cache
```

## File Descriptions

### Core Application Files

#### `main.py`
- Entry point for the application
- Initializes all components (DB, API, Bot)
- Sets up scheduler for automated monitoring
- Seeds example data on first run
- Manages background monitoring thread

**Key Functions**:
- `main()`: Application entry point
- `PMCCScheduler`: Handles scheduled tasks
- `seed_example_data()`: Creates example positions

#### `config.py`
- Central configuration management
- Loads environment variables from `.env`
- Provides defaults for all settings
- Validates required configuration

**Configuration Sections**:
- API credentials (Tradier, Telegram)
- Market hours (Eastern Time)
- Alert thresholds (50%, 80%, etc.)
- Scanner parameters (delta, DTE)
- Logging settings

#### `models.py`
- Database abstraction layer
- SQLite connection management
- Data models for all entities

**Models**:
- `Database`: Connection and schema initialization
- `LeapsPosition`: LEAPS position CRUD operations
- `ShortCall`: Short call position management
- `Alert`: Alert tracking and acknowledgment

**Key Features**:
- Automatic schema creation
- Cost basis calculation
- Position history tracking

#### `tradier.py`
- Tradier API client wrapper
- Market data fetching
- Options chain queries

**Methods**:
- `get_quote()`: Real-time stock/option quotes
- `get_options_chain()`: Full options chain with Greeks
- `get_options_expirations()`: Available expiration dates
- `find_options_by_criteria()`: Filtered option search
- `calculate_annualized_return()`: Return calculations

**Features**:
- Automatic error handling
- Request retry logic
- OCC symbol formatting

#### `alerts.py`
- Position monitoring engine
- Alert triggering logic
- Status tracking

**Alert Types**:
- 50% profit target (close candidate)
- 80% profit target (strong close)
- Strike proximity warning (3%)
- Expiration approaching (≤7 DTE)

**Methods**:
- `check_all_positions()`: Monitors all active positions
- `get_position_status()`: Detailed position info
- `_create_alert()`: Alert creation with deduplication

#### `scanner.py`
- Roll candidate scanner
- New short call scanner
- Options ranking logic

**Scanners**:
- `find_roll_candidates()`: Find roll opportunities
  - Multiple DTE targets (30, 45, 60)
  - Strike offsets ($5, $10, $15, $20)
  - Credit/debit analysis

- `find_new_call_candidates()`: New calls to sell
  - Target delta range (0.20-0.30)
  - Target DTE range (30-45)
  - Annualized return calculations

**Output**:
- Formatted results for Telegram
- Top N candidates ranked by criteria

#### `bot.py`
- Telegram bot interface
- Command handlers
- Message formatting

**Commands Implemented**:
- `/start`, `/help`: Help and documentation
- `/positions`: Show all positions with P/L
- `/alerts`: Show alert configuration
- `/summary`: Daily cost basis summary
- `/roll <id>`: Get roll candidates
- `/newcall <id>`: Get new call candidates
- `/close <id> <price>`: Close position
- `/add_leaps`: Add LEAPS position
- `/add_short`: Add short call

**Features**:
- Markdown formatting for readability
- Real-time position status
- Error handling and validation

### Configuration Files

#### `.env.example`
Template for environment variables with documentation.

**Required Variables**:
- `TRADIER_API_KEY`: Tradier API token
- `TRADIER_BASE_URL`: API endpoint (sandbox/prod)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID

**Optional Variables**:
- Monitoring intervals
- Alert thresholds
- Scanner parameters
- Logging level

#### `.env`
Your actual credentials (not included in git).

#### `.gitignore`
Prevents sensitive files from being committed:
- `.env` (credentials)
- `*.db` (database)
- `venv/` (virtual environment)
- `__pycache__/` (Python cache)

### Documentation

#### `README.md`
Comprehensive documentation covering:
- Feature overview
- Setup instructions
- All Telegram commands
- Deployment options
- Troubleshooting guide
- Production checklist

#### `QUICKSTART.md`
Get started in 5 minutes:
- Streamlined setup steps
- API credential acquisition
- Connection testing
- First commands

#### `DEPLOYMENT.md`
Detailed deployment guides for:
- Railway (recommended)
- Render
- Linux VPS (systemd)
- Docker/Docker Compose
- Local development

Includes:
- Step-by-step instructions
- Troubleshooting
- Cost comparison
- Security best practices

#### `PROJECT_STRUCTURE.md`
This file - explains all files and their purposes.

### Database

#### `schema.sql`
SQL schema reference showing:
- Table definitions
- Column types and constraints
- Foreign key relationships
- Indexes for performance

**Tables**:
- `leaps`: LEAPS positions
- `short_calls`: Short call positions
- `alerts`: Alert history
- `cost_basis_history`: Basis adjustments

#### `pmcc.db`
SQLite database (auto-created on first run):
- Stores all position data
- Alert history
- Cost basis tracking
- Automatically seeded with example data

### Testing & Utilities

#### `test_connection.py`
Connection verification script:
- Tests Tradier API connection
- Tests Telegram Bot connection
- Sends test message
- Validates configuration

Run before first use to verify setup.

#### `setup.sh`
Automated setup script:
- Creates virtual environment
- Installs dependencies
- Creates `.env` from template
- Creates data directory
- Provides next steps

Makes setup faster and less error-prone.

### Deployment Files

#### `requirements.txt`
Python package dependencies:
- `python-dotenv`: Environment variables
- `requests`: HTTP client
- `python-telegram-bot`: Telegram API
- `schedule`: Task scheduling
- `pytz`: Timezone handling
- `pytest`: Testing (dev)

#### `Procfile`
Process definition for Railway/Heroku:
```
worker: python main.py
```

Tells platform how to run the bot.

#### `runtime.txt`
Specifies Python version:
```
python-3.11.7
```

Ensures consistent Python version in cloud.

#### `Dockerfile`
Docker image definition:
- Based on Python 3.11 slim
- Installs dependencies
- Sets up volume for database
- Runs bot as CMD

#### `docker-compose.yml`
Docker Compose configuration:
- Builds from Dockerfile
- Mounts data volume
- Loads `.env` file
- Configures logging
- Automatic restart policy

#### `pmcc-bot.service`
Systemd service template for Linux:
- Service definition
- Auto-restart on failure
- Log rotation
- Security hardening options

Replace placeholders with your paths.

## Data Flow

```
┌─────────────────┐
│   Tradier API   │
│  (Market Data)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│          Main Process               │
│  ┌──────────────────────────────┐   │
│  │  Scheduler (every 5 min)     │   │
│  └──────────┬───────────────────┘   │
│             │                        │
│             ▼                        │
│  ┌──────────────────────────────┐   │
│  │    Alert Monitor             │   │
│  │  - Fetch current prices      │   │
│  │  - Check thresholds          │   │
│  │  - Trigger alerts            │   │
│  └──────────┬───────────────────┘   │
└─────────────┼───────────────────────┘
              │
              ▼
   ┌──────────────────┐
   │  SQLite Database │
   │  - Positions     │
   │  - Alerts        │
   │  - History       │
   └──────────┬───────┘
              │
              ▼
   ┌──────────────────┐
   │  Telegram Bot    │
   │  - Send alerts   │
   │  - Handle cmds   │
   └──────────────────┘
              │
              ▼
         Your Phone
```

## Extension Points

Want to customize? Here's where to add features:

### New Alert Types
- Edit `alerts.py`
- Add new condition in `_check_position()`
- Add alert type to `_create_alert()`

### New Telegram Commands
- Edit `bot.py`
- Add new handler method: `async def cmd_name()`
- Register in `_register_handlers()`

### New Scanner Strategies
- Edit `scanner.py`
- Create new scanner method
- Add formatting method
- Wire up to Telegram command

### Different Options Strategies
- Models in `models.py` are generic
- Adapt alert logic in `alerts.py`
- Customize scanners in `scanner.py`

### Additional Data Sources
- Create new API wrapper (like `tradier.py`)
- Integrate in `main.py`
- Use in scanners/alerts as needed

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.11+ | Core application |
| Database | SQLite | Position tracking |
| Market Data | Tradier API | Options chains, quotes |
| Alerts | Telegram Bot API | Notifications |
| Scheduling | `schedule` library | Background monitoring |
| Deployment | Railway/Render/Docker | Cloud hosting |
| Process Manager | systemd | Linux service |

## Development Workflow

1. **Setup**:
   ```bash
   ./setup.sh
   ```

2. **Configure**:
   ```bash
   nano .env
   ```

3. **Test**:
   ```bash
   python test_connection.py
   ```

4. **Run Locally**:
   ```bash
   python main.py
   ```

5. **Make Changes**:
   - Edit source files
   - Test locally
   - Commit to git

6. **Deploy**:
   ```bash
   railway up  # or docker-compose up -d
   ```

## Monitoring in Production

- **Railway**: Built-in logs and metrics
- **Render**: Dashboard with logs
- **VPS**: `journalctl -u pmcc-bot -f`
- **Docker**: `docker-compose logs -f`

## Backup Strategy

**Database**:
- Daily automated backups
- Keep 30 days history
- Export cost basis for taxes

**Code**:
- Version control with git
- Keep `.env` backed up separately (securely)

## Performance

- **CPU**: Minimal (polling every 5 min)
- **Memory**: ~50-100 MB
- **Network**: Low (API calls only during market hours)
- **Disk**: <10 MB (database grows slowly)

Suitable for:
- Free tier cloud platforms
- Raspberry Pi
- Minimal VPS

## Security Considerations

1. **API Keys**: Never commit to git
2. **Database**: Contains trading history, secure appropriately
3. **Telegram**: Bot token grants full bot access
4. **Backups**: Encrypt if contains sensitive data

## Future Enhancements

Possible additions (not yet implemented):

- [ ] Web dashboard for positions
- [ ] Email alerts (in addition to Telegram)
- [ ] Multiple underlying support
- [ ] Greeks tracking and alerts
- [ ] Backtesting framework
- [ ] Tax reporting export
- [ ] Position risk analysis
- [ ] Integration with other brokers

## Getting Help

1. Check relevant doc:
   - Setup issues → `QUICKSTART.md`
   - Deployment issues → `DEPLOYMENT.md`
   - Feature questions → `README.md`

2. Review logs:
   ```bash
   # Set DEBUG level
   LOG_LEVEL=DEBUG python main.py
   ```

3. Test components:
   ```bash
   python test_connection.py
   ```

4. Check configuration:
   ```bash
   cat .env  # Verify all required vars set
   ```

## License

MIT License - modify and use freely.

## Contributing

To add features:
1. Fork/clone the repo
2. Make changes in feature branch
3. Test thoroughly
4. Document changes
5. Submit pull request

---

For questions, see the main [README.md](README.md) file.

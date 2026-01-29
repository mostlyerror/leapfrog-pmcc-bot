"""
Configuration management for PMCC Bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Base directories
BASE_DIR = Path(__file__).parent

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL:
    # Production: PostgreSQL from Railway
    DB_TYPE = "postgresql"
    DB_PATH = None
else:
    # Development: SQLite
    DB_TYPE = "sqlite"
    DB_PATH = BASE_DIR / "pmcc.db"

# API Configuration
TRADIER_API_KEY = os.getenv("TRADIER_API_KEY", "")
TRADIER_BASE_URL = os.getenv(
    "TRADIER_BASE_URL",
    "https://sandbox.tradier.com/v1"  # Change to https://api.tradier.com/v1 for production
)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Monitoring Configuration
POLL_INTERVAL_MINUTES = int(os.getenv("POLL_INTERVAL_MINUTES", "5"))
MARKET_OPEN_HOUR = int(os.getenv("MARKET_OPEN_HOUR", "9"))  # ET
MARKET_OPEN_MINUTE = int(os.getenv("MARKET_OPEN_MINUTE", "30"))
MARKET_CLOSE_HOUR = int(os.getenv("MARKET_CLOSE_HOUR", "16"))  # ET
MARKET_CLOSE_MINUTE = int(os.getenv("MARKET_CLOSE_MINUTE", "0"))
DAILY_SUMMARY_HOUR = int(os.getenv("DAILY_SUMMARY_HOUR", "16"))  # ET
DAILY_SUMMARY_MINUTE = int(os.getenv("DAILY_SUMMARY_MINUTE", "30"))

# Alert Thresholds
PROFIT_THRESHOLD_LOW = float(os.getenv("PROFIT_THRESHOLD_LOW", "0.50"))  # 50%
PROFIT_THRESHOLD_HIGH = float(os.getenv("PROFIT_THRESHOLD_HIGH", "0.80"))  # 80%
STRIKE_PROXIMITY_PCT = float(os.getenv("STRIKE_PROXIMITY_PCT", "0.03"))  # 3%
LOW_PROFIT_DTE_THRESHOLD = int(os.getenv("LOW_PROFIT_DTE_THRESHOLD", "7"))

# Scanner Configuration
TARGET_DELTA_MIN = float(os.getenv("TARGET_DELTA_MIN", "0.20"))
TARGET_DELTA_MAX = float(os.getenv("TARGET_DELTA_MAX", "0.30"))
TARGET_DTE_MIN = int(os.getenv("TARGET_DTE_MIN", "30"))
TARGET_DTE_MAX = int(os.getenv("TARGET_DTE_MAX", "45"))

# Roll Scanner Configuration
ROLL_DTE_OPTIONS = [30, 45, 60]
ROLL_STRIKE_OFFSETS = [5, 10, 15, 20]  # Dollars above current short strike
ROLL_MAX_DELTA = float(os.getenv("ROLL_MAX_DELTA", "0.30"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def validate_config():
    """Validate required configuration"""
    errors = []

    if not TRADIER_API_KEY:
        errors.append("TRADIER_API_KEY is required")
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is required")
    if not TELEGRAM_CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID is required")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

    # Log database configuration
    if DATABASE_URL:
        logger.info("Using PostgreSQL database")
    else:
        logger.info(f"Using SQLite database at {DB_PATH}")

    return True

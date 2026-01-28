"""
Main entry point for PMCC Bot
"""
import asyncio
import logging
from datetime import datetime, time
from pytz import timezone
import schedule
from threading import Thread
from models import Database, LeapsPosition, ShortCall
from tradier import TradierAPI
from alerts import AlertMonitor
from bot import PMCCBot
import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class PMCCScheduler:
    """Scheduler for monitoring and alerts"""

    def __init__(self, db: Database, api: TradierAPI, bot: PMCCBot):
        self.db = db
        self.api = api
        self.bot = bot
        self.alert_monitor = AlertMonitor(db, api)
        self.eastern = timezone('US/Eastern')

    def is_market_hours(self) -> bool:
        """Check if currently in market hours"""
        now = datetime.now(self.eastern)

        # Skip weekends
        if now.weekday() >= 5:
            return False

        market_open = time(config.MARKET_OPEN_HOUR, config.MARKET_OPEN_MINUTE)
        market_close = time(config.MARKET_CLOSE_HOUR, config.MARKET_CLOSE_MINUTE)

        return market_open <= now.time() <= market_close

    def check_positions(self):
        """Check positions and send alerts"""
        if not self.is_market_hours():
            logger.debug("Outside market hours, skipping position check")
            return

        logger.info("Checking positions for alerts")

        try:
            alerts = self.alert_monitor.check_all_positions()

            if alerts:
                # Send alerts via Telegram
                for alert in alerts:
                    asyncio.run(self.bot.send_alert(alert['message']))

                logger.info(f"Sent {len(alerts)} alerts")
            else:
                logger.info("No alerts triggered")

        except Exception as e:
            logger.error(f"Error checking positions: {e}")

    def send_daily_summary(self):
        """Send daily summary"""
        logger.info("Sending daily summary")

        try:
            asyncio.run(self.bot.send_daily_summary())
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")

    def setup_schedule(self):
        """Setup scheduled tasks"""
        # Monitor positions every N minutes during market hours
        schedule.every(config.POLL_INTERVAL_MINUTES).minutes.do(self.check_positions)

        # Daily summary at specified time
        summary_time = f"{config.DAILY_SUMMARY_HOUR:02d}:{config.DAILY_SUMMARY_MINUTE:02d}"
        schedule.every().day.at(summary_time).do(self.send_daily_summary)

        logger.info(f"Scheduled position checks every {config.POLL_INTERVAL_MINUTES} minutes")
        logger.info(f"Scheduled daily summary at {summary_time} ET")

    def run(self):
        """Run scheduler in background thread"""
        import time

        def scheduler_thread():
            logger.info("Starting scheduler thread")
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        thread = Thread(target=scheduler_thread, daemon=True)
        thread.start()
        logger.info("Scheduler thread started")


def seed_example_data(db: Database):
    """Seed database with example positions"""
    leaps_model = LeapsPosition(db)
    short_call_model = ShortCall(db)

    # Check if data already exists
    if leaps_model.get_active():
        logger.info("Database already has data, skipping seed")
        return

    logger.info("Seeding example data")

    # Add example LEAPS
    leaps_id = leaps_model.add(
        symbol="SPY",
        strike=620.0,
        expiration="2027-01-17",
        entry_price=109.00,
        quantity=2,
        notes="Example LEAPS position"
    )

    # Add example short call
    short_call_model.add(
        leaps_id=leaps_id,
        symbol="SPY",
        strike=730.0,
        expiration="2026-03-21",
        entry_price=6.50,
        quantity=2,
        notes="Example short call position"
    )

    logger.info("Example data seeded successfully")


def main():
    """Main entry point"""
    try:
        # Validate configuration
        config.validate_config()
        logger.info("Configuration validated")

        # Initialize database
        db = Database(config.DB_PATH)
        logger.info("Database initialized")

        # Seed example data (only if database is empty)
        seed_example_data(db)

        # Initialize API client
        api = TradierAPI(config.TRADIER_API_KEY, config.TRADIER_BASE_URL)
        logger.info("Tradier API client initialized")

        # Initialize Telegram bot
        bot = PMCCBot(db, api)
        logger.info("Telegram bot initialized")

        # Initialize scheduler
        scheduler = PMCCScheduler(db, api, bot)
        scheduler.setup_schedule()
        scheduler.run()

        # Run bot (blocking)
        logger.info("Starting PMCC Bot")
        bot.run()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

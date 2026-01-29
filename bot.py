"""
Telegram bot handlers
"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters
)
from telegram.constants import ParseMode
from models import Database, LeapsPosition, ShortCall
from tradier import TradierAPI
from alerts import AlertMonitor
from scanner import OptionScanner
import config

logger = logging.getLogger(__name__)


class PMCCBot:
    """PMCC Telegram Bot"""

    def __init__(self, db: Database, api: TradierAPI):
        self.db = db
        self.api = api
        self.leaps_model = LeapsPosition(db)
        self.short_call_model = ShortCall(db)
        self.alert_monitor = AlertMonitor(db, api)
        self.scanner = OptionScanner(db, api)

        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self._register_handlers()

    def _register_handlers(self):
        """Register command handlers"""
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("positions", self.cmd_positions))
        self.app.add_handler(CommandHandler("alerts", self.cmd_alerts))
        self.app.add_handler(CommandHandler("roll", self.cmd_roll))
        self.app.add_handler(CommandHandler("newcall", self.cmd_newcall))
        self.app.add_handler(CommandHandler("close", self.cmd_close))
        self.app.add_handler(CommandHandler("add_leaps", self.cmd_add_leaps))
        self.app.add_handler(CommandHandler("add_short", self.cmd_add_short))
        self.app.add_handler(CommandHandler("summary", self.cmd_summary))
        self.app.add_handler(CommandHandler("clear", self.cmd_clear))

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        await update.message.reply_text(
            "👋 Welcome to PMCC Bot!\n\n"
            "I'll help you manage your Poor Man's Covered Call positions.\n"
            "Use /help to see available commands."
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """📚 PMCC Bot Commands

📊 Position Management
/positions - Show current positions
/add_leaps <symbol> <strike> <exp> <price> <qty> - Add LEAPS
/add_short <leaps_id> <symbol> <strike> <exp> <price> <qty> - Add short call
/clear confirm - Delete ALL positions (requires confirm)

🔔 Monitoring
/alerts - Show active alert thresholds
/summary - Get cost basis summary

🔍 Scanning
/roll <short_call_id> - Get roll candidates
/newcall <leaps_id> - Get new short call candidates

💰 Trading
/close <short_call_id> <exit_price> - Log closed short call

Examples:
/add_leaps SPY 620 2027-01-17 109.00 2
/add_short 1 SPY 730 2026-03-21 6.50 2
/close 1 3.25"""
        await update.message.reply_text(help_text)

    async def cmd_positions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current positions"""
        leaps_positions = self.leaps_model.get_active()
        short_calls = self.short_call_model.get_active()

        if not leaps_positions:
            await update.message.reply_text("No active LEAPS positions")
            return

        output = "📊 *Current Positions*\n\n"

        for leaps in leaps_positions:
            adjusted_cost = self.leaps_model.get_adjusted_cost_basis(leaps['id'])
            output += f"*LEAPS #{leaps['id']}*\n"
            output += f"{leaps['symbol']} ${leaps['strike']:.0f}C exp {leaps['expiration']}\n"
            output += f"Entry: ${leaps['entry_price']:.2f} × {leaps['quantity']}\n"
            output += f"Adjusted basis: ${adjusted_cost:.2f}/contract\n\n"

            # Find associated short calls
            leaps_shorts = [sc for sc in short_calls if sc['leaps_id'] == leaps['id']]
            if leaps_shorts:
                output += "*Short Calls:*\n"
                for sc in leaps_shorts:
                    status = self.alert_monitor.get_position_status(sc['id'])
                    if 'error' not in status:
                        output += f"  • #{sc['id']}: ${sc['strike']:.0f}C exp {sc['expiration']}\n"
                        output += f"    Entry: ${sc['entry_price']:.2f} | Current: ${status['current_price']:.2f}\n"
                        output += f"    P/L: {status['profit_pct']*100:.1f}% (${status['profit_dollars']:.2f})\n"
                        output += f"    DTE: {status['dte']}\n\n"
            else:
                output += "*No active short calls*\n\n"

        await update.message.reply_text(output, parse_mode=ParseMode.MARKDOWN)

    async def cmd_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show alert thresholds"""
        output = "🔔 *Alert Configuration*\n\n"
        output += f"Close candidate: {config.PROFIT_THRESHOLD_LOW*100:.0f}% profit\n"
        output += f"Strong close: {config.PROFIT_THRESHOLD_HIGH*100:.0f}% profit\n"
        output += f"Strike proximity: {config.STRIKE_PROXIMITY_PCT*100:.0f}%\n"
        output += f"Expiration warning: {config.LOW_PROFIT_DTE_THRESHOLD} DTE\n"
        output += f"\nMonitoring every {config.POLL_INTERVAL_MINUTES} minutes during market hours"

        await update.message.reply_text(output, parse_mode=ParseMode.MARKDOWN)

    async def cmd_roll(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get roll candidates"""
        if not context.args:
            await update.message.reply_text("Usage: /roll <short_call_id>")
            return

        try:
            short_call_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Invalid short call ID")
            return

        await update.message.reply_text("🔍 Scanning roll candidates...")

        candidates = self.scanner.find_roll_candidates(short_call_id)
        output = self.scanner.format_roll_candidates(candidates)

        await update.message.reply_text(output, parse_mode=ParseMode.MARKDOWN)

    async def cmd_newcall(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get new short call candidates"""
        if not context.args:
            await update.message.reply_text("Usage: /newcall <leaps_id>")
            return

        try:
            leaps_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Invalid LEAPS ID")
            return

        await update.message.reply_text("🔍 Scanning new call candidates...")

        candidates = self.scanner.find_new_call_candidates(leaps_id)
        output = self.scanner.format_new_call_candidates(candidates)

        await update.message.reply_text(output, parse_mode=ParseMode.MARKDOWN)

    async def cmd_close(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Close a short call"""
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /close <short_call_id> <exit_price>")
            return

        try:
            short_call_id = int(context.args[0])
            exit_price = float(context.args[1])
        except ValueError:
            await update.message.reply_text("Invalid parameters")
            return

        try:
            profit = self.short_call_model.close(short_call_id, exit_price)

            position = self.short_call_model.get_by_id(short_call_id)
            leaps = self.leaps_model.get_by_id(position['leaps_id'])
            adjusted_cost = self.leaps_model.get_adjusted_cost_basis(position['leaps_id'])

            output = "✅ *Short Call Closed*\n\n"
            output += f"Position: {position['symbol']}\n"
            output += f"Entry: ${position['entry_price']:.2f} | Exit: ${exit_price:.2f}\n"
            output += f"Profit: ${profit:.2f}\n\n"
            output += f"*Updated Cost Basis*\n"
            output += f"LEAPS adjusted basis: ${adjusted_cost:.2f}/contract"

            await update.message.reply_text(output, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await update.message.reply_text(f"Error closing position: {e}")

    async def cmd_add_leaps(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add LEAPS position"""
        if len(context.args) < 5:
            await update.message.reply_text(
                "Usage: /add_leaps <symbol> <strike> <expiration> <price> <quantity>\n"
                "Example: /add_leaps SPY 620 2027-01-17 109.00 2"
            )
            return

        try:
            symbol = context.args[0]
            strike = float(context.args[1])
            expiration = context.args[2]
            price = float(context.args[3])
            quantity = int(context.args[4])

            leaps_id = self.leaps_model.add(symbol, strike, expiration, price, quantity)

            await update.message.reply_text(
                f"✅ LEAPS added (ID: {leaps_id})\n"
                f"{symbol} ${strike:.0f}C exp {expiration}\n"
                f"Cost: ${price:.2f} × {quantity}"
            )
        except Exception as e:
            await update.message.reply_text(f"Error adding LEAPS: {e}")

    async def cmd_add_short(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add short call position"""
        if len(context.args) < 6:
            await update.message.reply_text(
                "Usage: /add_short <leaps_id> <symbol> <strike> <expiration> <price> <quantity>\n"
                "Example: /add_short 1 SPY 730 2026-03-21 6.50 2"
            )
            return

        try:
            leaps_id = int(context.args[0])
            symbol = context.args[1]
            strike = float(context.args[2])
            expiration = context.args[3]
            price = float(context.args[4])
            quantity = int(context.args[5])

            short_id = self.short_call_model.add(
                leaps_id, symbol, strike, expiration, price, quantity
            )

            await update.message.reply_text(
                f"✅ Short call added (ID: {short_id})\n"
                f"{symbol} ${strike:.0f}C exp {expiration}\n"
                f"Credit: ${price:.2f} × {quantity}"
            )
        except Exception as e:
            await update.message.reply_text(f"Error adding short call: {e}")

    async def cmd_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get cost basis summary"""
        await self.send_daily_summary()

    async def cmd_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear all positions (destructive - use with caution)"""
        # Require confirmation
        if not context.args or context.args[0].lower() != "confirm":
            await update.message.reply_text(
                "⚠️ WARNING: This will delete ALL positions, short calls, alerts, and cost basis history.\n\n"
                "To proceed, use: /clear confirm"
            )
            return

        try:
            with self.db.get_connection() as conn:
                if self.db.db_type == "postgresql":
                    with conn.cursor() as cursor:
                        cursor.execute("DELETE FROM cost_basis_history")
                        cursor.execute("DELETE FROM alerts")
                        cursor.execute("DELETE FROM short_calls")
                        cursor.execute("DELETE FROM leaps")
                        conn.commit()
                else:
                    conn.execute("DELETE FROM cost_basis_history")
                    conn.execute("DELETE FROM alerts")
                    conn.execute("DELETE FROM short_calls")
                    conn.execute("DELETE FROM leaps")
                    conn.commit()

            await update.message.reply_text(
                "✅ All positions cleared.\n\n"
                "Database is now empty and ready for real positions."
            )
            logger.info("All positions cleared via /clear command")

        except Exception as e:
            await update.message.reply_text(f"❌ Error clearing positions: {e}")
            logger.error(f"Error clearing positions: {e}")

    async def send_alert(self, message: str):
        """Send alert to Telegram"""
        try:
            await self.app.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info("Alert sent via Telegram")
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")

    async def send_daily_summary(self):
        """Send daily summary"""
        leaps_positions = self.leaps_model.get_active()
        short_calls = self.short_call_model.get_active()

        if not leaps_positions:
            return

        output = "📊 *Daily PMCC Summary*\n"
        output += f"_{datetime.now().strftime('%Y-%m-%d %H:%M ET')}_\n\n"

        total_premium = 0

        for leaps in leaps_positions:
            adjusted_cost = self.leaps_model.get_adjusted_cost_basis(leaps['id'])
            cost_reduction = (leaps['entry_price'] - adjusted_cost) * leaps['quantity']

            output += f"*{leaps['symbol']} ${leaps['strike']:.0f}C {leaps['expiration']}*\n"
            output += f"Original basis: ${leaps['entry_price']:.2f}\n"
            output += f"Adjusted basis: ${adjusted_cost:.2f}\n"
            output += f"Reduction: ${cost_reduction:.2f}\n\n"

            total_premium += cost_reduction

            # Check short calls status
            leaps_shorts = [sc for sc in short_calls if sc['leaps_id'] == leaps['id']]
            for sc in leaps_shorts:
                status = self.alert_monitor.get_position_status(sc['id'])
                if 'error' not in status:
                    if status['profit_pct'] >= config.PROFIT_THRESHOLD_LOW:
                        output += f"⚠️ Short ${sc['strike']:.0f}C: {status['profit_pct']*100:.1f}% profit - consider closing\n"
                    if status['dte'] <= 7:
                        output += f"⏰ Short ${sc['strike']:.0f}C: {status['dte']} DTE\n"

        output += f"\n*Total premium collected: ${total_premium:.2f}*"

        await self.send_alert(output)

    def run(self):
        """Run the bot"""
        logger.info("Starting Telegram bot")
        self.app.run_polling()

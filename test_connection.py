"""
Test script to verify API connections
"""
import sys
from config import validate_config, TRADIER_API_KEY, TRADIER_BASE_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from tradier import TradierAPI
import asyncio
from telegram import Bot

def test_tradier():
    """Test Tradier API connection"""
    print("Testing Tradier API connection...")
    print(f"Base URL: {TRADIER_BASE_URL}")

    try:
        api = TradierAPI(TRADIER_API_KEY, TRADIER_BASE_URL)
        quote = api.get_quote("SPY")

        if quote:
            print("✅ Tradier API connection successful!")
            print(f"   SPY Last Price: ${quote.get('last', 'N/A')}")
            return True
        else:
            print("❌ Failed to get quote from Tradier API")
            return False
    except Exception as e:
        print(f"❌ Tradier API error: {e}")
        return False


async def test_telegram():
    """Test Telegram Bot connection"""
    print("\nTesting Telegram Bot connection...")
    print(f"Chat ID: {TELEGRAM_CHAT_ID}")

    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="✅ PMCC Bot connection test successful!"
        )
        print("✅ Telegram Bot connection successful!")
        print("   Check your Telegram for the test message")
        return True
    except Exception as e:
        print(f"❌ Telegram Bot error: {e}")
        return False


def main():
    """Run all connection tests"""
    print("=" * 50)
    print("PMCC Bot Connection Test")
    print("=" * 50)

    # Validate config
    try:
        validate_config()
        print("✅ Configuration validated\n")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # Test Tradier
    tradier_ok = test_tradier()

    # Test Telegram
    telegram_ok = asyncio.run(test_telegram())

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Tradier API: {'✅ PASS' if tradier_ok else '❌ FAIL'}")
    print(f"Telegram Bot: {'✅ PASS' if telegram_ok else '❌ FAIL'}")

    if tradier_ok and telegram_ok:
        print("\n🎉 All tests passed! Ready to run the bot.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()

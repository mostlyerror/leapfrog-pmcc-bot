#!/bin/bash
# Quick setup script for PMCC Bot

set -e

echo "================================"
echo "PMCC Bot Setup Script"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
echo ""
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping..."
else
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your API credentials:"
    echo "   - TRADIER_API_KEY"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHAT_ID"
fi

# Create data directory for Docker
echo ""
echo "Creating data directory..."
mkdir -p data
echo "✅ Data directory created"

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials"
echo "   nano .env"
echo ""
echo "2. Test your connection"
echo "   python test_connection.py"
echo ""
echo "3. Run the bot"
echo "   python main.py"
echo ""
echo "Or use Docker:"
echo "   docker-compose up -d"
echo ""
echo "See QUICKSTART.md for detailed instructions."

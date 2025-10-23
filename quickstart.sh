#!/bin/bash

# Grievance Redressal Bot - Quick Start Script
# This script helps you set up and start the bot quickly

set -e

echo "🤖 Grievance Redressal Bot - Quick Start"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9.0"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo "❌ Python 3.9+ is required. You have Python $python_version"
    exit 1
fi
echo "✅ Python $python_version found"
echo ""

# Check Tesseract
echo "Checking Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    tesseract_version=$(tesseract --version 2>&1 | head -n 1)
    echo "✅ $tesseract_version found"
else
    echo "⚠️  Tesseract OCR not found!"
    echo ""
    echo "Please install Tesseract:"
    echo "  macOS:   brew install tesseract tesseract-lang"
    echo "  Ubuntu:  sudo apt-get install tesseract-ocr tesseract-ocr-hin"
    echo "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    echo ""
    read -p "Continue without Tesseract? OCR features will not work. (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment found"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing/Updating dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo ""
    
    if [ -f "env.example" ]; then
        echo "Creating .env from env.example..."
        cp env.example .env
        echo "✅ .env file created"
        echo ""
    fi
    
    echo "📝 Please configure your .env file with:"
    echo "   1. TELEGRAM_BOT_TOKEN (get from @BotFather on Telegram)"
    echo "   2. TESSERACT_CMD (path to tesseract executable)"
    echo ""
    
    # Try to find tesseract path automatically
    if command -v tesseract &> /dev/null; then
        tesseract_path=$(which tesseract)
        echo "   Detected Tesseract path: $tesseract_path"
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|TESSERACT_CMD=.*|TESSERACT_CMD=$tesseract_path|" .env 2>/dev/null || true
        else
            sed -i "s|TESSERACT_CMD=.*|TESSERACT_CMD=$tesseract_path|" .env 2>/dev/null || true
        fi
    fi
    
    echo ""
    read -p "Do you want to edit .env now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        ${EDITOR:-nano} .env
    fi
    echo ""
fi

# Check if TELEGRAM_BOT_TOKEN is set
if ! grep -q "^TELEGRAM_BOT_TOKEN=.\+$" .env 2>/dev/null; then
    echo "❌ TELEGRAM_BOT_TOKEN not configured in .env"
    echo ""
    echo "Please:"
    echo "  1. Open Telegram and search for @BotFather"
    echo "  2. Send /newbot and follow instructions"
    echo "  3. Copy your bot token to .env file"
    echo ""
    exit 1
fi
echo "✅ Configuration file ready"
echo ""

# Run tests
echo "Running tests..."
if python test_bot.py 2>&1 | tail -1 | grep -q "All tests passed"; then
    echo "✅ All tests passed!"
else
    echo "⚠️  Some tests failed, but you can still try running the bot"
fi
echo ""

# Ask to start bot
echo "=========================================="
echo "🎉 Setup complete!"
echo ""
echo "Your bot is ready to start."
echo ""
read -p "Start the bot now? (Y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "🚀 Starting Grievance Redressal Bot..."
    echo "Press Ctrl+C to stop"
    echo ""
    sleep 2
    python main.py
else
    echo ""
    echo "To start the bot later, run:"
    echo "  source venv/bin/activate"
    echo "  python main.py"
fi


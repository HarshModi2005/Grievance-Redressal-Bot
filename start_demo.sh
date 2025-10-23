#!/bin/bash

# Grievance Bot - Demo Mode Quick Start
echo "🎬 Grievance Redressal Bot - Demo Mode"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Creating from template..."
    cp env.example .env
fi

# Check if bot token is configured
if grep -q "123456789:ABCdefGHIjklMNOpqrsTUVwxyz-DUMMY_TOKEN" .env 2>/dev/null || grep -q "your_telegram_bot_token_here" .env 2>/dev/null; then
    echo "⚠️  WARNING: Dummy bot token detected!"
    echo ""
    echo "To run the demo, you need a real Telegram bot token."
    echo ""
    echo "📱 Steps to get your bot token:"
    echo "   1. Open Telegram and search for @BotFather"
    echo "   2. Send /newbot command"
    echo "   3. Follow instructions to create your bot"
    echo "   4. Copy the token you receive"
    echo ""
    read -p "Have you got your bot token? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "📝 Please enter your bot token:"
        read bot_token
        
        # Update .env with the token
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$bot_token|" .env
        else
            sed -i "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$bot_token|" .env
        fi
        
        echo "✅ Bot token configured!"
        echo ""
    else
        echo ""
        echo "Please get your bot token from @BotFather first, then run this script again."
        echo "OR edit .env file manually and add your token."
        exit 1
    fi
fi

echo "✅ Configuration ready!"
echo ""
echo "🔍 Checking environment..."

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import telegram" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
fi

echo "✅ All dependencies installed"
echo ""

# Check Tesseract
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found (OCR features will not work)"
    echo "   Install: brew install tesseract tesseract-lang (macOS)"
    echo "   Or: sudo apt-get install tesseract-ocr (Ubuntu)"
else
    echo "✅ Tesseract OCR found"
fi

echo ""
echo "=========================================="
echo "🚀 Starting Bot in DEMO MODE..."
echo "=========================================="
echo ""
echo "📋 Demo Features Available:"
echo "   ✅ Image upload & OCR processing"
echo "   ✅ Location detection (GPS + text)"
echo "   ✅ Smart complaint classification"
echo "   ✅ Mock UMANG submission"
echo "   ✅ Complaint tracking"
echo ""
echo "🎯 How to test:"
echo "   1. Open Telegram and find your bot"
echo "   2. Send /start command"
echo "   3. Click 'Submit New Complaint'"
echo "   4. Send a photo with text (road sign, poster, etc.)"
echo "   5. Watch the bot extract text and classify!"
echo ""
echo "💡 Tip: Use images with visible text for best results"
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""
sleep 2

# Start the bot
python main.py



# Grievance Redressal Bot - Setup Guide

Complete setup instructions for deploying the Grievance Redressal Telegram Bot.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Telegram Bot Setup](#telegram-bot-setup)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Python 3.9 or higher**
   ```bash
   python3 --version  # Should be 3.9+
   ```

2. **Tesseract OCR**
   - **macOS (via Homebrew):**
     ```bash
     brew install tesseract
     brew install tesseract-lang  # For Indian language support
     ```
   
   - **Ubuntu/Debian:**
     ```bash
     sudo apt-get update
     sudo apt-get install tesseract-ocr
     sudo apt-get install tesseract-ocr-hin tesseract-ocr-ben tesseract-ocr-tel tesseract-ocr-mar tesseract-ocr-guj tesseract-ocr-tam
     ```
   
   - **Windows:**
     - Download from: https://github.com/UB-Mannheim/tesseract/wiki
     - Install and note the installation path (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`)

3. **Git** (optional, for cloning)
   ```bash
   git --version
   ```

### Account Requirements

- **Telegram Account**: For creating and testing the bot
- **UMANG API Credentials** (optional): For production deployment with real government API integration

---

## System Requirements

- **RAM**: Minimum 512MB, Recommended 1GB+
- **Storage**: 500MB for dependencies + space for database and logs
- **Network**: Stable internet connection for Telegram API
- **OS**: Linux, macOS, or Windows

---

## Installation Steps

### 1. Clone or Download the Repository

```bash
# If using git
git clone https://github.com/yourusername/Grievance-Redressal-Bot.git
cd Grievance-Redressal-Bot

# Or download and extract the ZIP file
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

**Expected installation time**: 2-5 minutes depending on your internet speed.

### 4. Verify Tesseract Installation

```bash
# Check Tesseract version
tesseract --version

# Find Tesseract path
# On Linux/macOS:
which tesseract

# On Windows:
where tesseract
```

Note the path for later configuration.

---

## Configuration

### 1. Create Environment File

```bash
# Copy the example environment file
cp env.example .env

# On Windows:
copy env.example .env
```

### 2. Edit Configuration

Open `.env` file in your text editor and configure:

```bash
# Required - Get from BotFather (see next section)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Update Tesseract path based on your system
TESSERACT_CMD=/usr/bin/tesseract  # Linux
# TESSERACT_CMD=/opt/homebrew/bin/tesseract  # macOS (Intel)
# TESSERACT_CMD=/usr/local/bin/tesseract  # macOS (Apple Silicon)
# TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe  # Windows

# Optional - Keep empty for testing with mock client
UMANG_CLIENT_ID=
UMANG_CLIENT_SECRET=

# Other settings - defaults are fine for most cases
DATABASE_URL=sqlite:///grievance_bot.db
LOG_LEVEL=INFO
LOG_FILE=bot.log
OCR_LANGUAGES=eng+hin+ben+tel+mar+guj+tam
```

---

## Telegram Bot Setup

### 1. Create Your Bot with BotFather

1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather
3. Send `/newbot` command
4. Follow the prompts:
   - **Bot Name**: "Grievance Redressal Bot" (or your choice)
   - **Bot Username**: Must end with 'bot', e.g., `grievance_redressal_bot`

5. BotFather will provide your bot token:
   ```
   Done! Your bot token is: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

6. Copy this token to your `.env` file

### 2. Configure Bot Settings (Optional but Recommended)

Send these commands to BotFather:

```
/setdescription @your_bot_username
```
Description:
```
I help you submit public grievances to government departments through official channels (CPGRAMS/UMANG). Submit complaints with photos, track status, and get automated routing to appropriate departments.
```

```
/setabouttext @your_bot_username
```
About:
```
Official Grievance Redressal Assistant Bot for Indian citizens
```

```
/setuserpic @your_bot_username
```
Upload an appropriate profile picture for your bot.

```
/setcommands @your_bot_username
```
Commands:
```
start - Start the bot
help - Get help and instructions
menu - Show main menu
cancel - Cancel current operation
```

---

## Testing

### 1. Run Test Suite

Before starting the bot, run tests to verify everything is working:

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run tests
python test_bot.py
```

**Expected output**:
```
🚀 Starting Grievance Redressal Bot Tests
==================================================
✅ Configuration validation: PASSED
✅ Database operations: PASSED
✅ OCR processing: PASSED
✅ Location detection: PASSED
✅ Complaint classification: PASSED
✅ UMANG client: PASSED
✅ End-to-end workflow: PASSED
==================================================
📈 TOTAL: 7 tests | ✅ PASSED: 7 | ❌ FAILED: 0
🎉 All tests passed! Bot is ready for deployment.
```

### 2. Common Test Issues

**Issue**: OCR tests fail
- **Solution**: Ensure Tesseract is installed and `TESSERACT_CMD` path is correct in `.env`

**Issue**: "Tesseract not found" error
- **Solution**: 
  ```bash
  # Find Tesseract path
  which tesseract  # Linux/macOS
  where tesseract  # Windows
  
  # Update .env with correct path
  ```

**Issue**: Import errors
- **Solution**: Reinstall dependencies
  ```bash
  pip install --force-reinstall -r requirements.txt
  ```

---

## Deployment

### 1. Start the Bot

```bash
# Make sure you're in the project directory with venv activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the bot
python main.py
```

**Expected output**:
```
2024-10-23 10:30:00,000 - __main__ - INFO - Configuration validated successfully
2024-10-23 10:30:00,100 - __main__ - INFO - Startup cleanup completed
2024-10-23 10:30:00,500 - __main__ - INFO - Starting Grievance Redressal Bot...
2024-10-23 10:30:00,800 - __main__ - INFO - Bot is ready to receive messages!
```

### 2. Test Your Bot

1. Open Telegram
2. Search for your bot username (e.g., `@grievance_redressal_bot`)
3. Click **Start** or send `/start`
4. You should see the welcome message with menu options

### 3. Test Basic Flows

**Test 1: Manual Complaint**
1. Click "📝 Manual Complaint Entry"
2. Type a sample complaint: "Road is damaged with potholes at MG Road, Mumbai 400001"
3. Follow the prompts

**Test 2: Image-based Complaint**
1. Click "📸 Submit New Complaint"
2. Take or upload a photo with visible text
3. Follow the analysis and submission flow

**Test 3: Tracking**
1. Click "📊 Track Existing Complaint"
2. Enter a reference ID from previous submission
3. View the status

### 4. Production Deployment Options

#### Option A: Run on Server (VPS/Cloud)

**Using screen (Linux):**
```bash
# Install screen
sudo apt-get install screen

# Start a screen session
screen -S grievance_bot

# Activate venv and run bot
source venv/bin/activate
python main.py

# Detach from screen: Press Ctrl+A, then D
# Reattach later: screen -r grievance_bot
```

**Using systemd (Linux):**

Create `/etc/systemd/system/grievance-bot.service`:
```ini
[Unit]
Description=Grievance Redressal Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/Grievance-Redressal-Bot
Environment="PATH=/path/to/Grievance-Redressal-Bot/venv/bin"
ExecStart=/path/to/Grievance-Redressal-Bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable grievance-bot
sudo systemctl start grievance-bot
sudo systemctl status grievance-bot
```

#### Option B: Docker Deployment (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Install Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-hin \
    tesseract-ocr-ben \
    tesseract-ocr-tel \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t grievance-bot .
docker run -d --name grievance-bot \
  --env-file .env \
  -v $(pwd)/grievance_bot.db:/app/grievance_bot.db \
  grievance-bot
```

#### Option C: Cloud Platforms

**Heroku:**
- Add `Procfile`: `worker: python main.py`
- Add tesseract buildpack: `heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-apt`
- Create `Aptfile`: `tesseract-ocr tesseract-ocr-hin`
- Deploy: `git push heroku main`

**Railway/Render:**
- Similar to Heroku
- Configure build and start commands in platform settings

---

## Troubleshooting

### Common Issues

#### 1. Bot doesn't respond

**Symptoms**: Bot is running but doesn't reply to messages

**Solutions**:
- Verify bot token is correct in `.env`
- Check bot is running: `ps aux | grep main.py`
- Check logs: `tail -f bot.log`
- Ensure no firewall blocking Telegram API
- Try restarting the bot

#### 2. OCR not working

**Symptoms**: "No text extracted" or OCR errors

**Solutions**:
- Verify Tesseract installation: `tesseract --version`
- Check TESSERACT_CMD path in `.env`
- Test Tesseract manually:
  ```bash
  tesseract test_image.jpg output
  cat output.txt
  ```
- Install language packs if missing

#### 3. Location detection fails

**Symptoms**: "Could not detect location"

**Solutions**:
- Ensure geopy is installed: `pip install geopy`
- Check internet connectivity (needed for geocoding)
- Use manual location input instead
- Verify location text contains Indian addresses/pincodes

#### 4. Database errors

**Symptoms**: SQLAlchemy errors, locked database

**Solutions**:
- Delete database and restart: `rm grievance_bot.db`
- Check file permissions
- Ensure only one bot instance is running

#### 5. Memory issues

**Symptoms**: Bot crashes, slow performance

**Solutions**:
- Increase system RAM
- Monitor with: `top` or `htop`
- Check temp_images directory size
- Cleanup is automatic but can run manually:
  ```python
  python -c "from main import bot_handler; bot_handler.cleanup_temp_images()"
  ```

### Getting Help

1. **Check Logs**: 
   ```bash
   tail -100 bot.log
   ```

2. **Enable Debug Logging**:
   In `.env`: `LOG_LEVEL=DEBUG`

3. **Test Individual Components**:
   ```bash
   python test_bot.py
   ```

4. **Report Issues**:
   - GitHub Issues: [Your repo URL]
   - Include: logs, error messages, system info

---

## Security Considerations

### For Production Use:

1. **Secure your `.env` file**:
   ```bash
   chmod 600 .env
   ```

2. **Use HTTPS for webhooks** (if applicable)

3. **Regular backups**:
   ```bash
   # Backup database
   cp grievance_bot.db grievance_bot_backup_$(date +%Y%m%d).db
   ```

4. **Monitor logs for suspicious activity**

5. **Keep dependencies updated**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

6. **Use environment-specific configs**:
   - Development: `.env.development`
   - Production: `.env.production`

---

## Advanced Configuration

### Custom OCR Languages

Add more Tesseract languages:
```bash
# Install additional language pack
sudo apt-get install tesseract-ocr-[language_code]

# Update .env
OCR_LANGUAGES=eng+hin+[your_language]
```

### Database Migration to PostgreSQL

For production with multiple instances:

1. Install PostgreSQL
2. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/grievance_db
   ```
3. Install driver: `pip install psycopg2-binary`

### UMANG API Integration

For real government portal integration:

1. Apply for UMANG API credentials
2. Update `.env`:
   ```
   UMANG_CLIENT_ID=your_client_id
   UMANG_CLIENT_SECRET=your_client_secret
   ```
3. Bot will automatically use real API instead of mock

---

## Monitoring and Maintenance

### Log Monitoring

```bash
# Watch logs in real-time
tail -f bot.log

# Search for errors
grep ERROR bot.log

# Monitor specific user
grep "telegram_id: 123456" bot.log
```

### Database Maintenance

```bash
# View database stats
sqlite3 grievance_bot.db "SELECT COUNT(*) FROM complaints;"
sqlite3 grievance_bot.db "SELECT COUNT(*) FROM users;"

# Clean old sessions (if needed)
sqlite3 grievance_bot.db "DELETE FROM complaint_sessions WHERE updated_at < datetime('now', '-7 days');"
```

### Performance Monitoring

```bash
# Check bot process
ps aux | grep main.py

# Monitor resource usage
top -p $(pgrep -f main.py)

# Check disk usage
du -sh grievance_bot.db temp_images/
```

---

## Updating the Bot

### Pull Latest Changes

```bash
# Stop the bot first
# Ctrl+C or systemctl stop grievance-bot

# Pull updates
git pull

# Update dependencies
pip install --upgrade -r requirements.txt

# Run tests
python test_bot.py

# Restart bot
python main.py
```

---

## Support

For issues, questions, or contributions:

- **Documentation**: See README.md
- **Issues**: GitHub Issues page
- **Email**: [Your support email]

---

## License

[Your License Information]

---

**Last Updated**: October 2024
**Version**: 1.0.0


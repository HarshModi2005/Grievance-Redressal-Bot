# Grievance Redressal Telegram Bot

A comprehensive Telegram bot that processes images to extract complaint details, detects locations, classifies grievances, and submits them through official UMANG/CPGRAMS channels.

## 🌟 Features

- **📸 Image Processing**: Uses Tesseract OCR to extract text from complaint images
- **📍 Smart Location Detection**: Multi-method location detection via GPS metadata, OCR text analysis, and manual input
- **🏷️ Intelligent Classification**: NLP-based complaint categorization for proper routing
- **🚀 Official Integration**: Submits grievances through UMANG API to CPGRAMS system
- **📊 Complaint Tracking**: Track complaint status using reference IDs
- **💾 Data Management**: Secure storage of complaint history and user sessions
- **🔒 Privacy Compliant**: Follows IT Act 2000 guidelines for data protection

## 📋 Supported Complaint Categories

- **🛣️ Roads & Transport**: Potholes, traffic issues, highway problems
- **💧 Water & Drainage**: Supply issues, pipe leaks, drainage blocks
- **⚡ Electricity & Power**: Outages, equipment problems, billing issues
- **🗑️ Sanitation & Waste**: Garbage collection, cleanliness, public toilets
- **🏥 Healthcare**: Hospital services, medical facilities, staff issues
- **🎓 Education**: School problems, infrastructure, teacher issues
- **🚌 Public Transport**: Bus services, railway issues, stations
- **🏢 Public Services**: Government offices, documentation, procedures
- **🏠 Housing**: Building issues, society problems, construction
- **🍽️ Food Safety**: Restaurant hygiene, food quality, health violations

## 🔧 Installation & Setup

### Quick Start (Recommended)

The easiest way to get started:

**Linux/macOS:**
```bash
./quickstart.sh
```

**Windows:**
```cmd
quickstart.bat
```

The script will automatically:
- Check Python and Tesseract installation
- Create virtual environment
- Install dependencies
- Configure environment file
- Run tests
- Start the bot

### Manual Setup

For detailed step-by-step instructions, see **[SETUP.md](SETUP.md)** for comprehensive setup guide including:
- Detailed installation instructions for all platforms
- Configuration options
- Testing procedures
- Deployment options
- Troubleshooting guide

### Prerequisites

1. **Python 3.9+** (3.8 minimum, 3.9+ recommended)
2. **Tesseract OCR** installed on your system
3. **Telegram Bot Token** from [@BotFather](https://t.me/botfather)
4. **UMANG API Credentials** (optional - uses mock client if not available)

### System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-hin tesseract-ocr-ben
sudo apt install libtesseract-dev
```

#### macOS:
```bash
brew install tesseract tesseract-lang
```

#### Windows:
1. Download Tesseract from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and note the installation path
3. Update `TESSERACT_CMD` in configuration

### Python Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd Grievance-Redressal-Bot
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Create environment configuration**:
```bash
cp .env.example .env
```

5. **Configure environment variables** in `.env`:
```env
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Optional (uses mock client if not provided)
UMANG_CLIENT_ID=your_umang_client_id
UMANG_CLIENT_SECRET=your_umang_client_secret

# OCR Configuration
TESSERACT_CMD=/usr/bin/tesseract  # Adjust path as needed
OCR_LANGUAGES=eng+hin+ben+tel+mar+guj+tam

# Database (SQLite by default)
DATABASE_URL=sqlite:///grievance_bot.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log
```

### Getting Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token to your `.env` file

### UMANG API Access (Optional)

For production use with real CPGRAMS integration:

1. Visit [API Setu](https://www.apisetu.gov.in)
2. Register as a developer
3. Apply for UMANG/CPGRAMS API access
4. Add credentials to `.env` file

**Note**: Without UMANG credentials, the bot uses a mock client for testing.

## 🚀 Usage

### Starting the Bot

```bash
python main.py
```

The bot will start polling for Telegram messages.

### Bot Commands

- `/start` - Initialize the bot and show main menu
- `/help` - Show detailed help and instructions
- `/menu` - Return to main menu
- `/cancel` - Cancel current operation

### User Workflow

#### 1. Image-Based Complaint
1. Send `/start` to the bot
2. Click "📸 Submit New Complaint"
3. Send a clear photo of the issue
4. Bot automatically:
   - Extracts text using OCR
   - Detects location from GPS/text
   - Classifies complaint category
5. Review and confirm details
6. Submit to government portal
7. Receive reference ID for tracking

#### 2. Manual Complaint
1. Click "📝 Manual Complaint Entry"
2. Type detailed complaint description
3. Include location and issue details
4. Bot classifies and processes
5. Submit to official channels

#### 3. Track Complaint
1. Click "📊 Track Existing Complaint"
2. Enter your reference ID
3. Get current status and updates

## 🏗️ Architecture

### Core Components

- **`main.py`** - Telegram bot application and conversation flow
- **`config.py`** - Configuration management and environment variables
- **`database.py`** - SQLAlchemy models and database operations
- **`ocr_processor.py`** - Tesseract OCR integration and image processing
- **`location_detector.py`** - Multi-method location detection system
- **`complaint_classifier.py`** - NLP-based complaint categorization
- **`umang_client.py`** - UMANG API client with OAuth authentication

### Database Schema

- **Users**: Telegram user information
- **Complaints**: Submitted grievances with status tracking
- **ComplaintSessions**: Temporary data during complaint creation

### OCR Processing Pipeline

1. **Image Preprocessing**: Auto-rotation, resizing, format conversion
2. **Text Extraction**: Multi-language OCR with confidence scoring
3. **Location Parsing**: Address pattern recognition
4. **GPS Extraction**: EXIF metadata coordinate extraction

### Location Detection Methods

1. **GPS Metadata**: Extract coordinates from image EXIF data
2. **Text Analysis**: Pattern matching for Indian addresses
3. **Manual Input**: User-provided location information
4. **Geocoding**: Convert addresses to coordinates using Nominatim

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | - | Yes |
| `UMANG_CLIENT_ID` | UMANG API client ID | - | No |
| `UMANG_CLIENT_SECRET` | UMANG API client secret | - | No |
| `TESSERACT_CMD` | Tesseract executable path | `/usr/bin/tesseract` | No |
| `OCR_LANGUAGES` | OCR language codes | `eng+hin+ben+tel+mar+guj+tam` | No |
| `DATABASE_URL` | Database connection string | `sqlite:///grievance_bot.db` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `MAX_REQUESTS_PER_MINUTE` | Rate limiting | `10` | No |

### OCR Languages

The bot supports multiple Indian languages:
- `eng` - English
- `hin` - Hindi (हिंदी)
- `ben` - Bengali (বাংলা)
- `tel` - Telugu (తెలుగు)
- `mar` - Marathi (मराठी)
- `guj` - Gujarati (ગુજરાતી)
- `tam` - Tamil (தமிழ்)

Add more languages by updating `OCR_LANGUAGES` in configuration.

## 🧪 Testing

### Run Basic Tests

```bash
# Test OCR functionality
python -c "from ocr_processor import ocr_processor; print('OCR module loaded successfully')"

# Test database connection
python -c "from database import db_manager; print('Database connected successfully')"

# Test UMANG client (mock)
python -c "from umang_client import umang_client; print('UMANG client ready')"
```

### Test Bot Commands

1. Start the bot: `python main.py`
2. Send `/start` in Telegram
3. Try different workflows:
   - Upload test image
   - Submit manual complaint
   - Track complaint with mock ID

### Mock vs Production

- **Development**: Uses mock UMANG client without real API calls
- **Production**: Requires UMANG API credentials for real submissions

## 🔒 Security & Privacy

### Data Protection

- **Encryption**: Sensitive data encrypted in transit and at rest
- **Local Storage**: Images temporarily stored and automatically cleaned
- **No PII Storage**: No permanent storage of personal information
- **Audit Trail**: All API interactions logged securely

### Compliance

- **IT Act 2000**: Compliant data handling procedures
- **CPGRAMS Guidelines**: Follows official grievance data formats
- **Privacy Notice**: Clear disclaimer about unofficial nature

### Security Features

- **Rate Limiting**: Prevents spam and abuse
- **Input Validation**: Sanitizes all user inputs
- **Error Handling**: Graceful failure without data exposure
- **Session Management**: Secure temporary data storage

## 🚀 Deployment

### Local Development

```bash
python main.py
```

### Production Deployment

#### Using Docker (Recommended)

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-hin tesseract-ocr-ben \
    libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

#### Using systemd service

```ini
[Unit]
Description=Grievance Redressal Bot
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/path/to/Grievance-Redressal-Bot
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Cloud Deployment

#### Heroku
1. Create `Procfile`: `bot: python main.py`
2. Add Heroku buildpack for Tesseract
3. Set environment variables in Heroku dashboard

#### AWS/GCP/Azure
1. Use container services with Docker image
2. Configure environment variables
3. Set up persistent storage for database

## 📊 Monitoring & Logs

### Log Levels

- **INFO**: General operation information
- **WARNING**: Non-critical issues
- **ERROR**: Error conditions
- **DEBUG**: Detailed debugging information

### Key Metrics

- **Complaints Processed**: Total submissions
- **OCR Success Rate**: Text extraction accuracy
- **Location Detection Rate**: Successful location identification
- **API Response Times**: UMANG integration performance
- **User Activity**: Active users and usage patterns

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit pull request with detailed description

### Code Standards

- **PEP 8**: Python code formatting
- **Type Hints**: Use type annotations
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Graceful failure handling
- **Logging**: Appropriate log levels and messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

**1. Tesseract not found**
- Ensure Tesseract is installed and `TESSERACT_CMD` is correct
- Test: `tesseract --version`

**2. Bot not responding**
- Check bot token validity
- Verify network connectivity
- Check logs for errors

**3. OCR accuracy issues**
- Use well-lit, clear images
- Ensure text is readable
- Try different languages if needed

**4. Location detection fails**
- Include address details in image text
- Use manual location input option
- Check if GPS data exists in image

### Getting Help

1. **Documentation**: Check this README thoroughly
2. **Logs**: Review bot.log for error details
3. **Issues**: Create GitHub issue with details
4. **Community**: Join discussions for support

### Contact

- **GitHub Issues**: [Repository Issues](https://github.com/your-repo/issues)
- **Email**: your-email@domain.com
- **Documentation**: [Wiki](https://github.com/your-repo/wiki)

## 🛣️ Roadmap

### Upcoming Features

- **Multi-language UI**: Support regional languages in bot interface
- **Voice Input**: Voice message processing for complaints
- **Image Analysis**: Computer vision for automatic issue detection
- **Real-time Notifications**: Status updates via Telegram
- **Analytics Dashboard**: Complaint trends and statistics
- **WhatsApp Integration**: Expand to WhatsApp Business API

### Long-term Goals

- **AI-Powered Routing**: Advanced ML models for department routing
- **Sentiment Analysis**: Priority based on complaint sentiment
- **Integration Expansion**: Connect with more state portals
- **Mobile App**: Native mobile applications
- **Citizen Portal**: Web interface for complaint management

---

**Made with ❤️ for better governance and citizen services in India**


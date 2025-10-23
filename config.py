"""
Configuration management for the Grievance Redressal Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for bot settings"""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # UMANG API Configuration
    UMANG_CLIENT_ID = os.getenv('UMANG_CLIENT_ID')
    UMANG_CLIENT_SECRET = os.getenv('UMANG_CLIENT_SECRET')
    UMANG_API_BASE_URL = os.getenv('UMANG_API_BASE_URL', 'https://api.umang.gov.in')
    
    # OCR Configuration
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', '/usr/bin/tesseract')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///grievance_bot.db')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    # Security Configuration
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '10'))
    
    # Supported Languages for OCR
    OCR_LANGUAGES = os.getenv('OCR_LANGUAGES', 'eng+hin+ben+tel+mar+guj+tam').split('+')
    
    # Complaint Categories
    COMPLAINT_CATEGORIES = {
        'roads': ['road', 'highway', 'street', 'pothole', 'traffic'],
        'water': ['water', 'drainage', 'sewer', 'pipeline', 'supply'],
        'electricity': ['power', 'electricity', 'light', 'transformer', 'outage'],
        'sanitation': ['garbage', 'waste', 'cleaning', 'toilet', 'hygiene'],
        'healthcare': ['hospital', 'clinic', 'doctor', 'medicine', 'health'],
        'education': ['school', 'college', 'teacher', 'education', 'student'],
        'transport': ['bus', 'train', 'transport', 'station', 'vehicle'],
        'other': ['general', 'misc', 'other', 'complaint']
    }

def validate_config():
    """Validate required configuration variables"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(Config, var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True


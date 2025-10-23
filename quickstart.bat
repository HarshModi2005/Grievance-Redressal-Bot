@echo off
REM Grievance Redressal Bot - Quick Start Script for Windows
REM This script helps you set up and start the bot quickly

echo.
echo Grievance Redressal Bot - Quick Start
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

REM Check Tesseract
echo Checking Tesseract OCR...
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo Warning: Tesseract OCR not found!
    echo.
    echo Please install Tesseract from:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo Default installation path: C:\Program Files\Tesseract-OCR\tesseract.exe
    echo.
    set /p continue="Continue without Tesseract? OCR features will not work. (y/N): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    tesseract --version 2>&1 | findstr /R "tesseract"
    echo Tesseract found!
)
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment found
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error activating virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

REM Install dependencies
echo Installing/Updating dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo Dependencies installed
echo.

REM Check for .env file
if not exist ".env" (
    echo Warning: .env file not found!
    echo.
    
    if exist "env.example" (
        echo Creating .env from env.example...
        copy env.example .env >nul
        echo .env file created
    )
    
    echo.
    echo Please configure your .env file with:
    echo   1. TELEGRAM_BOT_TOKEN ^(get from @BotFather on Telegram^)
    echo   2. TESSERACT_CMD ^(path to tesseract executable^)
    echo.
    echo Example for Windows:
    echo   TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
    echo.
    
    set /p edit="Do you want to edit .env now? (Y/n): "
    if /i not "%edit%"=="n" (
        notepad .env
    )
    echo.
)

REM Check if TELEGRAM_BOT_TOKEN is set
findstr /R "^TELEGRAM_BOT_TOKEN=..*$" .env >nul 2>&1
if errorlevel 1 (
    echo Error: TELEGRAM_BOT_TOKEN not configured in .env
    echo.
    echo Please:
    echo   1. Open Telegram and search for @BotFather
    echo   2. Send /newbot and follow instructions
    echo   3. Copy your bot token to .env file
    echo.
    pause
    exit /b 1
)
echo Configuration file ready
echo.

REM Run tests
echo Running tests...
python test_bot.py >test_output.tmp 2>&1
type test_output.tmp | findstr /C:"All tests passed" >nul
if errorlevel 1 (
    echo Warning: Some tests failed, but you can still try running the bot
) else (
    echo All tests passed!
)
del test_output.tmp >nul 2>&1
echo.

REM Ask to start bot
echo ==========================================
echo Setup complete!
echo.
echo Your bot is ready to start.
echo.
set /p start="Start the bot now? (Y/n): "

if /i not "%start%"=="n" (
    echo.
    echo Starting Grievance Redressal Bot...
    echo Press Ctrl+C to stop
    echo.
    timeout /t 2 >nul
    python main.py
) else (
    echo.
    echo To start the bot later, run:
    echo   venv\Scripts\activate
    echo   python main.py
    echo.
    pause
)


@echo off
REM WattWise Admin Portal - Startup Script for Windows

echo.
echo 🚀 WattWise Admin Portal Backend
echo ==================================
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo 📋 Creating .env from .env.example...
    copy .env.example .env
    echo ✅ .env created. Please edit it with your settings.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Initialize database
echo 🗄️  Initializing database...
python -c "from config.database import init_db; init_db()" 2>nul || (
    echo ⚠️  Database initialization skipped (check your DATABASE_URL)
)

echo.
echo ✅ Setup complete!
echo.
echo 🌐 Starting server...
echo 📖 API docs available at: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python main.py

pause


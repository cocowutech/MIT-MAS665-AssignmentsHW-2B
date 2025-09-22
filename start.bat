@echo off
REM Adaptive English Placement Assessment - Windows Startup Script

echo 🚀 Starting Adaptive English Placement Assessment System
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is required but not installed.
    echo Please install Node.js 16+ and try again.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is required but not installed.
    echo Please install npm and try again.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "backend\uploads\audio" mkdir "backend\uploads\audio"
if not exist "backend\uploads\writing" mkdir "backend\uploads\writing"
if not exist "backend\uploads\content" mkdir "backend\uploads\content"

REM Backend setup
echo 🐍 Setting up Python backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Start backend server in background
echo 🚀 Starting backend server...
start /b python main.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Frontend setup
echo ⚛️ Setting up React frontend...
cd ..\frontend

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

REM Start frontend server
echo 🚀 Starting frontend server...
start /b npm start

echo.
echo 🎉 Application started successfully!
echo ==================================================
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop both servers
pause >nul

REM Stop background processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo ✅ Servers stopped
pause

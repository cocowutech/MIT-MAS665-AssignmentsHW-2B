#!/bin/bash

echo "🚀 Starting Adaptive English Placement Assessment System (Simplified)"
echo "=================================================================="

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create directories
mkdir -p backend/uploads/audio
mkdir -p backend/uploads/writing
mkdir -p backend/uploads/content

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install minimal dependencies first
echo "Installing core dependencies..."
pip install fastapi uvicorn python-multipart python-dotenv

# Start backend server
echo "🚀 Starting backend server..."
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Frontend setup
echo "⚛️ Setting up React frontend..."
cd ../frontend

# Install dependencies with --force to bypass cache issues
echo "Installing frontend dependencies..."
npm install --force

# Start frontend server
echo "🚀 Starting frontend server..."
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Application started!"
echo "========================"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM
wait

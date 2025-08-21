#!/bin/bash

# StudyGenie Development Startup Script

echo "🚀 StudyGenie Local Development Setup"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "VS_CODE_SETUP.md" ]; then
    echo "❌ Please run this script from the root project directory (/app)"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🔍 Checking prerequisites..."

# Check Python
if command_exists python3; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Node.js
if command_exists node; then
    echo "✅ Node.js found: $(node --version)"
else
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

# Check Yarn
if command_exists yarn; then
    echo "✅ Yarn found: $(yarn --version)"
else
    echo "❌ Yarn not found. Please install Yarn"
    exit 1
fi

# Check MongoDB (optional check)
if command_exists mongod; then
    echo "✅ MongoDB found"
else
    echo "⚠️  MongoDB not found in PATH. Make sure MongoDB is installed and running on localhost:27017"
fi

echo ""
echo "📦 Installing dependencies..."

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip3 install -r requirements.txt
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
yarn install
cd ..

echo ""
echo "🎯 Setup complete!"
echo ""
echo "To start development:"
echo "1. Open two terminals in VS Code"
echo "2. Terminal 1: cd backend && python server.py"
echo "3. Terminal 2: cd frontend && yarn start"
echo ""
echo "Or use the VS Code tasks (Ctrl+Shift+P → 'Tasks: Run Task' → 'Start Both Services')"
echo ""
echo "URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8001"
echo "  API Docs: http://localhost:8001/docs"
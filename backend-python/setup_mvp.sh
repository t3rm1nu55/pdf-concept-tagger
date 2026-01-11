#!/bin/bash
# MVP Setup Script
# Sets up Python environment, installs dependencies, and prepares database

set -e

echo "🚀 Setting up PDF Concept Tagger MVP..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "   ✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Creating .env file from .env.example..."
    cp .env.example .env
    echo "   ⚠️  Please edit .env and add your Cognizant proxy configuration!"
else
    echo "   ✅ .env file exists"
fi

# Check Docker
echo ""
echo "🐳 Checking Docker..."
if command -v docker &> /dev/null; then
    echo "   ✅ Docker is installed"
    if docker ps &> /dev/null; then
        echo "   ✅ Docker is running"
    else
        echo "   ⚠️  Docker is not running. Start Docker to use PostgreSQL."
    fi
else
    echo "   ⚠️  Docker not found. Install Docker to use PostgreSQL."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Cognizant proxy configuration"
echo "2. Start PostgreSQL: docker-compose -f docker-compose.mvp.yml up -d"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start server: uvicorn app.main:app --reload"
echo ""
echo "To activate virtual environment later:"
echo "  source venv/bin/activate"

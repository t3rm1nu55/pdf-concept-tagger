#!/bin/bash
# Setup script for backend-python
# Creates virtual environment and installs dependencies

set -e  # Exit on error

echo "🚀 Setting up Backend Python Environment..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Check if Python 3.11+ is available
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo "⚠️  Warning: Python 3.11+ recommended. Current: $PYTHON_VERSION"
    echo "   Continuing anyway, but some features may not work."
    echo ""
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo ""
    echo "📝 Creating .env.example file..."
    cat > .env.example << 'EOF'
# LLM APIs
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here

# Vector Database
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENV=us-east-1-aws
PINECONE_INDEX_NAME=concepts

# Graph Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j

# Document Processing
DOCLING_API_KEY=your_docling_key_here  # Optional

# PostgreSQL
POSTGRES_URL=postgresql://user:password@localhost:5432/pdf_tagger

# Redis
REDIS_URL=redis://localhost:6379

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# Server
API_PORT=8000
WS_PORT=8001
EOF
    echo "✅ Created .env.example"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
else
    echo ""
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the example usage:"
echo "   python llamaindex_example_usage.py"
echo ""
echo "4. Or start developing your own code!"
echo ""
echo "To deactivate the virtual environment:"
echo "   deactivate"
echo ""

#!/bin/bash
# Start MVP Services Script

set -e

echo "🚀 Starting PDF Concept Tagger MVP Services"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gateway is running
echo -n "Checking Cognizant LLM Gateway... "
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${YELLOW}⚠️  Not running${NC}"
    echo ""
    echo "Start the gateway in another terminal:"
    echo "  cd /Users/markforster/cognizant-llm-gateway"
    echo "  python -m clg.server"
    echo ""
    read -p "Press Enter when gateway is running, or Ctrl+C to exit..."
fi

# Check PostgreSQL
echo -n "Checking PostgreSQL... "
if docker ps | grep -q postgres; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${YELLOW}⚠️  Starting PostgreSQL...${NC}"
    docker-compose -f docker-compose.mvp.yml up -d
    sleep 3
    echo -e "${GREEN}✅ PostgreSQL started${NC}"
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
fi

# Run migrations
echo "Running database migrations..."
alembic upgrade head > /dev/null 2>&1 || echo "Migrations may need attention"

# Start server
echo ""
echo -e "${GREEN}✅ Starting MVP Backend...${NC}"
echo "Server will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

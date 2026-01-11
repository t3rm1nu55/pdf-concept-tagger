#!/bin/bash

# End-to-End Startup Script
# Starts all services needed for full system

set -e

echo "🚀 Starting PDF Concept Tagger - End-to-End"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon not running. Please start Docker Desktop.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker daemon running${NC}"

echo ""
echo "🔧 Starting Services..."
echo ""

# 1. Start PostgreSQL
echo "1️⃣  Starting PostgreSQL..."
cd backend-python
if docker-compose -f docker-compose.mvp.yml ps | grep -q "Up"; then
    echo -e "${YELLOW}   PostgreSQL already running${NC}"
else
    docker-compose -f docker-compose.mvp.yml up -d
    echo -e "${GREEN}   ✅ PostgreSQL started${NC}"
    sleep 2  # Give it time to start
fi

# 2. Run migrations
echo ""
echo "2️⃣  Running database migrations..."
if [ -d "venv" ]; then
    source venv/bin/activate
    if alembic upgrade head; then
        echo -e "${GREEN}   ✅ Migrations complete${NC}"
    else
        echo -e "${RED}   ❌ Migrations failed!${NC}"
        echo "      Check the error above and fix before continuing."
        exit 1
    fi
else
    echo -e "${RED}   ❌ Virtual environment not found!${NC}"
    echo ""
    echo "      Migrations CANNOT run without the virtual environment."
    echo "      Run setup first:"
    echo "      cd backend-python && ./setup_mvp.sh"
    echo ""
    echo -e "${RED}   Exiting - migrations are required for the system to work.${NC}"
    exit 1
fi

# 3. Check gateway
echo ""
echo "3️⃣  Checking Cognizant LLM Gateway..."
GATEWAY_URL="${COGNIZANT_LLM_GATEWAY_URL:-http://localhost:8080}"
if curl -s "$GATEWAY_URL/health" &> /dev/null; then
    echo -e "${GREEN}   ✅ Gateway is running at $GATEWAY_URL${NC}"
else
    echo -e "${YELLOW}   ⚠️  Gateway not running at $GATEWAY_URL${NC}"
    echo "      Start it in another terminal:"
    echo "      cd /Users/markforster/cognizant-llm-gateway"
    echo "      python -m clg.server"
fi

# 4. Start backend
echo ""
echo "4️⃣  Starting FastAPI backend..."
if [ -d "venv" ]; then
    echo -e "${GREEN}   ✅ Backend ready to start${NC}"
    echo ""
    echo "   To start backend, run:"
    echo "   cd backend-python"
    echo "   source venv/bin/activate"
    echo "   uvicorn app.main:app --reload"
    echo ""
else
    echo -e "${YELLOW}   ⚠️  Virtual environment not found${NC}"
fi

# 5. Frontend
echo ""
echo "5️⃣  Frontend..."
cd ..
if [ -f "index.html" ]; then
    echo -e "${GREEN}   ✅ Frontend files ready${NC}"
    echo ""
    echo "   To start frontend, run:"
    echo "   python3 -m http.server 3000"
    echo "   Then open: http://localhost:3000"
    echo ""
else
    echo -e "${RED}   ❌ Frontend files not found${NC}"
fi

echo ""
echo "============================================"
echo "📊 Status Summary"
echo "============================================"
echo ""
echo "Backend:"
echo "  - PostgreSQL: $(docker ps --filter 'name=postgres' --format '{{.Status}}' 2>/dev/null || echo 'Not running')"
echo "  - FastAPI: Ready to start (see instructions above)"
echo ""
echo "Frontend:"
echo "  - Angular app: Ready"
echo "  - Start server: python3 -m http.server 3000"
echo ""
echo "Gateway:"
if curl -s "$GATEWAY_URL/health" &> /dev/null; then
    echo "  - Status: ✅ Running"
else
    echo "  - Status: ⚠️  Not running (start manually)"
fi
echo ""
echo "============================================"
echo "🧪 Quick Test"
echo "============================================"
echo ""
echo "Once all services are running:"
echo ""
echo "1. Test backend health:"
echo "   curl http://localhost:8000/health"
echo ""
echo "2. Test frontend:"
echo "   Open http://localhost:3000 in browser"
echo ""
echo "3. Upload a PDF and watch concepts appear!"
echo ""

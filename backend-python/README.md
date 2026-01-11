# Backend Python - PDF Concept Tagger MVP

> **FastAPI backend with Cognizant LLM Gateway integration**

## Quick Start

```bash
# 1. Start gateway (separate terminal)
cd /Users/markforster/cognizant-llm-gateway
python -m clg.server

# 2. Setup backend
cd backend-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-mvp.txt

# 3. Configure
cp .env.example .env
# Edit .env: set COGNIZANT_LLM_GATEWAY_URL=http://localhost:8080

# 4. Start database
docker-compose -f docker-compose.mvp.yml up -d

# 5. Run migrations
alembic upgrade head

# 6. Start server
uvicorn app.main:app --reload
```

See [docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md) for detailed instructions.

## Documentation

- **[Getting Started](../docs/GETTING_STARTED.md)** - Quick start guide
- **[Setup Guide](../docs/SETUP.md)** - Complete setup instructions
- **[MVP Status](../docs/MVP_STATUS.md)** - Current status and features
- **[Gateway Setup](GATEWAY_SETUP.md)** - Cognizant LLM Gateway configuration
- **[Testing Guide](TESTING.md)** - Testing instructions

## Project Structure

```
backend-python/
├── app/
│   ├── api/v1/endpoints/    # API endpoints
│   ├── services/            # Business logic
│   ├── models/              # Database models
│   ├── database/            # Database connection
│   └── core/                # Core utilities (logging, etc.)
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
└── requirements-mvp.txt    # MVP dependencies
```

## API Endpoints

- `POST /api/v1/analyze` - Upload PDF and extract concepts
- `GET /api/v1/concepts` - List concepts
- `GET /api/v1/graph` - Get graph data
- `WS /api/v1/ws/{document_id}` - Real-time updates

See [docs/MVP_STATUS.md](../docs/MVP_STATUS.md) for full API documentation.

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
ruff check app/
black app/
mypy app/
```

See [PROJECT_RULES.md](../PROJECT_RULES.md) for development standards.

## Status

✅ **MVP Complete** - Core features working, ready for frontend integration

See [docs/MVP_STATUS.md](../docs/MVP_STATUS.md) for current status and next steps.

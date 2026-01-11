# MVP Quick Start Guide

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (for PostgreSQL)
- Cognizant proxy endpoint and API key

## Setup (5 minutes)

### 1. Configure Environment

```bash
cd backend-python
cp .env.example .env
# Edit .env and add your Cognizant proxy configuration
```

**Required in `.env`**:
```bash
# Cognizant LLM Gateway URL (defaults to localhost:8080)
COGNIZANT_LLM_GATEWAY_URL=http://localhost:8080
COGNIZANT_LLM_GATEWAY_API_KEY=  # Optional

# LLM Provider and Model
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview

# PostgreSQL Database
POSTGRES_URL=postgresql://pdf_tagger:pdf_tagger_dev@localhost:5432/pdf_tagger_mvp
```

### 2. Start PostgreSQL

```bash
docker-compose -f docker-compose.mvp.yml up -d
```

### 3. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
# Initialize Alembic (if not done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial MVP schema"

# Apply migrations
alembic upgrade head
```

### 5. Run Tests

```bash
pytest
```

### 6. Start Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 7. Test API

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","version":"0.1.0-mvp","proxy_configured":true}
```

## MVP Features

✅ **Working**:
- FastAPI server with health check
- Cognizant proxy integration
- PostgreSQL database setup
- Basic concept model
- Test structure

🚧 **In Progress** (see todos):
- PDF upload endpoint
- Concept extraction (HARVESTER agent)
- Concept storage
- Graph endpoint
- WebSocket updates

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_cognizant_proxy.py

# Run with verbose output
pytest -v
```

## Troubleshooting

### Proxy Connection Issues
- Verify `COGNIZANT_PROXY_ENDPOINT` is correct
- Check `COGNIZANT_PROXY_API_KEY` is set
- Test proxy endpoint manually: `curl -X POST $COGNIZANT_PROXY_ENDPOINT/chat/completions`

### Database Connection Issues
- Ensure PostgreSQL is running: `docker ps`
- Check connection string in `.env`
- Test connection: `psql $POSTGRES_URL -c "SELECT 1"`

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11+)

## Next Steps

1. Complete MVP Phase 2 tasks (see todos)
2. Implement PDF upload endpoint
3. Implement HARVESTER agent
4. Add concept storage
5. Test end-to-end workflow

See `MVP_BUILD_PLAN.md` for full plan.

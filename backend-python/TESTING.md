# MVP Testing Guide

## Quick Test Commands

### 1. Test Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Test imports
python3 -c "from app.main import app; print('✅ App imports OK')"

# Run unit tests
pytest tests/test_cognizant_proxy.py -v
```

### 2. Test Database Connection
```bash
# Start PostgreSQL
docker-compose -f docker-compose.mvp.yml up -d

# Test connection
python3 -c "from app.database.postgres import check_connection; import asyncio; print('✅ DB OK' if asyncio.run(check_connection()) else '❌ DB Failed')"
```

### 3. Test API Endpoints

**Start server:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Test health check:**
```bash
curl http://localhost:8000/health
```

**Test root:**
```bash
curl http://localhost:8000/
```

**Test concepts endpoint (requires DB):**
```bash
curl http://localhost:8000/api/v1/concepts
```

### 4. Test PDF Analysis (End-to-End)

**Prerequisites:**
- PostgreSQL running
- Cognizant proxy configured in `.env`
- Test PDF file available

```bash
# Upload PDF and extract concepts
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@test.pdf" \
  -F "page_number=1"
```

## Test Coverage

### Unit Tests
- ✅ Cognizant proxy service
- ✅ PDF processor
- ✅ Concept models
- ⏳ Database operations (requires DB)

### Integration Tests
- ⏳ API endpoints (requires DB + proxy)
- ⏳ End-to-end workflow (requires DB + proxy + PDF)

## Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_cognizant_proxy.py

# With verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Test Data

Create `test_data/` directory with sample PDFs for testing.

## Troubleshooting

### Import Errors
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

### Database Errors
- Ensure PostgreSQL is running: `docker ps`
- Check connection string in `.env`
- Run migrations: `alembic upgrade head`

### Proxy Errors
- Verify `COGNIZANT_PROXY_ENDPOINT` in `.env`
- Check `COGNIZANT_PROXY_API_KEY` is set
- Test proxy manually with curl

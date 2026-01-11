# MVP Quick Start Guide

Get the PDF Concept Tagger MVP running in 5 minutes.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Cognizant LLM Gateway (see GATEWAY_SETUP.md)

## Step 1: Start Cognizant LLM Gateway

```bash
cd /Users/markforster/cognizant-llm-gateway

# Install dependencies (if not done)
pip install -r requirements.txt

# Start gateway
python -m clg.server
# Or: uvicorn clg.server:app --host 0.0.0.0 --port 8080
```

Verify gateway is running:
```bash
curl http://localhost:8080/health
curl http://localhost:8080/v1/models
```

## Step 2: Setup MVP Backend

```bash
cd backend-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment

Create `.env` file:
```bash
# Cognizant LLM Gateway
COGNIZANT_LLM_GATEWAY_URL=http://localhost:8080
LLM_MODEL=gpt-4-turbo-preview  # Or any model available in gateway

# PostgreSQL
POSTGRES_URL=postgresql://pdf_tagger:pdf_tagger_dev@localhost:5432/pdf_tagger_mvp

# Optional
DEBUG=False
```

## Step 4: Start PostgreSQL

```bash
docker-compose -f docker-compose.mvp.yml up -d
```

Verify PostgreSQL is running:
```bash
docker ps | grep postgres
```

## Step 5: Run Database Migrations

```bash
alembic upgrade head
```

## Step 6: Start MVP Backend

```bash
uvicorn app.main:app --reload --port 8000
```

## Step 7: Test the API

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "version": "0.1.0-mvp",
#   "gateway_url": "http://localhost:8080",
#   "gateway_configured": true
# }

# Test PDF analysis (requires a PDF file)
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@test.pdf" \
  -F "page_number=1"
```

## Troubleshooting

### Gateway not responding
- Check gateway is running: `curl http://localhost:8080/health`
- Verify port 8080 is available
- Check gateway logs

### Database connection errors
- Verify PostgreSQL is running: `docker ps`
- Check connection string in `.env`
- Run migrations: `alembic upgrade head`

### Import errors
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

## Next Steps

- See `GATEWAY_SETUP.md` for gateway configuration
- See `TESTING.md` for testing guide
- See `README_MVP.md` for detailed documentation

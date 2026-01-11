# Getting Started - PDF Concept Tagger

> **Get up and running in 5 minutes**

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Cognizant LLM Gateway (see [Gateway Setup](backend-python/GATEWAY_SETUP.md))

## Quick Start (5 minutes)

### 1. Start Cognizant LLM Gateway

```bash
cd /Users/markforster/cognizant-llm-gateway
python -m clg.server
```

Gateway runs on `http://localhost:8080`

### 2. Setup MVP Backend

```bash
cd backend-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-mvp.txt

# Configure environment
cp .env.example .env
# Edit .env and set COGNIZANT_LLM_GATEWAY_URL=http://localhost:8080
```

### 3. Start PostgreSQL

```bash
docker-compose -f docker-compose.mvp.yml up -d
```

### 4. Run Migrations

```bash
alembic upgrade head
```

### 5. Start Backend Server

```bash
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`

### 6. Test

```bash
curl http://localhost:8000/health
```

## What's Next?

- **Test the API**: See [MVP Status](MVP_STATUS.md) for available endpoints
- **Connect Frontend**: See [Prototype Alignment](PROTOTYPE_ALIGNMENT.md)
- **Expand Features**: See [Tasks](demo-machine/TASKS.md)

## Troubleshooting

### Gateway not responding
- Check gateway is running: `curl http://localhost:8080/health`
- See [Gateway Setup](backend-python/GATEWAY_SETUP.md)

### Database errors
- Verify PostgreSQL is running: `docker ps`
- Check connection string in `.env`
- Run migrations: `alembic upgrade head`

### Import errors
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements-mvp.txt`

## Full Setup Guide

For detailed setup instructions, see [SETUP.md](SETUP.md)

## Current Status

See [MVP_STATUS.md](MVP_STATUS.md) for what's working and what's next.

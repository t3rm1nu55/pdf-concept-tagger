# Complete Setup Guide

> **Detailed setup instructions for PDF Concept Tagger**

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Cognizant LLM Gateway](#cognizant-llm-gateway)
3. [MVP Backend Setup](#mvp-backend-setup)
4. [Database Setup](#database-setup)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- **Python 3.11+** - Backend development
- **Docker & Docker Compose** - PostgreSQL database
- **Git** - Version control

### Optional
- **Node.js 18+** - For frontend development (future)
- **PostgreSQL client** - For direct database access

### Verify Installation

```bash
python3 --version  # Should be 3.11+
docker --version
docker-compose --version
```

---

## Cognizant LLM Gateway

The MVP backend requires the Cognizant LLM Gateway to be running.

### Quick Start

```bash
cd /Users/markforster/cognizant-llm-gateway

# Install dependencies (if not done)
pip install -r requirements.txt

# Start gateway
python -m clg.server
```

### Verify Gateway

```bash
curl http://localhost:8080/health
curl http://localhost:8080/v1/models
```

### Configuration

See [Gateway Setup](backend-python/GATEWAY_SETUP.md) for detailed configuration.

---

## MVP Backend Setup

### 1. Create Virtual Environment

```bash
cd backend-python
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# MVP dependencies (minimal)
pip install -r requirements-mvp.txt

# Or full dependencies (includes LangChain, LlamaIndex, etc.)
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Cognizant LLM Gateway
COGNIZANT_LLM_GATEWAY_URL=http://localhost:8080
LLM_MODEL=gpt-4-turbo-preview

# PostgreSQL
POSTGRES_URL=postgresql://pdf_tagger:pdf_tagger_dev@localhost:5432/pdf_tagger_mvp

# Optional
DEBUG=False
```

### 4. Verify Setup

```bash
python3 -c "from app.main import app; print('✅ App imports successfully')"
```

---

## Database Setup

### 1. Start PostgreSQL

```bash
docker-compose -f docker-compose.mvp.yml up -d
```

### 2. Verify Database

```bash
docker ps | grep postgres
```

### 3. Run Migrations

```bash
cd backend-python
source venv/bin/activate
alembic upgrade head
```

### 4. Verify Schema

```bash
# Connect to database (optional)
docker exec -it pdf-tagger-postgres psql -U pdf_tagger -d pdf_tagger_mvp
\dt  # List tables
```

---

## Configuration

### Environment Variables

See [Environment Config](config/ENV_CONFIG.md) for all available variables.

### Required Variables

- `COGNIZANT_LLM_GATEWAY_URL` - Gateway endpoint
- `POSTGRES_URL` - Database connection string

### Optional Variables

- `LLM_MODEL` - Model to use (default: gpt-4-turbo-preview)
- `DEBUG` - Enable debug logging (default: False)
- `COGNIZANT_LLM_GATEWAY_API_KEY` - Gateway API key (if required)

---

## Testing

### 1. Start Server

```bash
cd backend-python
source venv/bin/activate
uvicorn app.main:app --reload
```

### 2. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0-mvp",
  "gateway_url": "http://localhost:8080",
  "gateway_configured": true
}
```

### 3. Test API Endpoints

```bash
# List concepts
curl http://localhost:8000/api/v1/concepts

# Get graph data
curl http://localhost:8000/api/v1/graph
```

### 4. Run Tests

```bash
# Unit tests
pytest tests/test_cognizant_proxy.py -v

# Integration tests
pytest tests/test_api.py -v

# All tests
pytest tests/ -v
```

See [Testing Guide](backend-python/TESTING.md) for more details.

---

## Troubleshooting

### Gateway Connection Issues

**Problem**: `Gateway HTTP error` or connection refused

**Solutions**:
1. Verify gateway is running: `curl http://localhost:8080/health`
2. Check `COGNIZANT_LLM_GATEWAY_URL` in `.env`
3. Verify gateway port (default: 8080)
4. Check gateway logs for errors

### Database Connection Issues

**Problem**: `connection refused` or `database does not exist`

**Solutions**:
1. Verify PostgreSQL is running: `docker ps`
2. Check `POSTGRES_URL` in `.env`
3. Verify database exists: `docker exec -it pdf-tagger-postgres psql -U pdf_tagger -l`
4. Run migrations: `alembic upgrade head`

### Import Errors

**Problem**: `ModuleNotFoundError` or import failures

**Solutions**:
1. Verify virtual environment is activated
2. Install dependencies: `pip install -r requirements-mvp.txt`
3. Check Python version: `python3 --version` (should be 3.11+)
4. Verify you're in the correct directory

### Migration Errors

**Problem**: Migration fails or tables don't exist

**Solutions**:
1. Check database connection
2. Verify migrations exist: `ls alembic/versions/`
3. Check migration status: `alembic current`
4. Reset database (if needed): `alembic downgrade base && alembic upgrade head`

---

## Next Steps

- **Test the API**: Upload a PDF and extract concepts
- **Connect Frontend**: See [Prototype Alignment](PROTOTYPE_ALIGNMENT.md)
- **Expand Features**: See [Tasks](demo-machine/TASKS.md)

---

## Additional Resources

- [Gateway Setup](backend-python/GATEWAY_SETUP.md) - Detailed gateway configuration
- [Testing Guide](backend-python/TESTING.md) - Testing instructions
- [MVP Status](MVP_STATUS.md) - Current status and features
- [Project Rules](../PROJECT_RULES.md) - Development standards

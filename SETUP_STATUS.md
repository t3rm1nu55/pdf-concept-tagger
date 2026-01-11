# Setup Status & Next Steps

## Current Status

### ✅ Completed
- Virtual environment created
- MVP dependencies installed (using requirements-mvp.txt)
- Start script created (`start_services.sh`)

### ⚠️  Action Required

**1. Start Docker Desktop**
- Docker is not currently running
- PostgreSQL requires Docker to run
- Start Docker Desktop application

**2. Start Cognizant LLM Gateway**
```bash
cd /Users/markforster/cognizant-llm-gateway

# Install gateway dependencies (if not done)
pip install -r requirements.txt

# Start gateway
python -m clg.server
```

**3. Start PostgreSQL**
Once Docker is running:
```bash
cd backend-python
docker-compose -f docker-compose.mvp.yml up -d
```

**4. Run Migrations**
```bash
cd backend-python
source venv/bin/activate
alembic upgrade head
```

**5. Start MVP Backend**
```bash
cd backend-python
./start_services.sh
```

## Quick Start (Once Docker is Running)

```bash
# Terminal 1: Start Gateway
cd /Users/markforster/cognizant-llm-gateway
python -m clg.server

# Terminal 2: Start MVP Backend
cd backend-python
./start_services.sh
```

## Dependencies

- **MVP**: Uses `requirements-mvp.txt` (minimal dependencies)
- **Full Demo**: Uses `requirements.txt` (includes LangChain, LlamaIndex, etc.)

For MVP, only `requirements-mvp.txt` is needed.

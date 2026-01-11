# Quick Start - End-to-End

> **Get everything running in 5 minutes**

## Prerequisites

- Python 3.11+
- Docker Desktop (running)
- Cognizant LLM Gateway (separate repo)

## One-Command Start

```bash
./start_e2e.sh
```

This will:
1. ✅ Check prerequisites
2. ✅ Start PostgreSQL
3. ✅ Run database migrations
4. ✅ Check gateway status
5. ✅ Show you how to start backend and frontend

## Manual Start (3 Terminals)

### Terminal 1: Gateway
```bash
cd /Users/markforster/cognizant-llm-gateway
python -m clg.server
```
**Runs on**: `http://localhost:8080`

### Terminal 2: Backend
```bash
cd backend-python
./start_services.sh
```
**Or manually**:
```bash
cd backend-python
docker-compose -f docker-compose.mvp.yml up -d
source venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload
```
**Runs on**: `http://localhost:8000`

### Terminal 3: Frontend
```bash
# In project root
python3 -m http.server 3000
```
**Open**: `http://localhost:3000`

## Verify It Works

### 1. Test Backend
```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "version": "0.1.0-mvp",
  "gateway_url": "http://localhost:8080",
  "gateway_configured": true
}
```

### 2. Test Frontend
- Open `http://localhost:3000`
- Should see PDF Concept Tagger UI
- Click "Analyze Document" or upload a PDF

### 3. Watch Concepts Extract
- Concepts appear in D3.js graph
- Sidebar shows concept list
- Log panel shows agent activity

## Troubleshooting

**PostgreSQL not starting?**
```bash
docker ps  # Check if running
docker-compose -f backend-python/docker-compose.mvp.yml up -d
```

**Backend import errors?**
```bash
cd backend-python
source venv/bin/activate
pip install -r requirements-mvp.txt
```

**Frontend CORS errors?**
- Use `python -m http.server 3000` (not file://)
- Check backend CORS is enabled (it is by default)

**Gateway not responding?**
```bash
curl http://localhost:8080/health
# If fails, start gateway in separate terminal
```

## What You'll See

1. **Backend running**: `INFO: Uvicorn running on http://127.0.0.1:8000`
2. **Frontend**: Angular app with PDF viewer and graph
3. **Concepts**: Appear in real-time as they're extracted
4. **Graph**: D3.js visualization updates live

## Next Steps

- Upload a PDF and watch it work!
- Check `docs/E2E_STATUS.md` for detailed status
- See `docs/TESTING.md` for testing guide

---

**Ready to go!** 🚀

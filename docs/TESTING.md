# Testing Guide

> **How to test the MVP end-to-end**

## Quick Test

### 1. Start Services

**Terminal 1: Cognizant LLM Gateway**
```bash
cd /Users/markforster/cognizant-llm-gateway
python -m clg.server
```

**Terminal 2: PostgreSQL**
```bash
cd backend-python
docker-compose -f docker-compose.mvp.yml up -d
```

**Terminal 3: Backend**
```bash
cd backend-python
source venv/bin/activate
alembic upgrade head  # Run migrations
uvicorn app.main:app --reload
```

### 2. Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Test PDF upload (if you have a test PDF)
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@test.pdf" \
  -F "page_number=1"
```

### 3. Test Frontend

1. Open `index.html` in browser (or serve via local server)
2. Upload a PDF or load from URL
3. Verify concepts appear in graph
4. Check browser console for errors

## API Testing

### Test Analyze Endpoint (PDF)

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@sample.pdf" \
  -F "page_number=1" \
  --no-buffer
```

Expected: Streaming AgentPackets (newline-delimited JSON)

### Test Analyze Endpoint (Image Base64)

```bash
# First, encode an image to base64
IMAGE_B64=$(base64 -i image.png)

curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$IMAGE_B64\", \"pageNumber\": 1, \"excludeTerms\": []}"
```

Expected: Streaming AgentPackets

### Test Concepts Endpoint

```bash
# Get all concepts
curl http://localhost:8000/api/v1/concepts

# Get concepts for a document
curl "http://localhost:8000/api/v1/concepts?document_id={document_id}"

# Filter by type
curl "http://localhost:8000/api/v1/concepts?type=concept"
```

### Test Graph Endpoint

```bash
curl http://localhost:8000/api/v1/graph
```

### Test WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/{document_id}');
ws.onmessage = (event) => {
  const packet = JSON.parse(event.data);
  console.log('Received:', packet);
};
```

## Unit Tests

```bash
cd backend-python
source venv/bin/activate
pytest tests/ -v
```

## Integration Tests

```bash
cd backend-python
source venv/bin/activate
pytest tests/test_integration.py -v
```

## Troubleshooting

### Backend won't start

- Check PostgreSQL is running: `docker ps`
- Check gateway is running: `curl http://localhost:8080/health`
- Check environment variables: `cat .env`

### No concepts extracted

- Check backend logs: `tail -f backend-python/logs/app.log`
- Verify gateway connection
- Test with a simple PDF

### Frontend can't connect

- Check backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `app/main.py`
- Check browser console for errors

### Database errors

- Run migrations: `alembic upgrade head`
- Check connection string in `.env`
- Verify PostgreSQL is accessible

## Success Criteria

✅ Backend starts without errors  
✅ Health check returns 200  
✅ PDF upload extracts concepts  
✅ Concepts stored in database  
✅ Frontend receives AgentPackets  
✅ Graph visualization works  
✅ WebSocket updates work  

## Next Steps

After successful testing:
1. Expand agent implementations
2. Add OCR for image-based analysis
3. Implement ARCHITECT, CURATOR, CRITIC agents
4. Add Neo4j integration
5. Add RAG pipeline

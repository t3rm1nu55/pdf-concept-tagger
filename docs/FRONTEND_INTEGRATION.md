# Frontend Integration Guide

> **How to connect the Angular frontend to the FastAPI backend**

## Quick Start

### 1. Update Frontend Configuration

Edit `src/services/config.service.ts` or set environment variables:

```typescript
// Set backend URL
BACKEND_API_URL=http://localhost:8000
BACKEND_WS_URL=ws://localhost:8000
```

### 2. Update BackendApiService

The `BackendApiService` in `src/services/backend-api.service.ts` needs to:

1. **Change API endpoint** from `/api/v1/analyze` to `/api/v1/analyze`
2. **Update WebSocket URL** to `ws://localhost:8000/api/v1/ws/{document_id}`
3. **Handle AgentPacket format** (already done in prototype)

### 3. Start Backend

```bash
cd backend-python
./start_services.sh
```

Backend runs on `http://localhost:8000`

### 4. Test Connection

```bash
# Health check
curl http://localhost:8000/health

# Test PDF upload
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@test.pdf" \
  -F "page_number=1"
```

## API Compatibility

### Analyze Endpoint

**Prototype expects:**
- POST `/api/v1/analyze`
- Body: `{ image: base64, pageNumber: int, excludeTerms: string[] }`
- Response: Streaming AgentPackets (newline-delimited JSON)

**Backend provides:**
- POST `/api/v1/analyze`
- Supports both:
  - PDF upload: `multipart/form-data` with `file` and `page_number`
  - Image base64: JSON body with `image`, `pageNumber`, `excludeTerms`
- Response: Streaming AgentPackets ✅

### WebSocket

**Prototype expects:**
- WebSocket: `ws://localhost:8001/api/v1/ws/{document_id}`
- Messages: AgentPacket format

**Backend provides:**
- WebSocket: `ws://localhost:8000/api/v1/ws/{document_id}` ✅
- Messages: AgentPacket format ✅

## AgentPacket Format

The backend now returns AgentPackets matching the prototype exactly:

```json
{
  "sender": "HARVESTER",
  "recipient": "",
  "intent": "GRAPH_UPDATE",
  "content": {
    "concept": {
      "id": "uuid",
      "term": "GDPR",
      "type": "concept",
      "dataType": "legal",
      "category": "Regulation",
      "explanation": "...",
      "confidence": 0.95,
      "ui_group": "General"
    },
    "log": "Extracted concept: GDPR"
  }
}
```

## Frontend Changes Needed

### 1. Update BackendApiService URL

```typescript
// In src/services/backend-api.service.ts
private coordinatorUrl = signal<string>('http://localhost:8000');  // Changed from 4000
private wsUrl = signal<string>('ws://localhost:8000');  // Changed from 4001
```

### 2. Update analyzePageStream Method

The method should work as-is, but verify it:
- Sends POST to `/api/v1/analyze`
- Sends JSON body with `image`, `pageNumber`, `excludeTerms`
- Parses streaming response as AgentPackets

### 3. Update WebSocket Connection

```typescript
// WebSocket URL should be:
const wsUrl = `ws://localhost:8000/api/v1/ws/${documentId}`;
```

## Testing

### 1. Test Backend Standalone

```bash
# Start backend
cd backend-python
./start_services.sh

# Test endpoint
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"image": "base64data...", "pageNumber": 1}'
```

### 2. Test Frontend Connection

1. Start backend: `cd backend-python && ./start_services.sh`
2. Open frontend in browser
3. Upload a PDF or load from URL
4. Verify concepts appear in graph

## Troubleshooting

### CORS Issues

If you see CORS errors, ensure backend has CORS enabled:

```python
# In app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### WebSocket Connection Failed

- Verify backend is running: `curl http://localhost:8000/health`
- Check WebSocket URL matches: `ws://localhost:8000/api/v1/ws/{document_id}`
- Check browser console for errors

### No Concepts Extracted

- Check backend logs: `tail -f backend-python/logs/app.log`
- Verify gateway is running: `curl http://localhost:8080/health`
- Check concept extraction is working: Test with a simple PDF

## Next Steps

1. ✅ Backend returns AgentPacket format
2. ✅ WebSocket sends AgentPacket format
3. ⏳ Update frontend to use correct URLs
4. ⏳ Test end-to-end workflow
5. ⏳ Add OCR support for image-based analysis (future)

## Status

**Backend**: ✅ Ready for frontend integration  
**Frontend**: ⏳ Needs URL updates  
**Integration**: ⏳ Ready to test

# MVP Status & Quick Start

## ✅ MVP Complete - Ready for Testing

All core MVP features have been implemented and are ready for testing.

## What's Built

### ✅ Phase 1: Foundation
- [x] Python project structure
- [x] FastAPI application
- [x] Cognizant proxy integration
- [x] PostgreSQL models and database setup
- [x] Docker Compose for PostgreSQL
- [x] Alembic migrations

### ✅ Phase 2: Core Features
- [x] PDF upload endpoint (`POST /api/v1/analyze`)
- [x] PDF processing (text extraction)
- [x] HARVESTER agent (concept extraction)
- [x] Concept storage (PostgreSQL)
- [x] Concept query endpoints (`GET /api/v1/concepts`)

### ✅ Phase 3: Visualization
- [x] Graph endpoint (`GET /api/v1/graph`)
- [x] WebSocket endpoint (`/api/v1/ws/{document_id}`)
- [x] Real-time concept updates

## Quick Start (5 minutes)

### 1. Setup Environment

```bash
cd backend-python

# Run setup script
./setup_mvp.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Cognizant LLM Gateway

The gateway must be running before starting the MVP backend.

```bash
cd /Users/markforster/cognizant-llm-gateway
python -m clg.server
```

See `GATEWAY_SETUP.md` for detailed gateway setup.

### 3. Configure Environment

Edit `.env` file:
```bash
COGNIZANT_LLM_GATEWAY_URL=http://localhost:8080
LLM_MODEL=gpt-4-turbo-preview
POSTGRES_URL=postgresql://pdf_tagger:pdf_tagger_dev@localhost:5432/pdf_tagger_mvp
```

### 4. Start PostgreSQL

```bash
docker-compose -f docker-compose.mvp.yml up -d
```

### 5. Run Migrations

```bash
alembic upgrade head
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

## API Endpoints

### Analysis
- `POST /api/v1/analyze` - Upload PDF and extract concepts
- `GET /api/v1/analyze/{document_id}/status` - Get analysis status

### Concepts
- `GET /api/v1/concepts` - List concepts (with filtering)
- `GET /api/v1/concepts/{id}` - Get single concept

### Graph
- `GET /api/v1/graph` - Get graph data (nodes and edges)
- `GET /api/v1/graph/paths` - Find paths between nodes

### WebSocket
- `WS /api/v1/ws/{document_id}` - Real-time updates

## Testing

```bash
# Run unit tests
pytest tests/test_cognizant_proxy.py -v

# Run integration tests (requires DB)
pytest tests/test_integration.py -v

# Run all tests
pytest
```

## Example Usage

### 1. Upload PDF and Extract Concepts

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@sample.pdf" \
  -F "page_number=1"
```

Response:
```json
{
  "document_id": "uuid",
  "concepts": [
    {
      "id": "uuid",
      "term": "GDPR",
      "type": "concept",
      "confidence": 0.95,
      "assessment": "usually_true"
    }
  ],
  "total_concepts": 1
}
```

### 2. Query Concepts

```bash
curl http://localhost:8000/api/v1/concepts?document_id={document_id}
```

### 3. Get Graph Data

```bash
curl http://localhost:8000/api/v1/graph?document_id={document_id}
```

### 4. Connect WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/{document_id}');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'concept_extracted') {
    console.log('New concept:', data.data);
  }
};
```

## Architecture

```
┌─────────────┐
│   FastAPI   │
│   Server    │
└──────┬──────┘
       │
       ├─── POST /api/v1/analyze
       │    └─── PDF Processor (pdfplumber)
       │    └─── HARVESTER Agent
       │         └─── Cognizant Proxy LLM
       │    └─── PostgreSQL (store concepts)
       │    └─── WebSocket (broadcast updates)
       │
       ├─── GET /api/v1/concepts
       │    └─── PostgreSQL (query concepts)
       │
       ├─── GET /api/v1/graph
       │    └─── PostgreSQL (query nodes & edges)
       │
       └─── WS /api/v1/ws/{document_id}
            └─── Real-time updates
```

## Next Steps (v1.0)

After MVP testing, expand to:
- Multi-agent workflow (ARCHITECT, CURATOR, CRITIC)
- Neo4j for graph relationships
- Pinecone for vector search
- RAG pipeline
- Domain model matching
- Full frontend
- Advanced features (hooks, hypotheses, etc.)

## Troubleshooting

See `TESTING.md` for troubleshooting guide.

## Success Criteria

MVP is successful when:
- ✅ Can upload PDF and extract concepts
- ✅ Concepts stored in PostgreSQL
- ✅ Can query concepts via API
- ✅ Graph endpoint returns nodes and edges
- ✅ WebSocket sends real-time updates
- ✅ Cognizant proxy integration working
- ✅ Tests passing

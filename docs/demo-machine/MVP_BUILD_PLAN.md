# MVP Build Plan

> **Status**: Ready to Build  
> **Version**: 1.0.0  
> **Date**: 2026-01-11  
> **Goal**: Get working MVP first, then expand functionality

## MVP Scope

### Core MVP Features (Must Have)

1. **PDF Upload & Processing**
   - Upload PDF file
   - Extract text and basic structure
   - Process one page at a time

2. **Basic Concept Extraction**
   - Extract concepts using HARVESTER agent
   - Store concepts in database
   - Display concepts in UI

3. **Graph Visualization**
   - D3.js force-directed graph
   - Display concepts as nodes
   - Real-time updates via WebSocket

4. **Cognizant Proxy Integration**
   - Use Cognizant proxy for all LLM calls
   - Configure proxy endpoint
   - Handle proxy authentication

5. **Basic API**
   - POST /api/v1/analyze - Analyze PDF page
   - GET /api/v1/concepts - List concepts
   - GET /api/v1/graph - Get graph data
   - WebSocket /ws - Real-time updates

### MVP Out of Scope (Defer to v1.0)

- ❌ Full multi-agent workflow (just HARVESTER for MVP)
- ❌ Domain model matching
- ❌ RAG pipeline
- ❌ Full Neo4j/Pinecone integration (use PostgreSQL only)
- ❌ Hypotheses/claims
- ❌ Reality priors
- ❌ Advanced hook system
- ❌ Frontend (use API testing tools for MVP)

## MVP Architecture

### Simplified Stack

**Backend**:
- FastAPI (Python)
- PostgreSQL (single database for MVP)
- LangChain (for LLM integration)
- Cognizant Proxy (for LLM calls)

**Not in MVP**:
- Neo4j (use PostgreSQL relationships)
- Pinecone (use PostgreSQL full-text search)
- Elasticsearch (use PostgreSQL)
- Redis (use in-memory caching)
- Full LangGraph workflow (simple sequential processing)

### Database Schema (MVP)

**Simplified Tables**:
- `documents` - PDF documents
- `concepts` - Extracted concepts
- `relationships` - Concept relationships (stored in PostgreSQL, not Neo4j)

## Build Phases

### Phase 1: Foundation (Day 1-2)
- Set up project structure
- Configure Cognizant proxy
- Set up PostgreSQL
- Create basic FastAPI app
- Health check endpoint

### Phase 2: Core Features (Day 3-4)
- PDF upload endpoint
- PDF processing (text extraction)
- HARVESTER agent (basic concept extraction)
- Concept storage in PostgreSQL
- Basic concept query endpoint

### Phase 3: Visualization (Day 5)
- Graph endpoint
- WebSocket setup
- Basic D3.js visualization (if time permits)

### Phase 4: Testing & Polish (Day 6-7)
- Unit tests
- Integration tests
- API testing
- Bug fixes
- Documentation

## Cognizant Proxy Configuration

### Environment Variables

```bash
# Cognizant Proxy Configuration
COGNIZANT_PROXY_ENDPOINT=https://your-cognizant-proxy.com/api/v1/llm
COGNIZANT_PROXY_API_KEY=your_proxy_api_key
COGNIZANT_PROXY_TIMEOUT=60000

# LLM Provider (via proxy)
LLM_PROVIDER=openai  # or anthropic, google
LLM_MODEL=gpt-4-turbo-preview  # or claude-3-opus, gemini-pro

# Database
POSTGRES_URL=postgresql://user:pass@localhost:5432/pdf_tagger_mvp

# Server
API_PORT=8000
```

### Proxy Integration Pattern

```python
# app/services/llm_service.py
import httpx
from typing import Optional

class CognizantProxyLLM:
    """LLM service using Cognizant proxy"""
    
    def __init__(self):
        self.proxy_endpoint = os.getenv("COGNIZANT_PROXY_ENDPOINT")
        self.proxy_api_key = os.getenv("COGNIZANT_PROXY_API_KEY")
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.model = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    
    async def call(self, messages: List[Dict], **kwargs):
        """Call LLM via Cognizant proxy"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.proxy_endpoint}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.proxy_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "provider": self.provider,
                    "model": self.model,
                    "messages": messages,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json()
```

## Testing Strategy

### Unit Tests
- Test concept extraction logic
- Test database operations
- Test proxy integration
- Test data models

### Integration Tests
- Test API endpoints
- Test database connections
- Test proxy calls
- Test WebSocket connections

### API Tests
- Test PDF upload
- Test concept extraction
- Test concept queries
- Test graph endpoint

### Test Tools
- pytest (Python)
- httpx (API testing)
- pytest-asyncio (async tests)

## Success Criteria

### MVP is Complete When:

- [ ] Can upload PDF and extract concepts
- [ ] Concepts stored in PostgreSQL
- [ ] Can query concepts via API
- [ ] Cognizant proxy integration working
- [ ] Basic graph visualization (if time permits)
- [ ] Unit tests passing (>70% coverage)
- [ ] Integration tests passing
- [ ] API tests passing
- [ ] Documentation complete

## Next Steps After MVP

1. Add ARCHITECT agent (domain creation)
2. Add CURATOR agent (taxonomy building)
3. Add Neo4j for graph relationships
4. Add Pinecone for vector search
5. Add RAG pipeline
6. Add full frontend
7. Add advanced features (hooks, hypotheses, etc.)

## Risk Mitigation

### Risks
- Proxy integration issues → Test proxy early
- Database setup complexity → Use Docker Compose
- LLM rate limits → Implement retry logic
- Time constraints → Focus on core features only

### Mitigation
- Test proxy connection on Day 1
- Use Docker for easy database setup
- Implement exponential backoff for retries
- Defer non-essential features to v1.0

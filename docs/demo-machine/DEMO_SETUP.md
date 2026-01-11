# Demo Machine Setup Guide

## Quick Start (30 minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Step 1: Clone and Setup (5 min)

```bash
# Clone repository
git clone <repo-url>
cd pdf-concept-tagger

# Set up backend
cd backend-python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up frontend
cd ../frontend-react
npm install
```

### Step 2: Configure Environment (5 min)

**Backend `.env`:**
```bash
# LLM APIs
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key  # Optional
PROXY_API_ENDPOINT=http://localhost:3000/api/v1/analyze  # If using proxy

# Databases
POSTGRES_URL=postgresql://user:pass@localhost:5432/pdf_tagger
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-east1-gcp
REDIS_URL=redis://localhost:6379
ELASTICSEARCH_URL=http://localhost:9200

# Server
API_PORT=8000
WS_PORT=8001
```

**Frontend `.env`:**
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8001
```

### Step 3: Start Databases (10 min)

**Option A: Docker Compose (Recommended)**
```bash
docker-compose up -d
```

**Option B: Managed Services**
- PostgreSQL: Use managed service (Railway, Supabase, etc.)
- Neo4j: Create Neo4j Aura instance (free tier available)
- Pinecone: Create Pinecone account (free tier available)
- Redis: Use managed service or Docker
- Elasticsearch: Use managed service or Docker

### Step 4: Initialize Databases (5 min)

```bash
cd backend-python

# Run migrations
alembic upgrade head

# Initialize Neo4j
python scripts/init_neo4j.py

# Initialize Pinecone
python scripts/init_pinecone.py

# Initialize Elasticsearch
python scripts/init_elasticsearch.py
```

### Step 5: Start Services (5 min)

**Terminal 1 - Backend:**
```bash
cd backend-python
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend-react
npm run dev
```

### Step 6: Test (5 min)

1. Open http://localhost:5173 (or Vite port)
2. Upload a test PDF
3. Verify extraction works
4. Check graph visualization

## Detailed Setup

### Database Setup

#### PostgreSQL
```bash
# Local
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=pdf_tagger \
  -p 5432:5432 \
  postgres:15

# Or use managed service (Railway, Supabase, etc.)
```

#### Neo4j Aura
1. Go to https://neo4j.com/cloud/aura/
2. Create free instance
3. Copy connection URI and credentials
4. Add to `.env`

#### Pinecone
1. Go to https://www.pinecone.io/
2. Create free account
3. Create index (dimension: 1536 for OpenAI embeddings)
4. Copy API key and environment
5. Add to `.env`

#### Redis
```bash
# Local
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine

# Or use managed service
```

#### Elasticsearch
```bash
# Local
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.11.0

# Or use managed service (Elastic Cloud)
```

## Development Workflow

### Backend Development

```bash
cd backend-python
source venv/bin/activate

# Run with hot reload
uvicorn app.main:app --reload

# Run tests
pytest

# Run linting
ruff check .
black .

# Run type checking
mypy app/
```

### Frontend Development

```bash
cd frontend-react

# Run dev server
npm run dev

# Run tests
npm test

# Run linting
npm run lint

# Build for production
npm run build
```

### Agent Development

```bash
cd backend-python

# Test individual agent
python -m pytest tests/test_agents/test_harvester.py

# Test agent workflow
python -m pytest tests/test_chains/test_extraction_chain.py

# Run agent interactively
python scripts/test_agent.py harvester
```

## Experimentation Features

### Prompt Experimentation

1. **Edit Prompts**: Edit files in `backend-python/prompts/`
2. **Test Prompt**: Use `/api/v1/prompts/experiment` endpoint
3. **Compare Versions**: UI shows prompt performance metrics
4. **A/B Test**: Run multiple prompt versions simultaneously

### Model Switching

1. **Configure Models**: Edit `backend-python/app/services/llm_service.py`
2. **Switch Provider**: Change `DEFAULT_LLM_PROVIDER` in config
3. **Compare Models**: UI shows model performance comparison
4. **Cost Tracking**: Monitor API costs per model

### Domain Model Testing

1. **Load Domain Models**: Place JSON files in `backend-python/domain_models/`
2. **Test Matching**: Upload document, see domain detection
3. **View Schema**: UI shows detected domain schemas
4. **Validate Mapping**: Check extracted data against schema

### Tool Use Testing

1. **Create Tools**: Add tools in `backend-python/app/agents/tools/`
2. **Test Tools**: Use LangSmith to debug tool execution
3. **Monitor Usage**: UI shows tool usage statistics
4. **Optimize Tools**: Refine based on usage patterns

## Troubleshooting

### Common Issues

**Database Connection Errors**
- Check `.env` credentials
- Verify databases are running
- Test connections: `python scripts/test_connections.py`

**LLM API Errors**
- Verify API keys are set
- Check API quotas/limits
- Test API: `python scripts/test_llm.py`

**Frontend Not Connecting**
- Check `VITE_API_URL` in frontend `.env`
- Verify backend is running on correct port
- Check CORS settings in backend

**Agent Not Working**
- Check LangChain/LangGraph versions
- Verify prompt templates exist
- Check agent logs: `tail -f logs/agents.log`

## Performance Tuning

### Database Optimization

```sql
-- PostgreSQL indexes
CREATE INDEX idx_concepts_term ON concepts(term);
CREATE INDEX idx_concepts_type ON concepts(type);
CREATE INDEX idx_concepts_search ON concepts USING GIN(search_vector);

-- Neo4j indexes
CREATE INDEX concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;
```

### Caching

```python
# Redis caching for frequent queries
@cache(ttl=3600)
async def get_concept(id: str):
    ...
```

### Vector Search Optimization

```python
# Pinecone index settings
index_config = {
    "metric": "cosine",
    "dimension": 1536,
    "pods": 1,
    "replicas": 1
}
```

## Production Deployment

### Backend (Railway/Vercel/Render)

```bash
# Railway
railway login
railway init
railway up

# Set environment variables in Railway dashboard
# Deploy automatically on git push
```

### Frontend (Vercel)

```bash
# Vercel
vercel login
vercel --prod

# Set environment variables in Vercel dashboard
```

### Databases

- **PostgreSQL**: Use managed service (Railway, Supabase, Neon)
- **Neo4j**: Use Neo4j Aura (managed)
- **Pinecone**: Use Pinecone cloud (managed)
- **Redis**: Use managed service (Upstash, Railway)
- **Elasticsearch**: Use Elastic Cloud (managed)

## Monitoring

### LangSmith (Agent Monitoring)

```python
# Set in .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=pdf-concept-tagger
```

### Application Monitoring

- **Backend**: Use FastAPI monitoring (Prometheus, Grafana)
- **Frontend**: Use Sentry for error tracking
- **Databases**: Use database-specific monitoring

## Next Steps

1. **Set up development environment** (follow Quick Start)
2. **Load sample documents** for testing
3. **Experiment with prompts** using prompt editor
4. **Test different models** (OpenAI, Claude, Gemini)
5. **Try domain models** with sample documents
6. **Explore visualizations** and UI components

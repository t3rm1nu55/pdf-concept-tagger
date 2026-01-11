# PDF Concept Tagger - From Scratch Architecture

## Overview

This document outlines the optimal architecture for building PDF Concept Tagger from scratch using modern best practices and technologies.

## Technology Stack

### Frontend
- **React 18+** with **Vite** - Fast, modern, excellent DX
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling, rapid UI development
- **D3.js** - Graph visualization (keep existing)
- **Zustand** or **Jotai** - Lightweight state management
- **React Query (TanStack Query)** - Server state management, caching
- **Zod** - Runtime type validation

### Backend
- **Python 3.11+** - Best ecosystem for AI/ML, NLP, PDF processing
- **FastAPI** - Modern, fast, async Python web framework
- **Pydantic** - Data validation (similar to Zod)
- **Celery** - Distributed task queue for agent processing
- **Redis** - Message broker, caching, session storage
- **WebSockets** - Real-time updates (FastAPI native support)

### AI/ML Stack
- **LangChain** - Agent orchestration framework
- **LangGraph** - Multi-agent workflows
- **OpenAI/Anthropic/Gemini APIs** - LLM providers
- **Docling** - Advanced PDF parsing (as mentioned in requirements)
- **spaCy** or **NLTK** - NLP preprocessing
- **Sentence Transformers** - Embeddings for semantic search

### Storage & Databases

#### Primary Database
- **PostgreSQL 15+** - Relational data (concepts, relationships, metadata)
  - Full-text search capabilities
  - JSONB for flexible schema
  - Excellent for structured ontology data

#### Graph Database
- **Neo4j** or **Amazon Neptune** - Native graph storage
  - Perfect for knowledge graphs
  - Cypher query language
  - Built-in graph algorithms
  - Better than storing graphs in PostgreSQL

#### Vector Database (for semantic search)
- **Pinecone** or **Weaviate** or **Qdrant** - Vector embeddings
  - Semantic similarity search
  - Concept clustering
  - Related concept discovery

#### Object Storage
- **S3-compatible** (AWS S3, MinIO, Cloudflare R2) - PDF files, images
  - Scalable file storage
  - CDN integration
  - Versioning support

#### Caching
- **Redis** - Hot data caching, session storage
- **CDN** (Cloudflare/CloudFront) - Static assets, API responses

### Indexing & Search
- **Elasticsearch** or **OpenSearch** - Full-text search, faceted search
  - Search across concepts, relationships, documents
  - Aggregations and analytics
  - Real-time indexing

### Infrastructure
- **Docker** & **Docker Compose** - Local development
- **Kubernetes** (production) - Container orchestration
- **Terraform** - Infrastructure as code
- **GitHub Actions** - CI/CD

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                   │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   React App  │  │  Tailwind UI │  │   D3 Graph   │     │
│  │   (Vite)     │  │   Components │  │ Visualization│     │
│  └──────┬───────┘  └──────────────┘  └──────────────┘     │
│         │                                                      │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │  React Query (TanStack Query)                        │   │
│  │  - API state management                              │   │
│  │  - Caching & invalidation                            │   │
│  │  - Optimistic updates                                │   │
│  └──────┬──────────────────────────────────────────────┘   │
│         │                                                      │
│         │ HTTP/WebSocket                                      │
└─────────┼────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway / Load Balancer                     │
│              (Nginx / Traefik / AWS ALB)                    │
└─────────┬────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend Services (FastAPI)                      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Service (FastAPI)                               │  │
│  │  - REST endpoints                                    │  │
│  │  - WebSocket handlers                                │  │
│  │  - Authentication (JWT/OAuth)                       │  │
│  └──────┬──────────────────────────────────────────────┘  │
│         │                                                      │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │  Agent Orchestration (LangChain/LangGraph)          │   │
│  │  - HARVESTER agent                                  │   │
│  │  - ARCHITECT agent                                  │   │
│  │  - CURATOR agent                                    │   │
│  │  - CRITIC agent                                     │   │
│  │  - OBSERVER agent                                  │   │
│  └──────┬──────────────────────────────────────────────┘   │
│         │                                                      │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │  Task Queue (Celery + Redis)                        │   │
│  │  - Async agent processing                           │   │
│  │  - Task distribution                                │   │
│  │  - Retry logic                                      │   │
│  └──────┬──────────────────────────────────────────────┘   │
└─────────┼────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Layer                                      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Neo4j     │  │   Vector DB  │     │
│  │  - Concepts  │  │  - Graph      │  │  - Embeddings│     │
│  │  - Metadata  │  │  - Relations │  │  - Semantic  │     │
│  │  - Users     │  │  - Paths     │  │    Search    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Elasticsearch│  │     Redis     │  │      S3      │     │
│  │  - Full-text │  │  - Cache     │  │  - PDFs      │     │
│  │  - Search    │  │  - Sessions  │  │  - Images    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Component Architecture

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Tailwind UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Modal.tsx
│   │   ├── graph/           # D3 graph components
│   │   │   ├── GraphView.tsx
│   │   │   ├── Node.tsx
│   │   │   └── Edge.tsx
│   │   ├── pdf/             # PDF viewer
│   │   │   └── PDFViewer.tsx
│   │   └── concepts/        # Concept management
│   │       ├── ConceptList.tsx
│   │       └── ConceptInspector.tsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useGraph.ts
│   │   ├── useConcepts.ts
│   │   └── useWebSocket.ts
│   ├── services/
│   │   ├── api.ts           # API client (React Query)
│   │   ├── websocket.ts     # WebSocket client
│   │   └── storage.ts       # IndexedDB wrapper
│   ├── stores/              # Zustand stores
│   │   ├── graphStore.ts
│   │   └── uiStore.ts
│   ├── types/               # TypeScript types
│   │   └── index.ts
│   ├── utils/
│   │   └── validation.ts    # Zod schemas
│   └── App.tsx
├── public/
├── tailwind.config.js
├── vite.config.ts
└── package.json
```

### Backend Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── analyze.py
│   │   │   │   ├── concepts.py
│   │   │   │   └── graph.py
│   │   │   └── router.py
│   │   └── websocket.py
│   ├── agents/
│   │   ├── base.py          # Base agent class
│   │   ├── harvester.py
│   │   ├── architect.py
│   │   ├── curator.py
│   │   ├── critic.py
│   │   └── observer.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py      # DB connections
│   │   └── security.py
│   ├── models/              # Pydantic models
│   │   ├── concept.py
│   │   ├── graph.py
│   │   └── agent.py
│   ├── services/
│   │   ├── pdf_service.py   # PDF processing
│   │   ├── llm_service.py    # LLM integration
│   │   ├── graph_service.py  # Graph operations
│   │   └── search_service.py # Elasticsearch
│   ├── tasks/               # Celery tasks
│   │   └── agent_tasks.py
│   └── main.py              # FastAPI app
├── alembic/                 # Database migrations
├── tests/
├── requirements.txt
└── Dockerfile
```

## Database Schema Design

### PostgreSQL Schema

```sql
-- Concepts table
CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term TEXT NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'concept' | 'hypernode'
    data_type VARCHAR(50), -- 'entity' | 'date' | 'location' | ...
    category TEXT,
    explanation TEXT,
    confidence DECIMAL(3,2),
    bounding_box JSONB,
    ui_group TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(term, '') || ' ' || 
                   coalesce(explanation, ''))
    ) STORED
);

CREATE INDEX idx_concepts_search ON concepts USING GIN(search_vector);
CREATE INDEX idx_concepts_type ON concepts(type);
CREATE INDEX idx_concepts_ui_group ON concepts(ui_group);

-- Relationships table
CREATE TABLE relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    target_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    predicate TEXT NOT NULL,
    type VARCHAR(50), -- 'structural' | 'semantic' | 'hyperlink'
    weight DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_id, target_id, predicate)
);

CREATE INDEX idx_relationships_source ON relationships(source_id);
CREATE INDEX idx_relationships_target ON relationships(target_id);

-- Domains table
CREATE TABLE domains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    sensitivity VARCHAR(20), -- 'LOW' | 'MEDIUM' | 'HIGH'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Taxonomies table
CREATE TABLE taxonomies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    child_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL, -- 'is_a' | 'part_of'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(parent_id, child_id, type)
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    page_count INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Document pages table
CREATE TABLE document_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    s3_key TEXT NOT NULL,
    processed_at TIMESTAMP,
    concepts_extracted INTEGER DEFAULT 0,
    UNIQUE(document_id, page_number)
);
```

### Neo4j Graph Schema

```cypher
// Concept nodes
CREATE CONSTRAINT concept_id IF NOT EXISTS
FOR (c:Concept) REQUIRE c.id IS UNIQUE;

// Domain nodes
CREATE CONSTRAINT domain_id IF NOT EXISTS
FOR (d:Domain) REQUIRE d.id IS UNIQUE;

// Relationships
(:Concept)-[:RELATED_TO {predicate: string, weight: float}]->(:Concept)
(:Concept)-[:IS_A]->(:Domain)
(:Concept)-[:IS_A]->(:Concept)
(:Concept)-[:PART_OF]->(:Concept)
```

## Key Technology Choices Rationale

### React + Vite vs Angular
**React + Vite wins:**
- ✅ Faster build times (Vite is much faster than Angular CLI)
- ✅ Smaller bundle size
- ✅ Better ecosystem for data visualization
- ✅ More flexible, less opinionated
- ✅ Better TypeScript integration
- ✅ Easier to find React developers

### Python vs Node.js Backend
**Python wins:**
- ✅ Best AI/ML libraries (LangChain, spaCy, transformers)
- ✅ Better PDF processing (PyPDF2, pdfplumber, Docling)
- ✅ Superior NLP capabilities
- ✅ Better data science tooling
- ✅ More mature agent frameworks (LangChain, AutoGen)
- ✅ Better async support (FastAPI + asyncio)

### Tailwind CSS
**Why Tailwind:**
- ✅ Rapid UI development
- ✅ Consistent design system
- ✅ Small production bundle (purging unused styles)
- ✅ Excellent developer experience
- ✅ Great for dashboards and data visualization UIs

### PostgreSQL + Neo4j vs Single Database
**Why Both:**
- **PostgreSQL**: Structured data, full-text search, ACID transactions
- **Neo4j**: Native graph operations, graph algorithms, relationship queries
- **Best of both worlds**: Use PostgreSQL for structured data, Neo4j for graph operations

### Vector Database
**Why Vector DB:**
- Semantic similarity search for concepts
- Concept clustering and grouping
- Finding related concepts even without explicit relationships
- Better than traditional keyword search

### Elasticsearch
**Why Elasticsearch:**
- Full-text search across all concepts, relationships, documents
- Faceted search and aggregations
- Real-time indexing
- Advanced query capabilities

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
1. Set up React + Vite + Tailwind frontend
2. Set up FastAPI backend with basic endpoints
3. PostgreSQL database setup
4. Basic PDF upload and storage (S3)

### Phase 2: Core Features (Weeks 3-4)
1. PDF processing with Docling
2. Basic concept extraction (HARVESTER agent)
3. D3.js graph visualization
4. Concept storage in PostgreSQL

### Phase 3: Agent System (Weeks 5-6)
1. LangChain/LangGraph integration
2. Multi-agent orchestration
3. Celery task queue setup
4. WebSocket real-time updates

### Phase 4: Graph & Search (Weeks 7-8)
1. Neo4j integration
2. Graph operations and queries
3. Elasticsearch setup
4. Full-text search implementation

### Phase 5: Advanced Features (Weeks 9-10)
1. Vector database integration
2. Semantic search
3. Advanced graph algorithms
4. Performance optimization

## Example Stack Comparison

| Component | Current (Angular/Node) | From Scratch (React/Python) |
|-----------|----------------------|---------------------------|
| Frontend | Angular 20 | React 18 + Vite |
| Styling | Tailwind (CDN) | Tailwind CSS (bundled) |
| Backend | Node.js/Express | Python/FastAPI |
| Agents | Custom | LangChain/LangGraph |
| Graph DB | IndexedDB (browser) | Neo4j (server) |
| Vector DB | None | Pinecone/Weaviate |
| Search | None | Elasticsearch |
| Storage | IndexedDB | PostgreSQL + S3 |
| Task Queue | None | Celery + Redis |

## Migration Path

If migrating from current architecture:

1. **Keep frontend running** (Angular) while building React frontend
2. **Build Python backend** alongside Node.js backend
3. **Migrate data** from IndexedDB to PostgreSQL/Neo4j
4. **Switch frontend** to React when ready
5. **Decommission** Node.js backend

## Cost Considerations

### Development
- **React**: Faster development, larger talent pool
- **Python**: Better AI/ML tooling, easier agent development

### Infrastructure
- **PostgreSQL**: Free (self-hosted) or managed ($20-200/month)
- **Neo4j**: Free (community) or Aura ($65+/month)
- **Elasticsearch**: Free (self-hosted) or managed ($95+/month)
- **Vector DB**: Pinecone free tier, then $70+/month
- **S3**: Pay per use (~$0.023/GB storage)

### Total Estimated Monthly Cost (Small Scale)
- Managed PostgreSQL: $50
- Neo4j Aura: $65
- Elasticsearch: $95
- Pinecone: $70
- S3: $10-50 (depending on usage)
- **Total: ~$290-330/month**

Self-hosted option: ~$50-100/month (VPS costs)

## Conclusion

**Recommended From-Scratch Stack:**
- **Frontend**: React + Vite + Tailwind + D3.js
- **Backend**: Python + FastAPI + LangChain
- **Databases**: PostgreSQL + Neo4j + Vector DB + Elasticsearch
- **Infrastructure**: Docker + Kubernetes (production)

This stack provides:
- ✅ Best-in-class AI/ML capabilities
- ✅ Scalable architecture
- ✅ Modern developer experience
- ✅ Production-ready infrastructure
- ✅ Excellent performance and maintainability


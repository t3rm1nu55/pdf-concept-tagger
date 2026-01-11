# Demo Machine Architecture

## Overview

The demo machine is a **production-like but simplified** system that:
- Uses real data and real backends
- Implements proper agent frameworks (LangChain/LangGraph)
- Uses production databases (PostgreSQL, Neo4j, Vector DB)
- Includes RAG pipeline for semantic search
- Has a polished frontend
- Makes design assumptions that can be swapped later
- Focuses on best-in-class tools over pure OSS

## Technology Stack (Best-in-Class Focus)

### Backend Framework
- **Python 3.11+** with **FastAPI** - Best async Python framework
- **LangChain** + **LangGraph** - Industry-standard agent orchestration
- **Pydantic** - Best data validation

### Agent Framework
- **LangChain Agents** - Multi-agent coordination
- **LangGraph** - State machine for agent workflows
- **LangSmith** (optional) - Monitoring and debugging

### Databases
- **PostgreSQL 15+** - Primary relational database (best open-source RDBMS)
- **Neo4j Aura** - Graph database (managed, best graph DB)
- **Pinecone** - Vector database (best managed vector DB, free tier available)
- **Redis** - Caching and message broker

### Search & Indexing
- **Elasticsearch** (managed) or **OpenSearch** - Full-text search
- **Pinecone** - Vector embeddings for semantic search
- **PostgreSQL Full-Text Search** - Basic search

### PDF Processing
- **Docling** (preferred) - Best PDF processing library
- **pdfplumber** (fallback) - Good OSS alternative
- **PyPDF2** - Basic PDF operations

### LLM Integration
- **LangChain LLM abstractions** - Support multiple providers
- **OpenAI GPT-4** (primary) - Best overall model
- **Anthropic Claude** (secondary) - Best for long context
- **Google Gemini** (via proxy) - Cost-effective vision
- **LangChain Tool Use** - Function calling framework

### RAG Pipeline
- **LangChain RAG** - Document loading and chunking
- **LangChain Embeddings** - Text embeddings
- **Pinecone** - Vector storage and retrieval
- **LangChain Retrievers** - Hybrid search (vector + keyword)

### Frontend
- **React 18 + Vite** - Fastest development
- **TypeScript** - Type safety
- **Tailwind CSS** - Rapid UI development
- **D3.js** - Graph visualization
- **React Query (TanStack Query)** - Server state management
- **Zustand** - Client state management

### Infrastructure
- **Docker** + **Docker Compose** - Local development
- **Vercel** (frontend) or **Railway** (full stack) - Easy deployment
- **GitHub Actions** - CI/CD

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  React App   │  │  Tailwind UI │  │   D3 Graph   │    │
│  │   (Vite)     │  │   Components │  │ Visualization│    │
│  └──────┬───────┘  └──────────────┘  └──────────────┘    │
│         │                                                      │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │  React Query (API Client)                           │   │
│  │  WebSocket Client (Real-time)                       │   │
│  └──────┬──────────────────────────────────────────────┘   │
└─────────┼────────────────────────────────────────────────────┘
          │ HTTP/WebSocket
          ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  REST API Endpoints                                   │  │
│  │  - POST /api/v1/analyze                               │  │
│  │  - GET  /api/v1/concepts                              │  │
│  │  - GET  /api/v1/graph                                 │  │
│  │  - POST /api/v1/prompts/experiment                    │  │
│  └──────┬──────────────────────────────────────────────┘  │
│  ┌──────▼──────────────────────────────────────────────┐  │
│  │  WebSocket Handler (Real-time updates)              │  │
│  └──────┬──────────────────────────────────────────────┘  │
└─────────┼────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│         Agent Orchestration (LangChain/LangGraph)           │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  LangGraph State Machine                             │ │
│  │  - HARVESTER Agent (LangChain Agent)                │ │
│  │  - ARCHITECT Agent (LangChain Agent)                │ │
│  │  - CURATOR Agent (LangChain Agent)                  │ │
│  │  - CRITIC Agent (LangChain Agent)                   │ │
│  │  - OBSERVER Agent (LangChain Agent)                 │ │
│  └──────┬──────────────────────────────────────────────┘ │
│  ┌──────▼──────────────────────────────────────────────┐  │
│  │  LangChain Tools                                    │  │
│  │  - PDF Processing Tool                             │  │
│  │  - Domain Model Tool                               │  │
│  │  - Graph Update Tool                               │  │
│  │  - RAG Retrieval Tool                              │  │
│  └──────┬──────────────────────────────────────────────┘  │
└─────────┼────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              RAG Pipeline (LangChain)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Document    │  │  Embeddings  │  │   Retrieval  │     │
│  │  Loader      │→ │  Generator   │→ │   (Hybrid)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────┬────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Layer                                      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Neo4j     │  │   Pinecone   │     │
│  │  - Concepts  │  │  - Graph     │  │  - Vectors   │     │
│  │  - Metadata  │  │  - Relations │  │  - Semantic  │     │
│  │  - Full-text │  │  - Paths     │  │    Search   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Elasticsearch│  │     Redis     │                        │
│  │  - Search    │  │  - Cache      │                        │
│  │  - Indexing  │  │  - Sessions   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services                               │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Proxy API    │  │  LLM APIs    │                        │
│  │ (Gemini)     │  │  (OpenAI/    │                        │
│  │              │  │   Claude)    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Demo Machine Design Assumptions

### Assumptions (Can Be Swapped Later)

1. **Agent Framework**: LangChain/LangGraph (can swap to AutoGen, CrewAI)
2. **Graph DB**: Neo4j Aura (can swap to ArangoDB, Amazon Neptune)
3. **Vector DB**: Pinecone (can swap to Weaviate, Qdrant)
4. **Primary LLM**: OpenAI GPT-4 (can swap to Claude, Gemini)
5. **PDF Processing**: Docling preferred, pdfplumber fallback
6. **Frontend**: React + Vite (can swap to Angular, Vue)
7. **Deployment**: Vercel + Railway (can swap to AWS, GCP)

### Design Decisions (Best-in-Class)

1. **LangChain** - Industry standard, best ecosystem
2. **Neo4j** - Best graph database, managed service
3. **Pinecone** - Best managed vector DB, easy to use
4. **FastAPI** - Best async Python framework
5. **React + Vite** - Fastest development, best ecosystem
6. **PostgreSQL** - Best open-source RDBMS
7. **Elasticsearch** - Best full-text search

## Component Architecture

### Backend Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── analyze.py          # PDF analysis endpoint
│   │   │   │   ├── concepts.py         # Concept queries
│   │   │   │   ├── graph.py            # Graph queries
│   │   │   │   └── prompts.py          # Prompt experimentation
│   │   │   └── router.py
│   │   └── websocket.py                # Real-time updates
│   ├── agents/
│   │   ├── base.py                     # Base LangChain agent
│   │   ├── harvester.py                # HARVESTER agent
│   │   ├── architect.py                # ARCHITECT agent
│   │   ├── curator.py                  # CURATOR agent
│   │   ├── critic.py                   # CRITIC agent
│   │   └── observer.py                 # OBSERVER agent
│   ├── chains/
│   │   ├── extraction_chain.py         # LangChain extraction chain
│   │   ├── domain_matching_chain.py    # Domain model matching
│   │   └── rag_chain.py                # RAG retrieval chain
│   ├── graph/
│   │   ├── langgraph_state.py          # LangGraph state definition
│   │   └── workflow.py                  # Agent workflow
│   ├── services/
│   │   ├── pdf_service.py              # PDF processing (Docling)
│   │   ├── llm_service.py              # LLM abstraction
│   │   ├── rag_service.py              # RAG pipeline
│   │   ├── graph_service.py            # Neo4j operations
│   │   ├── vector_service.py           # Pinecone operations
│   │   └── search_service.py           # Elasticsearch
│   ├── models/                         # Pydantic models
│   │   ├── concept.py
│   │   ├── document.py
│   │   └── agent.py
│   ├── database/                       # Database connections
│   │   ├── postgres.py
│   │   ├── neo4j.py
│   │   └── redis.py
│   └── main.py                         # FastAPI app
├── prompts/                            # Prompt templates
│   ├── harvester_prompt.txt
│   ├── architect_prompt.txt
│   ├── curator_prompt.txt
│   └── domain_matching_prompt.txt
├── domain_models/                      # Domain model definitions
│   ├── microsoft_cdm.json
│   ├── accounting.json
│   └── trade.json
└── requirements.txt
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                         # Tailwind UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Modal.tsx
│   │   ├── graph/                      # D3 graph components
│   │   │   ├── GraphView.tsx
│   │   │   ├── Node.tsx
│   │   │   └── Edge.tsx
│   │   ├── pdf/                        # PDF viewer
│   │   │   └── PDFViewer.tsx
│   │   ├── concepts/                   # Concept management
│   │   │   ├── ConceptList.tsx
│   │   │   └── ConceptInspector.tsx
│   │   └── prompts/                   # Prompt experimentation
│   │       ├── PromptEditor.tsx
│   │       └── PromptTester.tsx
│   ├── hooks/
│   │   ├── useGraph.ts
│   │   ├── useConcepts.ts
│   │   ├── usePrompts.ts
│   │   └── useWebSocket.ts
│   ├── services/
│   │   ├── api.ts                      # React Query setup
│   │   ├── websocket.ts
│   │   └── storage.ts
│   ├── stores/                         # Zustand stores
│   │   ├── graphStore.ts
│   │   └── uiStore.ts
│   └── App.tsx
├── tailwind.config.js
├── vite.config.ts
└── package.json
```

## Key Features for Experimentation

### 1. Prompt Experimentation System
- Store prompts in files/database
- Version control for prompts
- A/B testing framework
- Prompt performance metrics
- Easy prompt swapping

### 2. Model Switching
- Support multiple LLM providers
- Easy model configuration
- Model comparison tools
- Cost tracking per model

### 3. Domain Model Integration
- Load domain models from JSON
- Automatic domain detection
- Schema mapping visualization
- Domain model performance tracking

### 4. Tool Use Framework
- LangChain tools for agent actions
- Custom tool creation
- Tool execution logging
- Tool performance metrics

### 5. Visual Structures
- Multiple graph layouts (force, hierarchical, circular)
- Interactive node/edge editing
- Filter and search in graph
- Export graph visualizations

### 6. Display Structures
- Multiple view modes (graph, list, table, timeline)
- Customizable dashboards
- Responsive layouts
- Theme switching

## Demo Machine Requirements

### Hardware Requirements

**Minimum (Local Development):**
- CPU: 4 cores
- RAM: 16GB
- Storage: 50GB SSD
- Network: Broadband internet

**Recommended (Demo Server):**
- CPU: 8 cores
- RAM: 32GB
- Storage: 100GB SSD
- Network: High-speed internet

### Software Requirements

**Development:**
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

**Services (Managed/Cloud):**
- PostgreSQL (managed or local)
- Neo4j Aura (cloud)
- Pinecone (cloud)
- Elasticsearch (managed or local)
- Redis (managed or local)

### API Keys Required

- OpenAI API key (or Anthropic/Google)
- Neo4j Aura credentials
- Pinecone API key
- Proxy API endpoint (if using)

## Refactoring Plan

### Current State Analysis

**Existing Code:**
- Angular frontend (browser-based)
- Node.js backend (simple coordinator)
- Custom agent implementation
- IndexedDB storage
- Direct Gemini API calls

**What to Keep:**
- Frontend UI concepts and layouts
- Graph visualization approach (D3.js)
- Agent packet protocol (concept)
- Basic extraction logic

**What to Replace:**
- Angular → React (faster dev, better ecosystem)
- Node.js agents → Python LangChain agents
- IndexedDB → PostgreSQL + Neo4j
- Custom coordination → LangGraph
- Direct API → Proxy + LangChain abstractions

### Refactoring Strategy

**Phase 1: Backend Foundation**
1. Set up Python FastAPI backend
2. Integrate LangChain/LangGraph
3. Set up databases (PostgreSQL, Neo4j, Pinecone)
4. Create basic agent structure

**Phase 2: Agent Migration**
1. Convert HARVESTER to LangChain agent
2. Convert ARCHITECT to LangChain agent
3. Convert CURATOR to LangChain agent
4. Set up LangGraph workflow

**Phase 3: Frontend Migration**
1. Create React frontend
2. Port graph visualization
3. Port UI components
4. Integrate with new backend

**Phase 4: Advanced Features**
1. Add RAG pipeline
2. Add domain model integration
3. Add prompt experimentation
4. Add tool use framework

## Task Breakdown with Dependencies

See TASKS.md for detailed task breakdown.

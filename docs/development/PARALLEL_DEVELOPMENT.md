# Parallel Development Plan

## Overview

Two development tracks running in parallel:
- **Track 1: Minimal Experimentation Backend** (Option 1) - Fast iteration, immediate use
- **Track 2: Full Demo Machine** (Option 2) - Production-like, comprehensive

Both tracks share interfaces and can merge later.

## Track 1: Minimal Experimentation Backend

**Goal**: Get something working in 1 day for immediate experimentation

**Timeline**: Week 1 (can start immediately)

**Structure**: `experiment-backend/`

**Features**:
- ✅ FastAPI backend
- ✅ LangChain LLM integration
- ✅ Multiple model support (OpenAI, Anthropic, Google)
- ✅ Prompt experimentation API
- ✅ Model switching
- ✅ Streaming responses
- ✅ Simple in-memory storage
- ✅ WebSocket support

**What to Experiment With**:
- Prompts (edit in code or via API)
- Models (switch providers)
- Extraction techniques
- Domain model matching (basic)
- Visual structures (via API responses)

**Dependencies**: None (can start immediately)

## Track 2: Full Demo Machine

**Goal**: Production-like system with proper architecture

**Timeline**: Weeks 1-9 (follows TASKS.md)

**Structure**: `backend-python/` (full implementation)

**Features**:
- ✅ LangChain/LangGraph agents
- ✅ PostgreSQL + Neo4j + Pinecone
- ✅ RAG pipeline
- ✅ Domain model integration
- ✅ Tool use framework
- ✅ Full frontend (React)
- ✅ Production-ready

**Dependencies**: Follows TASKS.md dependency chain

## Parallel Development Strategy

### Week 1: Foundation (Both Tracks)

**Track 1 (Experiment)**:
- Day 1: Set up minimal backend ✅
- Day 2: Add prompt experimentation UI
- Day 3: Add model switching UI
- Day 4: Test with real documents
- Day 5: Document findings

**Track 2 (Full Demo)**:
- Week 1: Set up databases, basic services (T1.1-T1.7, T2.1-T2.4)
- Can run parallel to Track 1

### Week 2-3: Agent Development

**Track 1 (Experiment)**:
- Add basic LangChain agents (simplified)
- Test agent coordination
- Experiment with prompts per agent
- Document what works

**Track 2 (Full Demo)**:
- Implement full LangChain/LangGraph agents (T3.1-T3.8)
- Set up proper state machine
- Integrate with databases

### Week 4+: Integration

**Track 1 Learnings → Track 2**:
- Validated prompts → Use in Track 2
- Working techniques → Implement properly
- Model preferences → Configure in Track 2
- UI patterns → Port to React frontend

**Track 2 Features → Track 1**:
- Database services → Can add to Track 1
- Agent patterns → Can simplify for Track 1
- RAG pipeline → Can add basic version to Track 1

## Shared Interfaces

### API Contract
Both tracks use same API contract:
```typescript
POST /api/v1/analyze
GET /api/v1/concepts
GET /api/v1/graph
POST /api/v1/prompts/experiment
```

### Data Models
Shared Pydantic models in `shared/models/`:
- `Concept`
- `AgentPacket`
- `Document`
- `Relationship`

### Prompt Templates
Shared prompt templates in `shared/prompts/`:
- Both tracks can use/contribute
- Version controlled
- A/B tested

## Coordination

### Daily Sync
- Track 1: Share what works, what doesn't
- Track 2: Share architecture decisions
- Both: Coordinate on shared interfaces

### Weekly Review
- Review Track 1 learnings
- Incorporate into Track 2 design
- Update shared components
- Plan next week

### Code Sharing
- Shared models: `shared/`
- Shared utilities: `shared/utils/`
- Shared prompts: `shared/prompts/`
- Track-specific: `experiment-backend/` vs `backend-python/`

## Migration Path

**Track 1 → Track 2**:
1. Keep Track 1 running for experimentation
2. Port validated features to Track 2
3. Gradually migrate users
4. Decommission Track 1 when Track 2 ready

**Or Merge**:
- Track 1 becomes "experimentation mode" in Track 2
- Same codebase, different configuration
- Experiment mode: in-memory, simplified
- Production mode: full databases, agents

## Getting Started

### Track 1: Start Now (10 minutes)
```bash
cd experiment-backend
pip install -r requirements.txt
cp .env.example .env
# Add API keys
python server.py
```

### Track 2: Start Week 1
```bash
# Follow DEMO_SETUP.md
# Start with T1.1-T1.7 (foundation tasks)
```

## Benefits

1. **Immediate Value**: Track 1 provides working system day 1
2. **Risk Reduction**: Track 1 validates assumptions early
3. **Parallel Progress**: Both tracks advance simultaneously
4. **Knowledge Sharing**: Learnings flow between tracks
5. **Flexible Migration**: Can merge or keep separate

# What's Next - Development Roadmap

## ✅ Current Status: MVP Backend Complete

**What's Done:**
- ✅ FastAPI backend with all core endpoints
- ✅ Cognizant LLM Gateway integration
- ✅ PostgreSQL database with migrations
- ✅ PDF processing and concept extraction (HARVESTER agent)
- ✅ Graph endpoint and WebSocket support
- ✅ Comprehensive test suite
- ✅ Documentation and setup scripts

**What's Missing (vs Prototype):**
- ⏳ **AgentPacket protocol format** (prototype expects specific structure)
- ⏳ **ARCHITECT agent** (domains)
- ⏳ **CURATOR agent** (taxonomies)
- ⏳ **CRITIC agent** (hypotheses)
- ⏳ **Missing data models** (Domain, Taxonomy, Hypothesis, Prior)
- ⏳ **Frontend integration** (Angular frontend exists but needs API format match)

**See**: `PROTOTYPE_ALIGNMENT.md` for detailed gap analysis

---

## 🎯 Immediate Next Steps (Choose Your Path)

### Option 1: Align Backend with Prototype ⭐ **CRITICAL - Do First**

**Goal**: Make existing Angular frontend work with FastAPI backend

**Problem**: Prototype expects AgentPacket format, but MVP returns different format

**Steps:**
1. **Fix API Response Format** (2-4 hours)
   - Update `/api/v1/analyze` to return AgentPacket format
   - Match prototype's expected structure:
     ```json
     {
       "sender": "HARVESTER",
       "intent": "GRAPH_UPDATE",
       "content": {
         "concept": { "id", "term", "type", "ui_group", ... }
       }
     }
     ```

2. **Add Missing Data Models** (2-3 hours)
   - Create Domain, Taxonomy, Hypothesis, Prior models
   - Add database migrations
   - See `PROTOTYPE_ALIGNMENT.md` for details

3. **Update WebSocket Format** (1-2 hours)
   - Send AgentPacket format via WebSocket
   - Match prototype's streaming expectations

4. **Add Basic Agent Stubs** (3-4 hours)
   - Create ARCHITECT, CURATOR, CRITIC agents (minimal)
   - Return appropriate AgentPackets (can be empty for now)

5. **Test Frontend Connection** (1-2 hours)
   - Connect Angular frontend to FastAPI backend
   - Verify graph visualization works
   - Test real-time updates

**Time**: 1 day  
**Outcome**: Working frontend connected to backend

**See**: `PROTOTYPE_ALIGNMENT.md` for detailed gap analysis

---

### Option 2: Build Frontend UI 🎨

**Goal**: Create a user interface to interact with the system

**You Have Two Choices:**

#### A. Port Existing Angular Frontend (Faster) ⚠️ **Requires Backend Alignment First**
- **Location**: `src/` directory (Angular 20+)
- **Status**: Already has D3.js graph, PDF viewer, concept display
- **Task**: Connect it to new FastAPI backend instead of Gemini API
- **Time**: 4-8 hours (after backend alignment)
- **Pros**: UI already exists, just needs API integration
- **Cons**: Angular (vs React in design)

**Prerequisites**: Complete Option 1 first (align backend with prototype)

**Steps:**
1. ✅ Backend returns AgentPacket format (from Option 1)
2. Update Angular `BackendApiService` to call FastAPI endpoints
3. Update WebSocket URL to `ws://localhost:8000/api/v1/ws/{document_id}`
4. Test end-to-end workflow
5. Verify graph visualization works

#### B. Build New React Frontend (Better Long-term)
- **Design**: React + Vite + Tailwind + D3.js (per DESIGN.md)
- **Status**: Not started
- **Task**: Build from scratch matching DESIGN.md UX spec
- **Time**: 2-3 days
- **Pros**: Modern stack, matches design, better DX
- **Cons**: More work upfront

**Steps:**
1. Set up React + Vite project
2. Create components (PDF upload, graph viewer, concept list)
3. Integrate D3.js for graph visualization
4. Connect to FastAPI backend
5. Add real-time WebSocket updates

**Recommendation**: Start with Option A (port Angular) to get something working quickly, then build React version later.

---

### Option 3: Expand Backend Features 🚀

**Goal**: Add more agents and advanced features

**Next Features to Add:**

1. **ARCHITECT Agent** (Week 2)
   - Domain model creation
   - Structure analysis
   - Relationship inference
   - **Time**: 1-2 days

2. **CURATOR Agent** (Week 3)
   - Taxonomy building
   - Concept organization
   - Quality validation
   - **Time**: 1-2 days

3. **Neo4j Integration** (Week 4)
   - Move relationships to Neo4j
   - Graph queries
   - Path finding
   - **Time**: 2-3 days

4. **RAG Pipeline** (Week 5)
   - Vector embeddings
   - Pinecone integration
   - Semantic search
   - **Time**: 2-3 days

5. **Domain Model Matching** (Week 6)
   - Microsoft CDM integration
   - Accounting models
   - Automatic matching
   - **Time**: 3-4 days

**See**: `docs/demo-machine/TASKS.md` for detailed task breakdown

---

## 📋 Recommended Development Order

### Phase 1: Align Backend with Prototype (This Week) ⭐ **CRITICAL**
1. ✅ Backend complete (basic structure)
2. ⏳ **Fix API format to match AgentPacket protocol** (2-4 hours)
3. ⏳ **Add missing data models** (Domain, Taxonomy, Hypothesis, Prior) (2-3 hours)
4. ⏳ **Update WebSocket format** (1-2 hours)
5. ⏳ **Add basic agent stubs** (ARCHITECT, CURATOR, CRITIC) (3-4 hours)
6. ⏳ **Test with Angular frontend** (1-2 hours)

**Outcome**: Working frontend connected to backend

### Phase 2: Implement Real Agents (Next Week)
1. Implement ARCHITECT agent (domain detection)
2. Implement CURATOR agent (taxonomy building)
3. Add bounding box extraction
4. Improve UI group assignment
5. Test full workflow (upload → extract → visualize)

**Outcome**: Feature parity with prototype

### Phase 3: Expand Features (Weeks 3-9)
1. Implement CRITIC agent (hypotheses)
2. Implement OBSERVER agent
3. Integrate Neo4j
4. Add RAG pipeline
5. Add domain model matching
6. Add advanced features (hooks, optimization, etc.)

---

## 🛠️ Quick Start Commands

### Test Backend Now
```bash
# 1. Start gateway
cd /Users/markforster/cognizant-llm-gateway
python -m clg.server

# 2. Start backend (in another terminal)
cd backend-python
./start_services.sh

# 3. Test API
curl http://localhost:8000/health
```

### Port Angular Frontend
```bash
# 1. Update API service URLs
# Edit src/services/backend-api.service.ts
# Change API endpoint to http://localhost:8000/api/v1

# 2. Update WebSocket URL
# Change WebSocket endpoint to ws://localhost:8000/api/v1/ws

# 3. Test locally
# Open index.html in browser or use local server
```

### Build React Frontend
```bash
# 1. Create React project
cd frontend-react
npm create vite@latest . -- --template react-ts

# 2. Install dependencies
npm install d3 @tanstack/react-query axios

# 3. Start dev server
npm run dev
```

---

## 🎯 Success Criteria

### MVP Validation Complete When:
- [ ] Can upload PDF via API
- [ ] Concepts extracted correctly
- [ ] Concepts stored in database
- [ ] Can query concepts via API
- [ ] Graph endpoint returns data
- [ ] WebSocket sends real-time updates
- [ ] No critical bugs

### Frontend Complete When:
- [ ] Can upload PDF via UI
- [ ] See concepts in graph visualization
- [ ] Real-time updates work
- [ ] Can query/filter concepts
- [ ] UI is responsive and usable

### Full Demo Complete When:
- [ ] All agents working (HARVESTER, ARCHITECT, CURATOR)
- [ ] Neo4j integrated
- [ ] RAG pipeline working
- [ ] Domain model matching working
- [ ] Frontend fully functional
- [ ] End-to-end tests passing

---

## 📚 Reference Documents

- **MVP Status**: `backend-python/MVP_STATUS.md`
- **Design**: `docs/demo-machine/DESIGN.md`
- **Tasks**: `docs/demo-machine/TASKS.md`
- **Architecture**: `docs/demo-machine/DEMO_ARCHITECTURE.md`
- **Requirements**: `REQUIREMENTS.md`

---

## 💡 Questions to Consider

1. **Do you want to test the backend first?** → Option 1
2. **Do you want a UI now?** → Option 2A (port Angular) or 2B (build React)
3. **Do you want more features?** → Option 3
4. **What's your priority?** → Choose based on your needs

---

**Recommendation**: Start with **Option 1** (test backend) to ensure everything works, then move to **Option 2A** (port Angular) to get a UI quickly. This gives you a working system in 1-2 days, then you can expand features incrementally.

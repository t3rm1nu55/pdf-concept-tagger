# Prototype Alignment Check

## Prototype Features Analysis

### ✅ What Prototype Has (Angular Frontend)

**Agents:**
- HARVESTER ✅ (extracts concepts)
- ARCHITECT ⏳ (creates domains)
- CURATOR ⏳ (builds taxonomies)
- CRITIC ⏳ (generates hypotheses, optimizations)
- OBSERVER ⏳ (monitoring)

**Data Structures:**
- **Concepts** ✅ (terms, types, ui_group, bounding boxes)
- **Relationships** ✅ (source, target, predicate, type)
- **Domains** ⏳ (ARCHITECT creates - hub nodes like "Legal", "Financial")
- **Taxonomies** ⏳ (CURATOR creates - hierarchical "is_a", "part_of" links)
- **Hypotheses** ⏳ (CRITIC creates - claims with evidence)
- **Priors** ⏳ (Reality priors/axioms - context knowledge)
- **Hypernodes** ⏳ (Grouping concepts)

**UI Features:**
- D3.js force-directed graph ✅
- PDF viewer with bounding boxes ✅
- Concept locker (sidebar list) ✅
- Inspector (detail view) ✅
- Real-time streaming updates ✅
- Agent status display ✅
- Log viewer ✅
- Hypotheses panel ⏳
- Context/priors panel ⏳

**Protocol:**
- AgentPacket format ✅ (sender, intent, content)
- Streaming via WebSocket ✅
- IndexedDB persistence ✅

---

## MVP Backend Status

### ✅ What MVP Backend Has

**Agents:**
- HARVESTER ✅ (basic concept extraction)

**Data Structures:**
- Concepts ✅ (stored in PostgreSQL)
- Relationships ✅ (stored in PostgreSQL)
- Documents ✅ (PDF metadata)

**API:**
- POST /api/v1/analyze ✅ (PDF upload)
- GET /api/v1/concepts ✅ (query concepts)
- GET /api/v1/graph ✅ (get nodes/edges)
- WebSocket /api/v1/ws/{document_id} ✅ (real-time updates)

**Missing:**
- ARCHITECT agent (domains)
- CURATOR agent (taxonomies)
- CRITIC agent (hypotheses)
- OBSERVER agent
- Domains table/model
- Taxonomies table/model
- Hypotheses table/model
- Priors table/model
- AgentPacket protocol matching
- Streaming response format

---

## Alignment Gaps

### 🔴 Critical Gaps (Block Frontend Integration)

1. **AgentPacket Protocol Mismatch**
   - **Prototype expects**: `{ sender, intent, content: { concept?, domain?, taxonomy?, hypothesis?, prior?, relationship? } }`
   - **MVP returns**: Simple concept objects
   - **Fix**: Update analyze endpoint to return AgentPacket format

2. **Missing Agents**
   - ARCHITECT, CURATOR, CRITIC, OBSERVER not implemented
   - **Fix**: Add basic implementations or mock responses

3. **Missing Data Models**
   - Domains, Taxonomies, Hypotheses, Priors not in database
   - **Fix**: Add models and migrations

4. **Streaming Format**
   - **Prototype expects**: Server-Sent Events (SSE) or WebSocket with AgentPacket format
   - **MVP has**: WebSocket but different message format
   - **Fix**: Update WebSocket to send AgentPacket format

### 🟡 Important Gaps (Features Missing)

5. **Bounding Boxes**
   - Prototype displays bounding boxes on PDF
   - MVP doesn't extract or store bounding box coordinates
   - **Fix**: Add bounding box extraction to HARVESTER

6. **UI Groups**
   - Prototype organizes concepts by `ui_group` (folders in Locker)
   - MVP stores `ui_group` but doesn't populate it intelligently
   - **Fix**: Improve HARVESTER to assign meaningful ui_groups

7. **Round Management**
   - Prototype tracks rounds (Auto-Harvest, etc.)
   - MVP doesn't have round concept
   - **Fix**: Add round tracking to backend

### 🟢 Nice-to-Have (Can Add Later)

8. **Optimization Scores**
   - CRITIC provides optimization suggestions
   - Not critical for MVP

9. **Advanced Agent Coordination**
   - Prototype has agent coordinator service
   - MVP has simple sequential processing
   - Can enhance later

---

## Recommended Fix Priority

### Phase 1: Make Frontend Work (Critical - 1-2 days)

1. **Update API Response Format** 🔴
   - Change `/api/v1/analyze` to return AgentPacket format
   - Match prototype's expected structure
   - **Time**: 2-4 hours

2. **Add Missing Data Models** 🔴
   - Create Domain, Taxonomy, Hypothesis, Prior models
   - Add migrations
   - **Time**: 2-3 hours

3. **Update WebSocket Format** 🔴
   - Send AgentPacket format via WebSocket
   - Match prototype's streaming expectations
   - **Time**: 1-2 hours

4. **Add Basic Agent Stubs** 🟡
   - Create ARCHITECT, CURATOR, CRITIC agents (minimal implementations)
   - Return appropriate AgentPackets
   - **Time**: 3-4 hours

**Total**: ~1 day to get frontend working

### Phase 2: Enhance Features (Important - 1 week)

5. **Implement ARCHITECT Agent** 🟡
   - Domain detection and creation
   - **Time**: 1-2 days

6. **Implement CURATOR Agent** 🟡
   - Taxonomy building
   - **Time**: 1-2 days

7. **Add Bounding Box Extraction** 🟡
   - Extract coordinates from PDF
   - Store in concept.source_location
   - **Time**: 1 day

8. **Improve UI Group Assignment** 🟡
   - Better categorization
   - **Time**: 1 day

### Phase 3: Full Feature Parity (Future)

9. **Implement CRITIC Agent**
10. **Implement OBSERVER Agent**
11. **Add Round Management**
12. **Add Optimization Scoring**

---

## Updated WHAT_NEXT.md Recommendations

### Immediate Priority: Frontend Integration

**Before building new features, get the existing Angular frontend working:**

1. **Fix API Format** (2-4 hours)
   - Update analyze endpoint to return AgentPacket format
   - Match prototype's expectations exactly

2. **Add Missing Models** (2-3 hours)
   - Domain, Taxonomy, Hypothesis, Prior models
   - Database migrations

3. **Update WebSocket** (1-2 hours)
   - Send AgentPacket format
   - Match prototype's streaming

4. **Test Frontend** (1-2 hours)
   - Connect Angular frontend to FastAPI backend
   - Verify graph visualization works
   - Test real-time updates

**Total**: ~1 day to get working frontend

### Then Expand Features

Once frontend works, add:
- ARCHITECT agent (domains)
- CURATOR agent (taxonomies)
- Bounding boxes
- Better UI groups

---

## Action Items

### For Frontend Integration (Do First)

- [ ] Update `analyze.py` to return AgentPacket format
- [ ] Add Domain, Taxonomy, Hypothesis, Prior models
- [ ] Create migrations for new models
- [ ] Update WebSocket to send AgentPacket format
- [ ] Add basic ARCHITECT/CURATOR stubs (can return empty for now)
- [ ] Test Angular frontend connection

### For Feature Parity (Do Next)

- [ ] Implement ARCHITECT agent (domain detection)
- [ ] Implement CURATOR agent (taxonomy building)
- [ ] Add bounding box extraction
- [ ] Improve UI group assignment
- [ ] Add round tracking

### For Full Demo (Future)

- [ ] Implement CRITIC agent
- [ ] Implement OBSERVER agent
- [ ] Add optimization scoring
- [ ] Add advanced agent coordination

---

## Conclusion

**Current State**: MVP backend has core concept extraction but doesn't match prototype's AgentPacket protocol or data structures.

**Recommendation**: 
1. **First**: Fix API format and add missing models (1 day) → Get frontend working
2. **Then**: Add ARCHITECT and CURATOR agents (1 week) → Feature parity
3. **Finally**: Add advanced features → Full demo

**Priority**: Frontend integration > Feature expansion > Advanced features

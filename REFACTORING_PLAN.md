# Refactoring Plan: Current to Demo Machine

## Current Architecture Analysis

### What We Have
- **Frontend**: Angular 20+ (browser-based, IndexedDB)
- **Backend**: Node.js coordinator with custom agents
- **Agents**: Custom JavaScript implementations
- **Storage**: IndexedDB (browser)
- **API**: Direct Gemini API calls
- **Visualization**: D3.js graph

### What We Need
- **Frontend**: React + Vite (modern, fast)
- **Backend**: Python FastAPI (best for AI/ML)
- **Agents**: LangChain/LangGraph (industry standard)
- **Storage**: PostgreSQL + Neo4j + Pinecone (production databases)
- **API**: Proxy + LangChain abstractions
- **Visualization**: D3.js (keep, port to React)

## Refactoring Strategy

### Phase 1: Parallel Development (Weeks 1-3)
**Strategy**: Build new system alongside old, don't break existing

1. **Create New Backend** (`backend-python/`)
   - Set up FastAPI structure
   - Implement core services
   - Keep old backend running

2. **Create New Frontend** (`frontend-react/`)
   - Set up React + Vite
   - Port UI components
   - Keep old frontend running

3. **Data Migration Tools**
   - Create export from IndexedDB
   - Create import to PostgreSQL/Neo4j
   - Test migration process

### Phase 2: Feature Parity (Weeks 4-6)
**Strategy**: Match existing features in new stack

1. **Core Features**
   - PDF upload and processing
   - Entity extraction
   - Graph visualization
   - Concept display

2. **Agent Features**
   - HARVESTER agent
   - ARCHITECT agent
   - CURATOR agent

3. **UI Features**
   - Document viewer
   - Graph explorer
   - Concept inspector
   - Search functionality

### Phase 3: Migration (Week 7)
**Strategy**: Switch over with minimal downtime

1. **Data Migration**
   - Export all data from old system
   - Import to new databases
   - Verify data integrity

2. **Deployment**
   - Deploy new backend
   - Deploy new frontend
   - Set up redirects

3. **Validation**
   - Test all features
   - Compare outputs
   - Fix any issues

### Phase 4: Decommission (Week 8)
**Strategy**: Remove old code after validation

1. **Archive Old Code**
   - Move to `archive/` directory
   - Document what was kept/changed
   - Keep for reference

2. **Clean Up**
   - Remove unused dependencies
   - Update documentation
   - Update README

## Code Mapping

### Frontend Components

| Current (Angular) | New (React) | Notes |
|-------------------|-------------|-------|
| `app.component.ts` | `App.tsx` | Main app component |
| `locker.component.ts` | `ConceptList.tsx` | Concept list view |
| `inspector.component.ts` | `ConceptInspector.tsx` | Concept detail view |
| `graph.service.ts` | `GraphView.tsx` + hooks | Graph visualization |
| `gemini.service.ts` | `api.ts` (React Query) | API client |
| `storage.service.ts` | `api.ts` (backend handles) | Storage moved to backend |
| `log.service.ts` | `api.ts` + WebSocket | Logs via backend |

### Backend Services

| Current (Node.js) | New (Python) | Notes |
|-------------------|--------------|-------|
| `coordinator.js` | `main.py` (FastAPI) | Main API server |
| `agents/harvester.js` | `agents/harvester.py` (LangChain) | LangChain agent |
| `agents/architect.js` | `agents/architect.py` (LangChain) | LangChain agent |
| `agents/curator.js` | `agents/curator.py` (LangChain) | LangChain agent |
| `shared/message-bus.js` | LangGraph state machine | Built into LangGraph |
| `shared/agent-base.js` | LangChain base agent | Use LangChain base |

### Data Models

| Current (IndexedDB) | New (Databases) | Notes |
|---------------------|-----------------|-------|
| `nodes` store | PostgreSQL `concepts` table | Relational data |
| `edges` store | Neo4j relationships | Graph data |
| `domains` store | PostgreSQL `domains` table | Relational data |
| `taxonomies` store | Neo4j taxonomy relationships | Graph data |
| `hypotheses` store | PostgreSQL `hypotheses` table | Relational data |
| Concept embeddings | Pinecone vectors | Vector search |

## Migration Scripts

### Export from Current System

```javascript
// export-data.js
// Run in browser console or Node.js
async function exportData() {
  const data = {
    concepts: await getAllFromIndexedDB('nodes'),
    relationships: await getAllFromIndexedDB('edges'),
    domains: await getAllFromIndexedDB('domains'),
    taxonomies: await getAllFromIndexedDB('taxonomies'),
    hypotheses: await getAllFromIndexedDB('hypotheses')
  };
  
  // Save to JSON file
  downloadJSON(data, 'exported-data.json');
}
```

### Import to New System

```python
# import-data.py
# Python script to import exported data
import json
from app.database.postgres import ConceptService
from app.database.neo4j import GraphService

async def import_data(json_file):
    with open(json_file) as f:
        data = json.load(f)
    
    # Import concepts to PostgreSQL
    for concept in data['concepts']:
        await ConceptService.create(concept)
    
    # Import relationships to Neo4j
    for rel in data['relationships']:
        await GraphService.create_relationship(rel)
    
    # Import domains, taxonomies, hypotheses...
```

## Key Differences

### Agent Communication

**Current**: Custom message bus with AgentPacket
**New**: LangGraph state machine with LangChain messages

**Migration**: Map AgentPacket to LangGraph state

### Storage

**Current**: Browser IndexedDB (client-side)
**New**: Server-side databases (PostgreSQL, Neo4j, Pinecone)

**Migration**: Export IndexedDB → Import to databases

### API

**Current**: Direct Gemini API calls from frontend
**New**: Backend API with proxy + LangChain abstractions

**Migration**: Update frontend to call new API endpoints

### State Management

**Current**: Angular signals + services
**New**: React Query + Zustand

**Migration**: Port state logic to React patterns

## Risk Mitigation

### Data Loss Prevention
- Export all data before migration
- Keep old system running during migration
- Verify data integrity after migration
- Keep backups

### Feature Regression
- Create feature comparison checklist
- Test all features in new system
- Keep old system available for comparison
- Document any missing features

### User Impact
- Run systems in parallel initially
- Gradual migration (feature by feature)
- Clear communication about changes
- Rollback plan ready

## Rollback Plan

If migration fails:
1. Revert to old frontend deployment
2. Keep old backend running
3. Restore data from backups
4. Document issues
5. Fix and retry

## Success Criteria

- [ ] All data migrated successfully
- [ ] All features working in new system
- [ ] Performance equal or better
- [ ] No data loss
- [ ] Users can use new system
- [ ] Old system decommissioned

# PDF Concept Tagger - System Architecture

## Overview

The PDF Concept Tagger uses a **multi-agent backend architecture** where each agent runs as a separate process, communicating via a message bus. This provides better scalability, fault tolerance, and separation of concerns compared to a monolithic browser-based approach.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Angular)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ AppComponent │  │ GraphService │  │ StorageService│     │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                      │
│         │ HTTP/WebSocket                                       │
└─────────┼────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Coordinator/Orchestrator (Express)             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Server (Port 4000)                              │  │
│  │  - POST /api/v1/analyze                               │  │
│  │  - GET /api/v1/agents                                 │  │
│  │  - GET /health                                         │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  WebSocket Server (Port 4001)                        │  │
│  │  - Real-time agent message updates                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────┬────────────────────────────────────────────────────┘
          │
          │ Message Bus
          │ (Memory/Redis/WebSocket)
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Processes                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  HARVESTER   │  │  ARCHITECT   │  │   CURATOR    │     │
│  │              │  │              │  │              │     │
│  │ - Extracts   │  │ - Defines    │  │ - Organizes  │     │
│  │   concepts   │  │   domains    │  │   taxonomies │     │
│  │ - Entities   │  │ - Creates    │  │ - Hierarchies│     │
│  │   from PDF   │  │   relations  │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │   CRITIC     │  │   OBSERVER   │                        │
│  │              │  │              │                        │
│  │ - Evaluates  │  │ - Monitors   │                        │
│  │   quality    │  │   system     │                        │
│  │ - Optimizes  │  │ - Explains   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────┬────────────────────────────────────────────────────┘
          │
          │ API Calls
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services                              │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Gemini API   │  │ Proxy API     │                        │
│  │ (via proxy)  │  │ (optional)    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Angular)

- **BackendApiService**: Communicates with coordinator via HTTP and WebSocket
- **GraphService**: Visualizes knowledge graph using D3.js
- **StorageService**: Persists data to IndexedDB
- **AppComponent**: Orchestrates UI and coordinates frontend services

### Backend Coordinator

- **Express API Server**: RESTful API for analysis requests
- **WebSocket Server**: Real-time updates to frontend
- **Message Bus**: Routes messages between agents
- **Agent Registry**: Tracks agent statuses and health

### Agent Processes

Each agent is a separate Node.js process:

1. **HARVESTER**: Extracts concepts from PDF pages
   - Uses Gemini API to analyze images
   - Outputs structured concept data
   - Handles exclusion lists to avoid duplicates

2. **ARCHITECT**: Defines domain structures
   - Analyzes extracted concepts
   - Creates domain definitions
   - Establishes semantic relationships

3. **CURATOR**: Organizes taxonomies
   - Links concepts to domains
   - Creates hierarchical relationships
   - Ensures ontological consistency

4. **CRITIC** (TODO): Evaluates graph quality
   - Scores graph completeness
   - Proposes optimizations
   - Validates hypotheses

5. **OBSERVER** (TODO): Monitors system
   - Tracks agent performance
   - Provides explainability
   - Generates insights

## Communication Flow

### Analysis Request Flow

1. **Frontend** → POST `/api/v1/analyze` with PDF page image
2. **Coordinator** → Creates new round, sends message to HARVESTER
3. **HARVESTER** → Extracts concepts, sends GRAPH_UPDATE packets
4. **Coordinator** → Collects concepts, sends to ARCHITECT
5. **ARCHITECT** → Defines domains/relationships, sends GRAPH_UPDATE packets
6. **Coordinator** → Sends concepts/domains to CURATOR
7. **CURATOR** → Creates taxonomies, sends GRAPH_UPDATE packets
8. **Coordinator** → Streams all packets to frontend
9. **Frontend** → Updates graph visualization in real-time

### Message Bus

Agents communicate via `AgentPacket` messages:

```typescript
{
  sender: 'HARVESTER',
  recipient: 'ORCHESTRATOR',
  intent: 'GRAPH_UPDATE',
  content: { concept: {...} },
  timestamp: '2024-01-01T00:00:00Z',
  correlationId: 'msg_123'
}
```

**Transport Options:**
- **Memory**: Single server, in-process (default)
- **Redis**: Distributed, multiple servers
- **WebSocket**: Browser clients

## Deployment

### Development

Single process (coordinator manages agents):
```bash
cd backend
npm run dev
```

### Production

Separate processes for scalability:
```bash
# Terminal 1: Coordinator
npm run coordinator

# Terminal 2-6: Agents
npm run agent:harvester
npm run agent:architect
npm run agent:curator
npm run agent:critic
npm run agent:observer
```

### Docker (Future)

Each agent can run in separate containers:
- `coordinator:latest`
- `agent-harvester:latest`
- `agent-architect:latest`
- etc.

## Benefits of Multi-Process Architecture

1. **Scalability**: Scale agents independently
2. **Fault Tolerance**: One agent failure doesn't crash the system
3. **Resource Management**: Distribute load across processes
4. **Development**: Easier to develop/test agents independently
5. **Deployment**: Deploy agents to different servers/regions
6. **Monitoring**: Track individual agent performance

## Future Enhancements

- [ ] Add CRITIC and OBSERVER agents
- [ ] Implement Redis message bus for distributed deployment
- [ ] Add agent health monitoring and auto-restart
- [ ] Implement task queue (Bull/Redis) for better task management
- [ ] Add agent load balancing
- [ ] Implement agent versioning and rolling updates
- [ ] Add distributed tracing (OpenTelemetry)


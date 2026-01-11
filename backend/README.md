# PDF Concept Tagger - Backend Service

Multi-agent backend system for PDF concept extraction and knowledge graph construction.

## Architecture

The backend consists of separate agent processes that communicate via a message bus:

- **Coordinator/Orchestrator**: Main API server that coordinates agents
- **HARVESTER**: Extracts concepts from PDF pages
- **ARCHITECT**: Defines domains and creates semantic relationships
- **CURATOR**: Organizes taxonomical hierarchies
- **CRITIC**: Evaluates graph quality (TODO)
- **OBSERVER**: Monitors system state (TODO)

## Setup

1. Install dependencies:
```bash
cd backend
npm install
```

2. Configure environment variables (create `.env`):
```bash
GEMINI_API_KEY=your_gemini_api_key
PROXY_API_ENDPOINT=http://localhost:3000/api/v1/analyze  # Optional
PORT=4000
WS_PORT=4001
MESSAGE_BUS_TRANSPORT=memory  # or 'redis' for distributed setup
REDIS_URL=redis://localhost:6379  # if using Redis
```

## Running

### Development Mode (Coordinator + Agents)

Run the coordinator which manages all agents:
```bash
npm run dev
```

### Production Mode (Separate Processes)

Run each agent as a separate process:

Terminal 1 - Coordinator:
```bash
npm run coordinator
```

Terminal 2 - Harvester:
```bash
npm run agent:harvester
```

Terminal 3 - Architect:
```bash
npm run agent:architect
```

Terminal 4 - Curator:
```bash
npm run agent:curator
```

## API Endpoints

### POST /api/v1/analyze
Analyze a PDF page and extract concepts.

**Request:**
```json
{
  "image": "base64_encoded_image",
  "pageNumber": 1,
  "excludeTerms": ["term1", "term2"]
}
```

**Response:** Streaming JSON (one packet per line)

### GET /health
Get system health and agent statuses.

### GET /api/v1/agents
Get status of all agents.

## WebSocket

Connect to `ws://localhost:4001` for real-time agent message updates.

## Message Bus

Agents communicate via a message bus. Supported transports:
- **memory**: In-process (default, single server)
- **redis**: Distributed (multiple servers)
- **websocket**: Browser clients

## Agent Communication

Agents communicate using `AgentPacket` format:
```json
{
  "sender": "HARVESTER",
  "recipient": "ORCHESTRATOR",
  "intent": "GRAPH_UPDATE",
  "content": { ... },
  "timestamp": "2024-01-01T00:00:00Z",
  "correlationId": "msg_123456"
}
```

## Development

### Adding a New Agent

1. Create `src/agents/your-agent.js`
2. Extend `BaseAgent` class
3. Implement agent-specific logic
4. Register in `coordinator.js`

### Message Bus Transport

To use Redis for distributed agents:
1. Install Redis: `brew install redis` (macOS) or `apt-get install redis` (Linux)
2. Start Redis: `redis-server`
3. Set `MESSAGE_BUS_TRANSPORT=redis` in `.env`


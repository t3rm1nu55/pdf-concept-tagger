<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# PDF Concept Tagger

A regulatory analysis tool that ingests PDFs, performs AI-powered analysis, and constructs a live knowledge graph of concepts, relationships, and hypotheses using a **multi-agent backend architecture**.

## Architecture

The system uses **separate agent processes** running on a Node.js backend:
- **HARVESTER**: Extracts concepts from PDF pages
- **ARCHITECT**: Defines domains and creates semantic relationships  
- **CURATOR**: Organizes taxonomical hierarchies
- **CRITIC**: Evaluates graph quality (TODO)
- **OBSERVER**: Monitors system state (TODO)

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### 1. Start Backend Services

```bash
# Install backend dependencies
cd backend
npm install

# Configure environment (create .env file)
cp .env.example .env
# Edit .env and set GEMINI_API_KEY

# Start coordinator (manages all agents)
npm run dev
```

The backend will start on:
- API Server: http://localhost:4000
- WebSocket Server: ws://localhost:4001

### 2. Start Frontend

```bash
# In project root
npm install
npm run dev
```

The frontend will connect to the backend automatically.

### Production Deployment (Separate Processes)

For production, run agents as separate processes:

```bash
# Terminal 1: Coordinator
npm run coordinator

# Terminal 2: Harvester Agent
npm run agent:harvester

# Terminal 3: Architect Agent  
npm run agent:architect

# Terminal 4: Curator Agent
npm run agent:curator
```

## Features

- **Multi-Agent Architecture**: Separate processes for each agent role
- **Message Bus Communication**: Agents communicate via message bus (memory/Redis)
- **Real-Time Updates**: WebSocket support for live agent updates
- **Streaming Analysis**: Real-time PDF analysis with streaming responses
- **Knowledge Graph**: Interactive D3.js visualization of extracted concepts
- **Persistence**: IndexedDB storage for concepts, relationships, and hypotheses

## Project Structure

```
├── backend/                 # Backend services
│   ├── src/
│   │   ├── agents/         # Individual agent processes
│   │   │   ├── harvester.js
│   │   │   ├── architect.js
│   │   │   └── curator.js
│   │   ├── shared/        # Shared utilities
│   │   │   ├── agent-base.js
│   │   │   ├── message-bus.js
│   │   │   └── types.js
│   │   └── coordinator.js # Main orchestrator
│   └── package.json
├── src/                    # Frontend (Angular)
│   ├── services/
│   │   └── backend-api.service.ts
│   └── components/
└── README.md
```

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design
- [REQUIREMENTS.md](REQUIREMENTS.md) - Requirements for prototype to demo transition
- [PROXY_DEPLOYMENT.md](PROXY_DEPLOYMENT.md) - Proxy API deployment guide
- [CONTEXT.md](CONTEXT.md) - Project context and history
- [backend/README.md](backend/README.md) - Backend-specific documentation

## Development

### Adding a New Agent

1. Create `backend/src/agents/your-agent.js`
2. Extend `BaseAgent` class
3. Implement agent-specific logic
4. Register in `coordinator.js`
5. Add npm script in `backend/package.json`

### Message Bus

Agents communicate via `AgentPacket` messages. Supported transports:
- **memory**: In-process (default, single server)
- **redis**: Distributed (multiple servers)

See [backend/README.md](backend/README.md) for details.

## License

MIT

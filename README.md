# PDF Concept Tagger

Intelligent PDF analysis system using multi-agent AI to extract concepts, relationships, and domain structures from documents.

## 🚀 Quick Start

**Want to experiment immediately?**
```bash
cd experiment-backend
./setup.sh
# Edit .env with API keys
python server.py
```

**Want the full demo machine?**
See [docs/demo-machine/DEMO_SETUP.md](docs/demo-machine/DEMO_SETUP.md) for complete setup instructions.

## 📋 Project Status

### Track 1: Experimentation Backend ✅
- **Status**: Ready to use
- **Location**: `experiment-backend/`
- **Purpose**: Fast iteration, prompt/model experimentation
- **Setup**: 10 minutes

### Track 2: Full Demo Machine 🚧
- **Status**: In development
- **Location**: `backend-python/`
- **Purpose**: Production-like system with proper architecture
- **Timeline**: 9 weeks (see [docs/demo-machine/TASKS.md](docs/demo-machine/TASKS.md))

## 🏗️ Architecture

- **Backend**: FastAPI + LangChain/LangGraph
- **Agents**: Multi-agent system (HARVESTER, ARCHITECT, CURATOR, CRITIC, OBSERVER)
- **Databases**: PostgreSQL, Neo4j, Pinecone, Elasticsearch, Redis
- **Frontend**: React + Vite (Track 2) / Angular (legacy)
- **LLM**: OpenAI, Anthropic, Google Gemini

See [docs/demo-machine/DEMO_ARCHITECTURE.md](docs/demo-machine/DEMO_ARCHITECTURE.md) for full details.

## 📚 Documentation

### Production (Main Branch)
- **[REQUIREMENTS.md](REQUIREMENTS.md)** - Functional requirements
- **[CONTEXT.md](CONTEXT.md)** - Project context

### Development (Develop Branch)
- **[docs/development/PARALLEL_DEVELOPMENT.md](docs/development/PARALLEL_DEVELOPMENT.md)** - Development coordination
- **[docs/development/REPO_STRUCTURE.md](docs/development/REPO_STRUCTURE.md)** - Repository structure
- **[docs/development/BRANCH_STRATEGY.md](docs/development/BRANCH_STRATEGY.md)** - Git workflow

### Track 1: Experimentation (track1-experiment Branch)
- **[experiment-backend/README.md](experiment-backend/README.md)** - Experiment backend guide
- **[experiment-backend/QUICK_START.md](experiment-backend/QUICK_START.md)** - Quick start

### Track 2: Demo Machine (track2-demo-machine Branch)
- **[docs/demo-machine/DEMO_ARCHITECTURE.md](docs/demo-machine/DEMO_ARCHITECTURE.md)** - Architecture design
- **[docs/demo-machine/DEMO_SETUP.md](docs/demo-machine/DEMO_SETUP.md)** - Setup instructions
- **[docs/demo-machine/TASKS.md](docs/demo-machine/TASKS.md)** - Task breakdown
- **[docs/demo-machine/DESIGN_HOOKS.md](docs/demo-machine/DESIGN_HOOKS.md)** - Design hooks reference

## 🔄 Development Tracks

### Track 1: Experimentation (Fast)
- Experiment with prompts, models, techniques
- Quick iteration and validation
- Immediate feedback

### Track 2: Demo Machine (Comprehensive)
- Production-like architecture
- Full feature implementation
- Proper databases and agents

Both tracks run in parallel and share learnings.

## 🛠️ Technology Stack

- **Python 3.11+** with FastAPI
- **LangChain** + **LangGraph** for agents
- **PostgreSQL** + **Neo4j** + **Pinecone** for storage
- **React** + **Vite** for frontend
- **Docker** for local development

## 📖 Key Features

- ✅ Multi-agent concept extraction
- ✅ Domain model integration
- ✅ RAG pipeline for semantic search
- ✅ Graph visualization
- ✅ Prompt experimentation
- ✅ Model switching (OpenAI/Claude/Gemini)
- ✅ Real-time updates via WebSocket

## 🤝 Contributing

1. Check [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) for workflow
2. Track 1: Use `track1-experiment` branch
3. Track 2: Use `track2-demo-machine` branch
4. See [PARALLEL_DEVELOPMENT.md](PARALLEL_DEVELOPMENT.md) for coordination

## 📝 License

[Add your license here]

## 🔗 Links

- Architecture: [DEMO_ARCHITECTURE.md](DEMO_ARCHITECTURE.md)
- Requirements: [REQUIREMENTS.md](REQUIREMENTS.md)
- Tasks: [TASKS.md](TASKS.md)
- Quick Start: [START_HERE.md](START_HERE.md)

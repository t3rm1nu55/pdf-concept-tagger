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
See [START_HERE.md](START_HERE.md) for complete setup instructions.

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
- **Timeline**: 9 weeks (see TASKS.md)

## 🏗️ Architecture

- **Backend**: FastAPI + LangChain/LangGraph
- **Agents**: Multi-agent system (HARVESTER, ARCHITECT, CURATOR, CRITIC, OBSERVER)
- **Databases**: PostgreSQL, Neo4j, Pinecone, Elasticsearch, Redis
- **Frontend**: React + Vite (Track 2) / Angular (legacy)
- **LLM**: OpenAI, Anthropic, Google Gemini

See [DEMO_ARCHITECTURE.md](DEMO_ARCHITECTURE.md) for full details.

## 📚 Documentation

- **[START_HERE.md](START_HERE.md)** - Quick start guide
- **[PARALLEL_DEVELOPMENT.md](PARALLEL_DEVELOPMENT.md)** - Development coordination
- **[TASKS.md](TASKS.md)** - Detailed task breakdown
- **[REQUIREMENTS.md](REQUIREMENTS.md)** - Functional requirements
- **[DEMO_SETUP.md](DEMO_SETUP.md)** - Setup instructions
- **[BRANCH_STRATEGY.md](BRANCH_STRATEGY.md)** - Git workflow

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

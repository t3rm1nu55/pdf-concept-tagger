# PDF Concept Tagger

Intelligent PDF analysis system using multi-agent AI to extract concepts, relationships, and domain structures from documents.

## 🚀 Quick Start

**Get started in 5 minutes:**
```bash
# See docs/GETTING_STARTED.md for complete instructions
cd backend-python
./start_services.sh
```

**Full setup guide:** [docs/SETUP.md](docs/SETUP.md)

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

**📖 [Complete Documentation Index](docs/README.md)** - Single source of truth

### Essential Docs
- **[Getting Started](docs/GETTING_STARTED.md)** - Quick start guide ⭐
- **[Setup Guide](docs/SETUP.md)** - Complete setup instructions
- **[MVP Status](docs/MVP_STATUS.md)** - Current status and features
- **[Requirements](REQUIREMENTS.md)** - Functional requirements
- **[Project Rules](PROJECT_RULES.md)** - Development standards ⭐

### Development
- **[Design](docs/demo-machine/DESIGN.md)** - Complete design specification
- **[Architecture](docs/demo-machine/DEMO_ARCHITECTURE.md)** - System architecture
- **[Tasks](docs/demo-machine/TASKS.md)** - Implementation tasks
- **[Prototype Alignment](docs/PROTOTYPE_ALIGNMENT.md)** - Frontend integration guide

### Configuration
- **[Gateway Setup](docs/backend-python/GATEWAY_SETUP.md)** - Cognizant LLM Gateway
- **[Environment Config](docs/config/ENV_CONFIG.md)** - Environment variables

## 📋 Current Status

**MVP Backend**: ✅ Complete and ready for testing  
**Frontend**: ⏳ Needs API format alignment (see [Prototype Alignment](docs/PROTOTYPE_ALIGNMENT.md))  
**Next Steps**: Align backend with prototype, connect frontend, expand features

See [MVP Status](docs/MVP_STATUS.md) for details.

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

**Before contributing, read [PROJECT_RULES.md](PROJECT_RULES.md) for development guidelines.**

1. Read [Getting Started](docs/GETTING_STARTED.md)
2. Follow [Project Rules](PROJECT_RULES.md) for code quality
3. See [MVP Status](docs/MVP_STATUS.md) for current status
4. Check [Prototype Alignment](docs/PROTOTYPE_ALIGNMENT.md) for next steps

## 📝 License

[Add your license here]

## 🔗 Quick Links

- **[Documentation](docs/README.md)** - Complete documentation index
- **[Getting Started](docs/GETTING_STARTED.md)** - Quick start guide
- **[Requirements](REQUIREMENTS.md)** - Functional requirements
- **[Design](docs/demo-machine/DESIGN.md)** - Design specification
- **[Tasks](docs/demo-machine/TASKS.md)** - Implementation tasks

# Repository Structure

## Overview

This repository contains multiple development tracks running in parallel.

## Directory Structure

```
pdf-concept-tagger/
│
├── 📁 experiment-backend/      # Track 1: Quick experimentation
│   ├── server.py               # FastAPI server
│   ├── prompts/                # Prompt templates
│   ├── requirements.txt        # Python dependencies
│   ├── setup.sh                # Quick setup script
│   └── test_experiment.py      # Test script
│
├── 📁 backend-python/          # Track 2: Full demo machine
│   ├── app/                    # (To be created)
│   ├── requirements.txt        # Full dependencies
│   └── README.md
│
├── 📁 shared/                  # Shared between tracks
│   └── models.py              # Shared data models
│
├── 📁 src/                     # Current Angular frontend (legacy)
│   ├── app.component.ts
│   ├── services/
│   └── components/
│
├── 📁 backend/                 # Current Node.js backend (legacy)
│   ├── src/
│   │   ├── agents/
│   │   └── coordinator.js
│   └── package.json
│
├── 📄 Documentation/
│   ├── START_HERE.md           # Quick start guide
│   ├── PARALLEL_DEVELOPMENT.md # Coordination plan
│   ├── TASKS.md                # Task breakdown
│   ├── DEMO_ARCHITECTURE.md    # Architecture design
│   ├── REQUIREMENTS.md         # Requirements
│   ├── DESIGN_HOOKS.md        # Design hooks reference
│   ├── DEMO_SETUP.md           # Setup instructions
│   ├── REFACTORING_PLAN.md     # Migration plan
│   ├── BRANCH_STRATEGY.md      # Git workflow
│   └── REPO_STRUCTURE.md       # This file
│
├── 📄 Configuration/
│   ├── docker-compose.yml      # Local databases
│   ├── .gitignore
│   └── package.json            # Frontend dependencies
│
└── 📄 Root Files
    ├── README.md               # Main README
    ├── CONTEXT.md              # Project context
    └── QUICK_START.md          # Quick reference
```

## Track Organization

### Track 1: Experimentation Backend
**Location**: `experiment-backend/`
**Purpose**: Fast iteration, immediate experimentation
**Status**: ✅ Ready to use
**Branch**: `track1-experiment`

### Track 2: Full Demo Machine
**Location**: `backend-python/` + `frontend-react/` (to be created)
**Purpose**: Production-like system
**Status**: 🚧 In development
**Branch**: `track2-demo-machine`

### Legacy Code
**Location**: `src/` (Angular), `backend/` (Node.js)
**Purpose**: Reference, will be migrated
**Status**: 📦 Preserved for reference

## Shared Components

**Location**: `shared/`
- `models.py`: Pydantic models used by both tracks
- Future: `prompts/`, `utils/`, `config/`

## Documentation

All documentation is in the root directory for easy access:
- **Getting Started**: START_HERE.md, QUICK_START.md
- **Architecture**: DEMO_ARCHITECTURE.md
- **Development**: PARALLEL_DEVELOPMENT.md, TASKS.md
- **Reference**: REQUIREMENTS.md, DESIGN_HOOKS.md

## Configuration Files

- `docker-compose.yml`: Local database setup
- `.gitignore`: Git ignore rules
- `package.json`: Frontend dependencies (legacy)
- `requirements.txt`: Python dependencies (per track)

## Future Structure

When Track 2 is complete:
```
pdf-concept-tagger/
├── backend/              # Production backend (from backend-python)
├── frontend/             # Production frontend (from frontend-react)
├── shared/               # Shared components
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── tests/                # Integration tests
```

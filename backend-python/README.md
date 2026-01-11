# Full Demo Machine Backend

Production-like backend with LangChain/LangGraph, proper databases, and RAG pipeline.

## Status

🚧 **In Development** - Follow TASKS.md for implementation

## Quick Start (When Ready)

```bash
# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up databases (see DEMO_SETUP.md)
# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## Architecture

See DEMO_ARCHITECTURE.md for full architecture details.

## Development Tasks

Follow TASKS.md for detailed task breakdown.

## Development Guidelines

**Follow [PROJECT_RULES.md](../PROJECT_RULES.md) for:**
- Incremental & modular development
- Critical mocking guidelines (pytest-specific)
- Requirements → Design → Tasks pipeline
- State-based actions and transparency
- Pragmatic decision-making

## Parallel Development

This track runs parallel to `experiment-backend/`:
- Experiment backend validates approaches quickly
- This backend implements properly with full architecture
- Learnings flow from experiment → demo

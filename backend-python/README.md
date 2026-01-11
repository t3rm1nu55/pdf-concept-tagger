# Full Demo Machine Backend

Production-like backend with LangChain/LangGraph, proper databases, and RAG pipeline.

## Status

🚧 **In Development** - Follow TASKS.md for implementation

## Quick Start

### Setup Virtual Environment

**Option 1: Use setup script (Recommended)**
```bash
cd backend-python
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

**Option 2: Manual setup**
```bash
cd backend-python
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Configure Environment

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```bash
nano .env  # or use your preferred editor
```

### Run Examples

```bash
# Activate venv (if not already active)
source venv/bin/activate

# Run LlamaIndex examples
python llamaindex_example_usage.py

# Test structured extraction pipeline
python -c "from structured_extraction_pipeline import StructuredExtractionPipeline; print('Pipeline ready!')"
```

### Development

```bash
# Activate venv
source venv/bin/activate

# Install new packages
pip install package_name
pip freeze > requirements.txt  # Update requirements

# Run tests (when available)
pytest

# Start server (when implemented)
uvicorn app.main:app --reload
```

### Virtual Environment Management

**Activate:**
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**Deactivate:**
```bash
deactivate
```

**Check if activated:**
```bash
which python  # Should show venv/bin/python
```

**Remove and recreate:**
```bash
rm -rf venv
./setup.sh
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

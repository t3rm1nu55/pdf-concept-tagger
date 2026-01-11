# Experimentation Backend

Quick-start backend for experimenting with prompts, models, techniques, and domain models.

## Quick Start (5 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and edit .env
cp .env.example .env
# Add your API keys

# Run server
python server.py
# Or: uvicorn server:app --reload
```

Server runs on http://localhost:8000

## Features

- ✅ PDF analysis with streaming responses
- ✅ Multiple LLM provider support (OpenAI, Anthropic, Google)
- ✅ Model switching at runtime
- ✅ Prompt experimentation endpoint
- ✅ WebSocket support for real-time updates
- ✅ Simple in-memory storage (easy to swap for real DBs)

## API Endpoints

### POST /api/v1/analyze
Analyze PDF page image.

**Request:**
```json
{
  "image_base64": "data:image/png;base64,...",
  "page_number": 1,
  "exclude_terms": [],
  "prompt_override": "optional custom prompt",
  "model_override": "optional model name"
}
```

**Response:** Server-Sent Events stream of AgentPacket objects

### POST /api/v1/prompts/experiment
Test custom prompts.

**Request:**
```
prompt: "Your custom prompt here"
image_base64: "base64 image"
model: "optional model name"
```

### GET /api/v1/models
Get available models and current provider.

### POST /api/v1/models/switch
Switch LLM provider/model.

**Request:**
```json
{
  "provider": "openai",
  "model": "gpt-4-turbo-preview"
}
```

### GET /api/v1/concepts
Get all extracted concepts (in-memory for now).

### WebSocket /ws
Real-time updates (basic echo for now).

## Experimentation Workflow

1. **Start server**: `python server.py`
2. **Test with default prompt**: Use `/api/v1/analyze`
3. **Experiment with prompts**: Use `/api/v1/prompts/experiment`
4. **Switch models**: Use `/api/v1/models/switch`
5. **Compare results**: Check `/api/v1/concepts`

## Next Steps

- Add real databases (PostgreSQL, Neo4j, Pinecone)
- Add LangChain agents
- Add LangGraph workflow
- Add RAG pipeline
- Add domain model integration

# Quick Start: Get Experimenting in 30 Minutes

## Option 1: Minimal Backend (Fastest - 10 minutes)

Just backend API for experimentation:

```bash
cd experiment-backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python server.py
```

Test with curl:
```bash
curl -X POST http://localhost:8000/api/v1/prompts/experiment \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Extract all dates from this text: The project started on 2024-01-15 and will complete on 2024-06-30",
    "image_base64": ""
  }'
```

## Option 2: Full Demo Machine (30 minutes)

Follow DEMO_SETUP.md for complete setup with databases, agents, and frontend.

## Option 3: Use Current Angular App (5 minutes)

Current app works! Just needs backend:

```bash
# Terminal 1: Start current Angular app
npm install
npm run dev

# Terminal 2: Start experiment backend
cd experiment-backend
pip install -r requirements.txt
python server.py

# Update frontend to point to http://localhost:8000
```

## Experimentation Features Available Now

### 1. Prompt Experimentation
- Edit prompts in code or via API
- Test different prompt structures
- Compare prompt performance

### 2. Model Switching
- Switch between OpenAI, Anthropic, Google
- Compare model outputs
- Test different models on same input

### 3. Technique Testing
- Try different extraction approaches
- Test confidence scoring methods
- Experiment with entity types

### 4. Domain Model Testing
- Load domain model JSON files
- Test domain detection
- Validate schema mapping

## What You Can Experiment With

### Prompts
- Entity extraction prompts
- Relationship discovery prompts
- Domain matching prompts
- Confidence scoring prompts

### Models
- GPT-4 (best overall)
- Claude 3 Opus (best for long context)
- Gemini Pro (cost-effective vision)

### Techniques
- Zero-shot extraction
- Few-shot examples
- Chain-of-thought reasoning
- Tool use for validation

### Domain Models
- Microsoft CDM structures
- Accounting schemas
- Trade/commerce models
- Custom domain models

## Next: Add Real Features

Once you've experimented, add:
1. Real databases (see TASKS.md)
2. LangChain agents (see TASKS.md)
3. RAG pipeline (see TASKS.md)
4. Frontend (see TASKS.md)

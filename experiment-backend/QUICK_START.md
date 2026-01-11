# Experiment Backend Quick Start

## 🚀 Get Started in 10 Minutes

```bash
cd experiment-backend
./setup.sh
# Edit .env with your API keys
source venv/bin/activate
python server.py
```

## Test It

```bash
python test_experiment.py
```

## Experimentation Features

### 1. Prompt Experimentation
Edit prompts in `prompts/` directory or test via API:
```bash
curl -X POST http://localhost:8000/api/v1/prompts/experiment \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your custom prompt", "model": "gpt-4-turbo-preview"}'
```

### 2. Model Switching
Switch between OpenAI, Anthropic, Google:
```bash
curl -X POST http://localhost:8000/api/v1/models/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "model": "gpt-4-turbo-preview"}'
```

### 3. Analyze PDF Pages
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/png;base64,...",
    "page_number": 1
  }'
```

## API Endpoints

- `POST /api/v1/analyze` - Analyze PDF page
- `POST /api/v1/prompts/experiment` - Test custom prompts
- `GET /api/v1/models` - List available models
- `POST /api/v1/models/switch` - Switch LLM provider
- `GET /api/v1/concepts` - Get extracted concepts
- `GET /health` - Health check

## Next Steps

1. Experiment with prompts in `prompts/` directory
2. Test different models
3. Try extraction techniques
4. Document findings for Track 2

See `experiment-backend/README.md` for more details.

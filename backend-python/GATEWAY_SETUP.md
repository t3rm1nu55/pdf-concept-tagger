# Cognizant LLM Gateway Setup

The MVP backend uses the Cognizant LLM Gateway for all LLM calls. The gateway provides OpenAI-compatible endpoints with intelligent routing.

## Quick Start

### 1. Start the Gateway

The gateway should be running before starting the MVP backend.

```bash
cd /Users/markforster/cognizant-llm-gateway

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the gateway
python -m clg.server
# Or use uvicorn directly:
uvicorn clg.server:app --host 0.0.0.0 --port 8080
```

The gateway will be available at `http://localhost:8080`

### 2. Configure Gateway Backends

The gateway needs backends configured. See the gateway's documentation for setup:
- `/Users/markforster/cognizant-llm-gateway/clg/backends/README.md`
- `/Users/markforster/cognizant-llm-gateway/clg/backends/QUICKSTART.md`

Common backends:
- **LiteLLM**: Supports OpenAI, Anthropic, Google, etc.
- **Ollama**: Local models
- **Claude CLI**: Anthropic Claude models

### 3. Configure MVP Backend

Set the gateway URL in `.env`:

```bash
COGNIZANT_LLM_GATEWAY_URL=http://localhost:8080
LLM_MODEL=gpt-4-turbo-preview  # Or any model available in gateway
```

### 4. Verify Gateway is Running

```bash
# Check gateway health
curl http://localhost:8080/health

# List available models
curl http://localhost:8080/v1/models

# Test chat completion
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4-turbo-preview",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Gateway Endpoints

The gateway provides:

- **OpenAI-compatible**: `/v1/chat/completions`, `/v1/models`, etc.
- **Anthropic-compatible**: `/v1/messages`
- **Admin**: `/health`, `/status`, `/config`

See `/Users/markforster/cognizant-llm-gateway/clg/api/example_usage.py` for examples.

## Integration

The MVP backend's `CognizantProxyLLM` service automatically uses the gateway:

```python
from app.services.cognizant_proxy import CognizantProxyLLM

llm = CognizantProxyLLM()
response = await llm.chat_completion([
    {"role": "user", "content": "Extract concepts from this text..."}
])
```

The service makes HTTP requests to `{gateway_url}/v1/chat/completions` using OpenAI-compatible format.

## Troubleshooting

### Gateway not responding
- Check gateway is running: `curl http://localhost:8080/health`
- Verify port 8080 is not in use
- Check gateway logs for errors

### Models not available
- Verify backends are configured in gateway
- Check gateway `/status` endpoint for backend status
- Ensure API keys are set in gateway configuration

### Connection errors
- Verify `COGNIZANT_LLM_GATEWAY_URL` in `.env` matches gateway URL
- Check network connectivity
- Review gateway logs for request details

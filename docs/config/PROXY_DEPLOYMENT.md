# Proxy API Deployment Guide

## Overview
This document describes how to deploy a separate proxy API service for the PDF Concept Tagger application. The proxy isolates API key management and provides a clean interface for the frontend application.

## Architecture

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────┐
│  Frontend App   │ ──────> │  Proxy API   │ ──────> │ Gemini API  │
│  (Browser)      │         │  (Server)    │         │             │
└─────────────────┘         └──────────────┘         └─────────────┘
```

## Proxy API Specification

### Endpoint
`POST /api/v1/analyze`

### Request Format
```json
{
  "image": "base64_encoded_image_string",
  "pageNumber": 1,
  "excludeTerms": ["term1", "term2"],
  "prompt": "optional_custom_prompt",
  "model": "gemini-2.5-flash",
  "schema": { /* AgentProtocolSchema */ }
}
```

### Response Format
The proxy should return a streaming response (Server-Sent Events or chunked transfer encoding) containing JSON objects in the AgentPacket format:

```json
[
  {
    "sender": "SYSTEM",
    "intent": "GRAPH_UPDATE",
    "content": { /* ... */ }
  },
  {
    "sender": "HARVESTER",
    "intent": "GRAPH_UPDATE",
    "content": { /* ... */ }
  }
]
```

### Headers
- `Content-Type: application/json`
- `Authorization: Bearer <api_key>` (optional, if proxy requires auth)

## Deployment Options

### Option 1: Node.js/Express Proxy

#### Setup
```bash
mkdir pdf-tagger-proxy
cd pdf-tagger-proxy
npm init -y
npm install express cors @google/genai
```

#### Implementation (`server.js`)
```javascript
const express = require('express');
const cors = require('cors');
const { GoogleGenAI } = require('@google/genai');

const app = express();
app.use(cors());
app.use(express.json({ limit: '50mb' }));

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

app.post('/api/v1/analyze', async (req, res) => {
  try {
    const { image, pageNumber, excludeTerms, prompt, model, schema } = req.body;
    
    // Set up streaming response
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Transfer-Encoding', 'chunked');
    
    const imagePart = {
      inlineData: {
        mimeType: 'image/png',
        data: image
      }
    };
    
    const result = await ai.models.generateContentStream({
      model: model || 'gemini-2.5-flash',
      contents: { parts: [imagePart, { text: prompt }] },
      config: {
        responseMimeType: 'application/json',
        responseSchema: schema,
        maxOutputTokens: 8192
      }
    });
    
    // Stream the response
    for await (const chunk of result) {
      const text = chunk.text || '';
      res.write(text);
    }
    
    res.end();
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Proxy API running on port ${PORT}`);
});
```

#### Environment Variables
Create `.env`:
```
GEMINI_API_KEY=your_gemini_api_key_here
PORT=3000
```

#### Run
```bash
node server.js
```

### Option 2: Python/Flask Proxy

#### Setup
```bash
mkdir pdf-tagger-proxy
cd pdf-tagger-proxy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask flask-cors google-generativeai
```

#### Implementation (`server.py`)
```python
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

@app.route('/api/v1/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        image_data = data.get('image')
        prompt = data.get('prompt', '')
        model_name = data.get('model', 'gemini-2.5-flash')
        
        model = genai.GenerativeModel(model_name)
        
        def generate():
            response = model.generate_content(
                [image_data, prompt],
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        return Response(generate(), mimetype='application/json')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
```

#### Run
```bash
export GEMINI_API_KEY=your_key_here
python server.py
```

### Option 3: Cloud Deployment

#### Vercel (Node.js)
1. Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "server.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/api/v1/analyze",
      "dest": "server.js"
    }
  ],
  "env": {
    "GEMINI_API_KEY": "@gemini_api_key"
  }
}
```

2. Deploy:
```bash
vercel --prod
```

#### Railway/Render
1. Set environment variable: `GEMINI_API_KEY`
2. Deploy the proxy code
3. Update frontend config with proxy URL

## Frontend Configuration

### Environment Variables
Create `.env.local`:
```
PROXY_API_ENDPOINT=http://localhost:3000/api/v1/analyze
PROXY_API_KEY=optional_proxy_auth_key
PROXY_TIMEOUT=60000
PROXY_RETRY_ATTEMPTS=3
PROXY_RETRY_DELAY=1000
```

### Runtime Configuration
Alternatively, set in `index.html` before app loads:
```html
<script>
  window.__PROXY_CONFIG__ = {
    endpoint: 'https://your-proxy-domain.com/api/v1/analyze',
    apiKey: 'optional_key',
    timeout: 60000,
    retryAttempts: 3,
    retryDelay: 1000
  };
</script>
```

## Security Considerations

### 1. API Key Protection
- **Never** expose Gemini API key in frontend code
- Store API key only in proxy server environment variables
- Use secure secret management (e.g., Vercel Secrets, AWS Secrets Manager)

### 2. Rate Limiting
Implement rate limiting in the proxy:
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/v1/analyze', limiter);
```

### 3. CORS Configuration
Restrict CORS to your frontend domain:
```javascript
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:4200',
  credentials: true
}));
```

### 4. Request Validation
Validate incoming requests:
```javascript
app.post('/api/v1/analyze', (req, res, next) => {
  const { image, pageNumber } = req.body;
  
  if (!image || typeof image !== 'string') {
    return res.status(400).json({ error: 'Invalid image data' });
  }
  
  if (image.length > 10 * 1024 * 1024) { // 10MB limit
    return res.status(400).json({ error: 'Image too large' });
  }
  
  next();
}, analyzeHandler);
```

## Monitoring & Logging

### Logging
```javascript
const morgan = require('morgan');
app.use(morgan('combined'));

// Custom logging
app.post('/api/v1/analyze', (req, res) => {
  console.log(`[${new Date().toISOString()}] Request received: page ${req.body.pageNumber}`);
  // ... handler
});
```

### Error Tracking
Consider integrating error tracking (e.g., Sentry):
```javascript
const Sentry = require('@sentry/node');
Sentry.init({ dsn: process.env.SENTRY_DSN });
```

## Testing

### Local Testing
```bash
# Start proxy
node server.js

# Test with curl
curl -X POST http://localhost:3000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_image_data",
    "pageNumber": 1,
    "excludeTerms": [],
    "prompt": "test prompt"
  }'
```

### Health Check Endpoint
Add a health check:
```javascript
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});
```

## Separate Deployment for Surfsense

To avoid interfering with surfsense testing:

1. **Separate Repository/Branch**: Deploy proxy from a separate repo or branch
2. **Different Domain/Subdomain**: Use `pdf-tagger-proxy.yourdomain.com` vs `surfsense-proxy.yourdomain.com`
3. **Separate Environment**: Use different environment variables and API keys
4. **Isolated Infrastructure**: Deploy to separate cloud resources

### Example: Separate Vercel Projects
```bash
# PDF Tagger Proxy
cd pdf-tagger-proxy
vercel --prod --name pdf-tagger-proxy

# Surfsense Proxy (separate)
cd surfsense-proxy
vercel --prod --name surfsense-proxy
```

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure CORS is properly configured in proxy
   - Check that frontend URL matches CORS origin

2. **Streaming Not Working**
   - Verify proxy supports streaming responses
   - Check browser network tab for chunked transfer encoding

3. **Timeout Errors**
   - Increase timeout in frontend config
   - Check proxy server timeout settings

4. **API Key Errors**
   - Verify `GEMINI_API_KEY` is set in proxy environment
   - Check API key is valid and has proper permissions

## Next Steps

1. Deploy proxy to your preferred platform
2. Update frontend `.env.local` with proxy endpoint
3. Test end-to-end flow
4. Monitor proxy logs and performance
5. Set up error alerting


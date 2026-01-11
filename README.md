<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/drive/1YedlEMdBJs7q_5w9PubERhrarZIzm7Sz

## Run Locally

**Prerequisites:**  Node.js

### Option 1: Using Proxy API (Recommended)

1. Install dependencies:
   ```bash
   npm install
   ```

2. Deploy the proxy server (see [PROXY_DEPLOYMENT.md](PROXY_DEPLOYMENT.md)):
   ```bash
   # Example: Run the example proxy server
   GEMINI_API_KEY=your_key_here node proxy-server-example.js
   ```

3. Configure the frontend to use the proxy:
   - Create `.env.local` file:
     ```
     PROXY_API_ENDPOINT=http://localhost:3000/api/v1/analyze
     ```
   - Or set in `index.html` before app loads:
     ```html
     <script>
       window.__PROXY_CONFIG__ = {
         endpoint: 'http://localhost:3000/api/v1/analyze'
       };
     </script>
     ```

4. Run the app:
   ```bash
   npm run dev
   ```

### Option 2: Direct API (Legacy)

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set the `API_KEY` in `.env.local` to your Gemini API key:
   ```
   API_KEY=your_gemini_api_key_here
   ```

3. Run the app:
   ```bash
   npm run dev
   ```

## Features

- **Proxy API Integration**: Secure API key management via proxy server
- **Agent Coordination**: Robust agent coordination framework (ADK/A2A patterns)
- **Streaming Analysis**: Real-time PDF analysis with streaming responses
- **Knowledge Graph**: Interactive D3.js visualization of extracted concepts
- **Persistence**: IndexedDB storage for concepts, relationships, and hypotheses

## Documentation

- [REQUIREMENTS.md](REQUIREMENTS.md) - Requirements for prototype to demo transition
- [PROXY_DEPLOYMENT.md](PROXY_DEPLOYMENT.md) - Proxy API deployment guide
- [CONTEXT.md](CONTEXT.md) - Project context and architecture

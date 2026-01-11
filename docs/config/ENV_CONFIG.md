# Environment Configuration Guide

## Overview
The PDF Concept Tagger supports two modes of operation:
1. **Proxy Mode** (Recommended): Uses a proxy server to handle API calls
2. **Direct Mode** (Legacy): Direct API calls from the browser

## Configuration Methods

### Method 1: Environment Variables (Build Time)

Create a `.env.local` file in the project root:

```bash
# Proxy Mode (Recommended)
PROXY_API_ENDPOINT=http://localhost:3000/api/v1/analyze
PROXY_API_KEY=optional_proxy_auth_key
PROXY_TIMEOUT=60000
PROXY_RETRY_ATTEMPTS=3
PROXY_RETRY_DELAY=1000

# Direct Mode (Legacy - only if PROXY_API_ENDPOINT is not set)
API_KEY=your_gemini_api_key_here
```

### Method 2: Runtime Configuration (Browser)

Set configuration in `index.html` before the app loads:

```html
<script>
  window.__PROXY_CONFIG__ = {
    endpoint: 'https://your-proxy-domain.com/api/v1/analyze',
    apiKey: 'optional_proxy_auth_key',
    timeout: 60000,
    retryAttempts: 3,
    retryDelay: 1000
  };
</script>
```

### Method 3: Programmatic Configuration

Update configuration at runtime:

```typescript
import { ConfigService } from './services/config.service';

const configService = inject(ConfigService);
configService.updateConfig({
  endpoint: 'https://new-proxy-endpoint.com/api/v1/analyze',
  timeout: 120000
});
```

## Configuration Options

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PROXY_API_ENDPOINT` | string | `http://localhost:3000/api/v1/analyze` | Proxy API endpoint URL |
| `PROXY_API_KEY` | string | `undefined` | Optional authentication key for proxy |
| `PROXY_TIMEOUT` | number | `60000` | Request timeout in milliseconds |
| `PROXY_RETRY_ATTEMPTS` | number | `3` | Number of retry attempts on failure |
| `PROXY_RETRY_DELAY` | number | `1000` | Initial retry delay in milliseconds (exponential backoff) |
| `API_KEY` | string | `undefined` | Direct Gemini API key (legacy mode) |

## Proxy Mode vs Direct Mode

### Proxy Mode (Recommended)
- ✅ API keys stay secure on the server
- ✅ Rate limiting and monitoring capabilities
- ✅ Better error handling and retry logic
- ✅ Can be deployed separately from frontend
- ✅ Supports multiple frontend instances

### Direct Mode (Legacy)
- ⚠️ API key exposed in browser (security risk)
- ⚠️ Limited error handling
- ⚠️ No rate limiting
- ✅ Simpler setup for development

## Environment-Specific Configuration

### Development
```bash
PROXY_API_ENDPOINT=http://localhost:3000/api/v1/analyze
```

### Staging
```bash
PROXY_API_ENDPOINT=https://staging-proxy.yourdomain.com/api/v1/analyze
PROXY_API_KEY=staging_auth_key
```

### Production
```bash
PROXY_API_ENDPOINT=https://proxy.yourdomain.com/api/v1/analyze
PROXY_API_KEY=production_auth_key
PROXY_TIMEOUT=120000
PROXY_RETRY_ATTEMPTS=5
```

## Troubleshooting

### Proxy Not Found
- Check that `PROXY_API_ENDPOINT` is correctly set
- Verify the proxy server is running
- Check CORS configuration on proxy server

### Timeout Errors
- Increase `PROXY_TIMEOUT` value
- Check network connectivity
- Verify proxy server is responding

### Authentication Errors
- Verify `PROXY_API_KEY` is correct (if required)
- Check proxy server authentication configuration

### Fallback to Direct Mode
If proxy is unavailable and `API_KEY` is set, the app will automatically fall back to direct mode (if configured).


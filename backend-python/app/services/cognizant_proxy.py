"""
Cognizant LLM Gateway Service

Handles all LLM calls through the Cognizant LLM Gateway.
The gateway provides OpenAI-compatible endpoints with intelligent routing.

See PROJECT_RULES.md for development guidelines.
"""

import os
import httpx
from typing import List, Dict, Optional, AsyncIterator
from dotenv import load_dotenv
from app.core.logging import logger

load_dotenv()


class CognizantProxyLLM:
    """
    LLM service using Cognizant proxy for all API calls.
    
    This service abstracts LLM provider details and routes all calls
    through the Cognizant proxy endpoint.
    
    Attributes:
        proxy_endpoint: Cognizant proxy endpoint URL
        proxy_api_key: API key for proxy authentication
        provider: LLM provider (openai, anthropic, google)
        model: Model name (e.g., gpt-4-turbo-preview)
        timeout: Request timeout in seconds
    """
    
    def __init__(self):
        """Initialize the gateway LLM service."""
        # Gateway URL - defaults to localhost:8080 if not set
        self.gateway_url = os.getenv("COGNIZANT_LLM_GATEWAY_URL", "http://localhost:8080")
        # API key is optional for now (gateway may not require auth in dev)
        self.api_key = os.getenv("COGNIZANT_LLM_GATEWAY_API_KEY", "")
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.model = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
        self.timeout = float(os.getenv("COGNIZANT_GATEWAY_TIMEOUT", "60.0"))
        
        # Remove trailing slash
        self.gateway_url = self.gateway_url.rstrip("/")
        
        logger.info(f"Initialized CognizantProxyLLM: gateway={self.gateway_url}, model={self.model}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ):
        """
        Call LLM via Cognizant proxy for chat completion.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Response dict with 'content' and metadata
            
        Raises:
            httpx.HTTPError: If proxy request fails
            ValueError: If response format is invalid
        """
        logger.debug(f"Calling gateway: {self.model}, messages={len(messages)}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Gateway uses OpenAI-compatible format
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                **kwargs
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
            if stream:
                payload["stream"] = True
            
            # Build headers - API key is optional for gateway
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            try:
                # Gateway provides OpenAI-compatible endpoint
                response = await client.post(
                    f"{self.gateway_url}/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                logger.debug(f"Gateway response: {response.status_code}")
            except httpx.HTTPError as e:
                logger.error(f"Gateway HTTP error: {e}")
                raise
            except Exception as e:
                logger.error(f"Gateway error: {e}")
                raise
            
            if stream:
                async for chunk in self._handle_stream_response(response):
                    yield chunk
            else:
                return response.json()
    
    async def _handle_stream_response(self, response: httpx.Response) -> AsyncIterator[Dict]:
        """
        Handle streaming response from proxy.
        
        Yields:
            Dict with 'content' chunk and metadata
        """
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    break
                try:
                    import json
                    yield json.loads(data)
                except json.JSONDecodeError:
                    continue
    
    async def extract_concepts(
        self,
        text: str,
        prompt_template: Optional[str] = None
    ) -> List[Dict]:
        """
        Extract concepts from text using LLM via proxy.
        
        Args:
            text: Text to extract concepts from
            prompt_template: Optional custom prompt template
            
        Returns:
            List of concept dicts with id, term, type, confidence, etc.
        """
        if not prompt_template:
            prompt_template = self._get_default_extraction_prompt()
        
        messages = [
            {
                "role": "system",
                "content": "You are a concept extraction agent. Extract concepts from text and return JSON."
            },
            {
                "role": "user",
                "content": f"{prompt_template}\n\nText:\n{text}"
            }
        ]
        
        # Note: response_format may need to be passed differently depending on proxy
        # Check Cognizant proxy documentation for exact format
        response = await self.chat_completion(
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"} if self.provider == "openai" else None
        )
        
        # Parse response and extract concepts
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        import json
        result = json.loads(content)
        return result.get("concepts", [])
    
    def _get_default_extraction_prompt(self) -> str:
        """Get default concept extraction prompt."""
        return """
Extract concepts from the following text. Return a JSON object with a "concepts" array.

Each concept should have:
- id: unique identifier
- term: the concept text
- type: concept type (entity, date, location, organization, etc.)
- confidence: confidence score (0.0-1.0)
- explanation: brief explanation

Example:
{
  "concepts": [
    {
      "id": "c1",
      "term": "GDPR",
      "type": "legal",
      "confidence": 0.95,
      "explanation": "General Data Protection Regulation"
    }
  ]
}
"""

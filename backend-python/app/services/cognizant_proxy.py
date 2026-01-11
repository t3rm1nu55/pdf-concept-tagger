"""
Cognizant Proxy LLM Service

Handles all LLM calls through the Cognizant proxy.
This ensures secure API key management and centralized rate limiting.

See PROJECT_RULES.md for development guidelines.
"""

import os
import httpx
from typing import List, Dict, Optional, AsyncIterator
from dotenv import load_dotenv

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
        self.proxy_endpoint = os.getenv("COGNIZANT_PROXY_ENDPOINT")
        self.proxy_api_key = os.getenv("COGNIZANT_PROXY_API_KEY")
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.model = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
        self.timeout = float(os.getenv("COGNIZANT_PROXY_TIMEOUT", "60.0"))
        
        if not self.proxy_endpoint:
            raise ValueError("COGNIZANT_PROXY_ENDPOINT not set in environment")
        if not self.proxy_api_key:
            raise ValueError("COGNIZANT_PROXY_API_KEY not set in environment")
    
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
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "provider": self.provider,
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                **kwargs
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            if stream:
                payload["stream"] = True
            
            headers = {
                "Authorization": f"Bearer {self.proxy_api_key}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{self.proxy_endpoint}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
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

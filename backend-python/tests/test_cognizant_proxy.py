"""
Tests for Cognizant Proxy LLM Service

Tests the proxy integration without making actual API calls.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.cognizant_proxy import CognizantProxyLLM


@pytest.fixture
def mock_proxy_env(monkeypatch):
    """Mock environment variables for proxy."""
    monkeypatch.setenv("COGNIZANT_PROXY_ENDPOINT", "https://test-proxy.com/api/v1/llm")
    monkeypatch.setenv("COGNIZANT_PROXY_API_KEY", "test_api_key")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-4-turbo-preview")


@pytest.fixture
def proxy_llm(mock_proxy_env):
    """Create CognizantProxyLLM instance."""
    return CognizantProxyLLM()


@pytest.mark.asyncio
async def test_proxy_initialization(mock_proxy_env):
    """Test proxy service initializes correctly."""
    llm = CognizantProxyLLM()
    assert llm.proxy_endpoint == "https://test-proxy.com/api/v1/llm"
    assert llm.proxy_api_key == "test_api_key"
    assert llm.provider == "openai"
    assert llm.model == "gpt-4-turbo-preview"


@pytest.mark.asyncio
async def test_proxy_missing_endpoint(monkeypatch):
    """Test error when proxy endpoint not set."""
    monkeypatch.delenv("COGNIZANT_PROXY_ENDPOINT", raising=False)
    with pytest.raises(ValueError, match="COGNIZANT_PROXY_ENDPOINT"):
        CognizantProxyLLM()


@pytest.mark.asyncio
async def test_proxy_missing_api_key(monkeypatch):
    """Test error when proxy API key not set."""
    monkeypatch.setenv("COGNIZANT_PROXY_ENDPOINT", "https://test-proxy.com")
    monkeypatch.delenv("COGNIZANT_PROXY_API_KEY", raising=False)
    with pytest.raises(ValueError, match="COGNIZANT_PROXY_API_KEY"):
        CognizantProxyLLM()


@pytest.mark.asyncio
@patch("httpx.AsyncClient")
async def test_chat_completion(mock_client_class, proxy_llm):
    """Test chat completion via proxy."""
    # Mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "Test response"
            }
        }]
    }
    mock_response.raise_for_status = MagicMock()
    
    # Mock client
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client_class.return_value = mock_client
    
    messages = [{"role": "user", "content": "Test"}]
    result = await proxy_llm.chat_completion(messages)
    
    assert result["choices"][0]["message"]["content"] == "Test response"
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert "chat/completions" in call_args[0][0]
    assert call_args[1]["headers"]["Authorization"] == "Bearer test_api_key"


@pytest.mark.asyncio
@patch("httpx.AsyncClient")
async def test_extract_concepts(mock_client_class, proxy_llm):
    """Test concept extraction."""
    # Mock response with JSON concepts
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": '{"concepts": [{"id": "c1", "term": "GDPR", "type": "legal", "confidence": 0.95}]}'
            }
        }]
    }
    mock_response.raise_for_status = MagicMock()
    
    # Mock client
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client_class.return_value = mock_client
    
    concepts = await proxy_llm.extract_concepts("GDPR requires data protection")
    
    assert len(concepts) == 1
    assert concepts[0]["term"] == "GDPR"
    assert concepts[0]["type"] == "legal"
    assert concepts[0]["confidence"] == 0.95

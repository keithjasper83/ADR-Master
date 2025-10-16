"""Tests for LLM configuration."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import Settings
from app.services.llm_service import LLMService


def test_llm_model_default():
    """Test LLM model has default value."""
    settings = Settings()
    assert settings.llm_model == "llama2"


def test_llm_model_custom():
    """Test LLM model can be customized."""
    settings = Settings(llm_model="qwen/qwen3-4b-2507")
    assert settings.llm_model == "qwen/qwen3-4b-2507"


def test_llm_endpoint_default():
    """Test LLM endpoint has default value."""
    settings = Settings()
    assert settings.llm_endpoint == "http://localhost:11434/api/generate"


def test_llm_endpoint_custom():
    """Test LLM endpoint can be customized."""
    custom_endpoint = "http://desktop.taile9300d.ts.net:1234/v1/chat/completions"
    settings = Settings(llm_endpoint=custom_endpoint)
    assert settings.llm_endpoint == custom_endpoint


@pytest.mark.asyncio
async def test_llm_service_uses_configured_model():
    """Test that LLMService uses the configured model name."""
    # Create a mock database session
    mock_db = MagicMock()
    
    # Create settings with custom model
    custom_model = "qwen/qwen3-4b-2507"
    
    with patch("app.services.llm_service.get_settings") as mock_get_settings:
        mock_settings = Settings(llm_model=custom_model)
        mock_get_settings.return_value = mock_settings
        
        # Create LLM service
        llm_service = LLMService(mock_db)
        
        # Verify the service has the correct settings
        assert llm_service.settings.llm_model == custom_model
        
        # Mock httpx client to verify the model is used
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={"response": "test response"})
            
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            # Call the LLM
            result = await llm_service._call_llm("test content")
            
            # Verify the model was used in the request
            assert mock_post.called
            call_args = mock_post.call_args
            assert call_args is not None
            json_data = call_args.kwargs.get("json", {})
            assert json_data.get("model") == custom_model
            assert result == "test response"

# LLM service - Swappable LLM implementations
from .base import LLMService
from .azure_openai import AzureOpenAIService
from app.config import get_settings

# Singleton instance
_llm_service: LLMService = None


def get_llm_service() -> LLMService:
    """Factory function to get the configured LLM service."""
    global _llm_service
    
    if _llm_service is None:
        settings = get_settings()
        _llm_service = AzureOpenAIService(
            endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            deployment=settings.AZURE_OPENAI_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
    
    return _llm_service


__all__ = ["LLMService", "get_llm_service"]

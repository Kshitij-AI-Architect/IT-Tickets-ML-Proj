# Embeddings service - Swappable embedding implementations
from .base import EmbeddingService
from .sentence_transformers import SentenceTransformersEmbeddingService
from app.config import get_settings

# Singleton instance (model loading is expensive)
_embedding_service: EmbeddingService = None


def get_embedding_service() -> EmbeddingService:
    """Factory function to get the configured embedding service."""
    global _embedding_service
    
    if _embedding_service is None:
        settings = get_settings()
        _embedding_service = SentenceTransformersEmbeddingService(
            model_name=settings.EMBEDDING_MODEL
        )
    
    return _embedding_service


__all__ = ["EmbeddingService", "get_embedding_service"]

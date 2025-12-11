"""
Abstract base class for embedding operations.
All embedding implementations must follow this interface.
"""
from abc import ABC, abstractmethod


class EmbeddingService(ABC):
    """Abstract embedding service interface."""
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        pass
    
    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts (batch)."""
        pass

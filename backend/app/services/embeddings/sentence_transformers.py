"""
Sentence Transformers implementation for embeddings.
Free, runs locally on CPU, good quality.
"""
from sentence_transformers import SentenceTransformer
from .base import EmbeddingService


class SentenceTransformersEmbeddingService(EmbeddingService):
    """Local embedding service using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the sentence-transformers model.
                       - "all-MiniLM-L6-v2": Fast, 384 dims, good quality
                       - "all-mpnet-base-v2": Slower, 768 dims, better quality
        """
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()
    
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self._dimension
    
    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts (batch)."""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()

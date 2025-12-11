"""
Application configuration - All external service configs in one place.
Swap providers by changing environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "Ticket Analytics Platform"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    
    # Database (Supabase)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # Azure OpenAI (LLM)
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = ""  # e.g., "gpt-4o"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    # Embeddings (local sentence-transformers)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Fast, good quality, runs on CPU
    EMBEDDING_DIMENSION: int = 384  # Dimension for all-MiniLM-L6-v2
    
    # JWT Auth
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Storage
    STORAGE_PROVIDER: str = "supabase"  # or "local", "s3"
    LOCAL_STORAGE_PATH: str = "./data"
    
    # Clustering
    CLUSTERING_MIN_CLUSTER_SIZE: int = 5
    CLUSTERING_MIN_SAMPLES: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

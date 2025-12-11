# Database service - Swappable database implementations
from .base import DatabaseService
from .supabase import SupabaseDatabaseService
from app.config import get_settings


def get_database_service() -> DatabaseService:
    """Factory function to get the configured database service."""
    settings = get_settings()
    # Currently only Supabase, but easy to add PostgreSQL, etc.
    return SupabaseDatabaseService(
        url=settings.SUPABASE_URL,
        key=settings.SUPABASE_KEY
    )


__all__ = ["DatabaseService", "get_database_service"]

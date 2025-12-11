"""
Abstract base class for database operations.
All database implementations must follow this interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class DatabaseService(ABC):
    """Abstract database service interface."""
    
    # ==================== Organizations ====================
    @abstractmethod
    async def create_organization(self, name: str, settings: dict = None) -> dict:
        """Create a new organization."""
        pass
    
    @abstractmethod
    async def get_organization(self, org_id: str) -> Optional[dict]:
        """Get organization by ID."""
        pass
    
    # ==================== Users ====================
    @abstractmethod
    async def create_user(self, org_id: str, email: str, role: str, password_hash: str) -> dict:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email."""
        pass
    
    # ==================== Schema Mappings ====================
    @abstractmethod
    async def save_schema_mapping(self, org_id: str, mappings: list[dict]) -> None:
        """Save column mappings for an organization."""
        pass
    
    @abstractmethod
    async def get_schema_mapping(self, org_id: str) -> list[dict]:
        """Get column mappings for an organization."""
        pass

    
    # ==================== Uploads ====================
    @abstractmethod
    async def create_upload(self, org_id: str, filename: str, row_count: int = 0) -> dict:
        """Create upload record."""
        pass
    
    @abstractmethod
    async def update_upload_status(self, upload_id: str, status: str, row_count: int = None) -> None:
        """Update upload status."""
        pass
    
    @abstractmethod
    async def get_upload(self, upload_id: str, org_id: str) -> Optional[dict]:
        """Get upload by ID."""
        pass
    
    # ==================== Tickets ====================
    @abstractmethod
    async def insert_tickets(self, tickets: list[dict]) -> None:
        """Bulk insert tickets."""
        pass
    
    @abstractmethod
    async def get_tickets_by_upload(self, upload_id: str, org_id: str) -> list[dict]:
        """Get all tickets for an upload."""
        pass
    
    @abstractmethod
    async def update_ticket_embeddings(self, ticket_ids: list[str], embeddings: list[list[float]]) -> None:
        """Update embeddings for tickets."""
        pass
    
    # ==================== Clusters ====================
    @abstractmethod
    async def create_cluster(self, cluster_data: dict) -> dict:
        """Create a cluster."""
        pass
    
    @abstractmethod
    async def get_clusters(self, org_id: str, upload_id: str = None) -> list[dict]:
        """Get clusters for an organization."""
        pass
    
    @abstractmethod
    async def get_cluster(self, cluster_id: str, org_id: str) -> Optional[dict]:
        """Get cluster by ID."""
        pass
    
    @abstractmethod
    async def assign_tickets_to_cluster(self, cluster_id: str, ticket_ids: list[str]) -> None:
        """Assign tickets to a cluster."""
        pass
    
    # ==================== Knowledge Base ====================
    @abstractmethod
    async def create_knowledge_entry(self, entry: dict) -> dict:
        """Create a knowledge entry (SME feedback)."""
        pass
    
    @abstractmethod
    async def get_knowledge_entries(self, org_id: str, status: str = None) -> list[dict]:
        """Get knowledge entries for an organization."""
        pass
    
    @abstractmethod
    async def update_knowledge_status(self, entry_id: str, status: str, approved_by: str = None, rejection_reason: str = None) -> None:
        """Update knowledge entry status (approve/reject)."""
        pass
    
    @abstractmethod
    async def search_similar_knowledge(self, org_id: str, embedding: list[float], limit: int = 3, threshold: float = 0.7) -> list[dict]:
        """Search for similar knowledge entries using vector similarity."""
        pass
    
    # ==================== Audit Logs ====================
    @abstractmethod
    async def create_audit_log(self, knowledge_id: str, action: str, actor_id: str, details: dict = None) -> None:
        """Create an audit log entry."""
        pass

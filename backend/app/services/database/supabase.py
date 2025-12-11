"""
Supabase implementation of the database service.
Uses Supabase's PostgreSQL with pgvector for vector operations.
"""
from typing import Optional
from supabase import create_client, Client
from .base import DatabaseService
import uuid
from datetime import datetime


class SupabaseDatabaseService(DatabaseService):
    """Supabase database service implementation."""
    
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
    
    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())
    
    # ==================== Organizations ====================
    async def create_organization(self, name: str, settings: dict = None) -> dict:
        org_id = self._generate_id()
        data = {
            "id": org_id,
            "name": name,
            "settings": settings or {},
            "created_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("organizations").insert(data).execute()
        return result.data[0] if result.data else data
    
    async def get_organization(self, org_id: str) -> Optional[dict]:
        result = self.client.table("organizations").select("*").eq("id", org_id).execute()
        return result.data[0] if result.data else None
    
    # ==================== Users ====================
    async def create_user(self, org_id: str, email: str, role: str, password_hash: str) -> dict:
        user_id = self._generate_id()
        data = {
            "id": user_id,
            "org_id": org_id,
            "email": email,
            "role": role,
            "password_hash": password_hash,
            "created_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("users").insert(data).execute()
        return result.data[0] if result.data else data
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        result = self.client.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None

    
    # ==================== Schema Mappings ====================
    async def save_schema_mapping(self, org_id: str, mappings: list[dict]) -> None:
        # Delete existing mappings for this org
        self.client.table("schema_mappings").delete().eq("org_id", org_id).execute()
        
        # Insert new mappings
        for mapping in mappings:
            data = {
                "id": self._generate_id(),
                "org_id": org_id,
                "source_column": mapping["source_column"],
                "canonical_field": mapping["canonical_field"],
                "transform": mapping.get("transform"),
                "created_at": datetime.utcnow().isoformat()
            }
            self.client.table("schema_mappings").insert(data).execute()
    
    async def get_schema_mapping(self, org_id: str) -> list[dict]:
        result = self.client.table("schema_mappings").select("*").eq("org_id", org_id).execute()
        return result.data or []
    
    # ==================== Uploads ====================
    async def create_upload(self, org_id: str, filename: str, row_count: int = 0) -> dict:
        upload_id = self._generate_id()
        data = {
            "id": upload_id,
            "org_id": org_id,
            "filename": filename,
            "row_count": row_count,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("uploads").insert(data).execute()
        return result.data[0] if result.data else data
    
    async def update_upload_status(self, upload_id: str, status: str, row_count: int = None) -> None:
        update_data = {"status": status}
        if row_count is not None:
            update_data["row_count"] = row_count
        self.client.table("uploads").update(update_data).eq("id", upload_id).execute()
    
    async def get_upload(self, upload_id: str, org_id: str) -> Optional[dict]:
        result = self.client.table("uploads").select("*").eq("id", upload_id).eq("org_id", org_id).execute()
        return result.data[0] if result.data else None
    
    # ==================== Tickets ====================
    async def insert_tickets(self, tickets: list[dict]) -> None:
        # Batch insert in chunks of 100
        chunk_size = 100
        for i in range(0, len(tickets), chunk_size):
            chunk = tickets[i:i + chunk_size]
            self.client.table("tickets").insert(chunk).execute()
    
    async def get_tickets_by_upload(self, upload_id: str, org_id: str) -> list[dict]:
        result = self.client.table("tickets").select("*").eq("upload_id", upload_id).eq("org_id", org_id).execute()
        return result.data or []
    
    async def update_ticket_embeddings(self, ticket_ids: list[str], embeddings: list[list[float]]) -> None:
        for ticket_id, embedding in zip(ticket_ids, embeddings):
            self.client.table("tickets").update({"embedding": embedding}).eq("id", ticket_id).execute()

    
    # ==================== Clusters ====================
    async def create_cluster(self, cluster_data: dict) -> dict:
        cluster_id = self._generate_id()
        data = {
            "id": cluster_id,
            **cluster_data,
            "created_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("clusters").insert(data).execute()
        return result.data[0] if result.data else data
    
    async def get_clusters(self, org_id: str, upload_id: str = None) -> list[dict]:
        query = self.client.table("clusters").select("*").eq("org_id", org_id)
        if upload_id:
            query = query.eq("upload_id", upload_id)
        result = query.order("ticket_count", desc=True).execute()
        return result.data or []
    
    async def get_cluster(self, cluster_id: str, org_id: str) -> Optional[dict]:
        result = self.client.table("clusters").select("*").eq("id", cluster_id).eq("org_id", org_id).execute()
        return result.data[0] if result.data else None
    
    async def assign_tickets_to_cluster(self, cluster_id: str, ticket_ids: list[str]) -> None:
        for ticket_id in ticket_ids:
            data = {"cluster_id": cluster_id, "ticket_id": ticket_id}
            self.client.table("cluster_tickets").insert(data).execute()
    
    # ==================== Knowledge Base ====================
    async def create_knowledge_entry(self, entry: dict) -> dict:
        entry_id = self._generate_id()
        data = {
            "id": entry_id,
            **entry,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("knowledge_entries").insert(data).execute()
        return result.data[0] if result.data else data
    
    async def get_knowledge_entries(self, org_id: str, status: str = None) -> list[dict]:
        query = self.client.table("knowledge_entries").select("*").eq("org_id", org_id)
        if status:
            query = query.eq("status", status)
        result = query.order("created_at", desc=True).execute()
        return result.data or []
    
    async def update_knowledge_status(self, entry_id: str, status: str, approved_by: str = None, rejection_reason: str = None) -> None:
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        if approved_by:
            update_data["approved_by"] = approved_by
            update_data["approved_at"] = datetime.utcnow().isoformat()
        if rejection_reason:
            update_data["rejection_reason"] = rejection_reason
        self.client.table("knowledge_entries").update(update_data).eq("id", entry_id).execute()
    
    async def search_similar_knowledge(self, org_id: str, embedding: list[float], limit: int = 3, threshold: float = 0.7) -> list[dict]:
        """
        Search for similar knowledge entries using pgvector.
        Uses Supabase RPC function for vector similarity search.
        """
        result = self.client.rpc(
            "search_knowledge",
            {
                "query_embedding": embedding,
                "match_org_id": org_id,
                "match_threshold": threshold,
                "match_count": limit
            }
        ).execute()
        return result.data or []
    
    # ==================== Audit Logs ====================
    async def create_audit_log(self, knowledge_id: str, action: str, actor_id: str, details: dict = None) -> None:
        data = {
            "id": self._generate_id(),
            "knowledge_id": knowledge_id,
            "action": action,
            "actor_id": actor_id,
            "details": details or {},
            "created_at": datetime.utcnow().isoformat()
        }
        self.client.table("audit_logs").insert(data).execute()

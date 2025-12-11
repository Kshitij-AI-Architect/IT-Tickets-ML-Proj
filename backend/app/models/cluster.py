"""Cluster models."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ClusterBase(BaseModel):
    auto_name: str
    summary: Optional[str] = None
    ticket_count: int = 0


class ClusterCreate(ClusterBase):
    org_id: str
    upload_id: str
    centroid: Optional[list[float]] = None


class Cluster(ClusterBase):
    id: str
    org_id: str
    upload_id: str
    sme_name: Optional[str] = None  # SME can rename
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResolutionStep(BaseModel):
    step: str
    classification: str  # "auto", "semi", "manual"
    time_mins: Optional[int] = None
    reason: Optional[str] = None


class ClusterAssessment(BaseModel):
    """Assessment response for a cluster."""
    cluster_id: str
    cluster_name: str
    ticket_count: int
    
    # Assessment details
    automation_potential: float  # 0-100
    automation_level: str  # "fully_automatable", "semi_automatable", "manual"
    confidence: str  # "high", "medium", "low"
    
    # Content
    summary: str
    recommendation: str
    resolution_steps: list[ResolutionStep]
    
    # Source attribution
    source: str  # "knowledge_base" or "llm_generic"
    knowledge_ids: list[str] = []
    needs_sme_review: bool = False

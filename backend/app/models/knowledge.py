"""Knowledge base models."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class KnowledgeStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AutomationLevel(str, Enum):
    MANUAL = "manual"
    SEMI = "semi"
    AUTO = "auto"


class ResolutionStepInput(BaseModel):
    step: str
    classification: AutomationLevel
    time_mins: Optional[int] = None


class KnowledgeBase(BaseModel):
    category: str
    subcategory: Optional[str] = None
    current_process: str
    automation_level: AutomationLevel
    tools_used: list[str] = []
    blockers: Optional[str] = None
    resolution_steps: list[ResolutionStepInput] = []


class KnowledgeCreate(KnowledgeBase):
    org_id: str
    cluster_id: str
    submitted_by: str


class KnowledgeEntry(KnowledgeBase):
    id: str
    org_id: str
    cluster_id: str
    status: KnowledgeStatus = KnowledgeStatus.PENDING
    submitted_by: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeApproval(BaseModel):
    """Request body for approving/rejecting knowledge."""
    approved: bool
    rejection_reason: Optional[str] = None

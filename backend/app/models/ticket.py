"""Ticket models."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TicketBase(BaseModel):
    ticket_id: str
    description: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    priority: Optional[str] = None


class TicketCreate(TicketBase):
    org_id: str
    upload_id: str
    raw_data: Optional[dict] = None


class Ticket(TicketBase):
    id: str
    org_id: str
    upload_id: str
    cluster_id: Optional[str] = None
    raw_data: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

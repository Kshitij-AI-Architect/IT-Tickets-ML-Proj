"""Organization models."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrganizationBase(BaseModel):
    name: str


class OrganizationCreate(OrganizationBase):
    settings: Optional[dict] = None


class Organization(OrganizationBase):
    id: str
    settings: dict = {}
    created_at: datetime
    
    class Config:
        from_attributes = True

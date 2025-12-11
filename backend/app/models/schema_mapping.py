"""Schema mapping models."""
from pydantic import BaseModel
from typing import Optional


class SchemaMappingBase(BaseModel):
    source_column: str
    canonical_field: str
    transform: Optional[str] = None


class SchemaMappingCreate(BaseModel):
    mappings: list[SchemaMappingBase]


class SchemaMapping(SchemaMappingBase):
    id: str
    org_id: str
    
    class Config:
        from_attributes = True


class ColumnSuggestion(BaseModel):
    """Suggested mapping for a detected column."""
    source_column: str
    suggested_field: Optional[str] = None
    confidence: float = 0.0
    alternatives: list[str] = []


class ColumnDetectionResponse(BaseModel):
    """Response from column detection."""
    columns: list[str]
    suggestions: list[ColumnSuggestion]
    has_existing_mapping: bool = False


# Canonical fields that we support
CANONICAL_FIELDS = [
    "ticket_id",
    "description", 
    "category",
    "subcategory",
    "priority",
    "created_date",
    "resolved_date",
    "resolution",
]

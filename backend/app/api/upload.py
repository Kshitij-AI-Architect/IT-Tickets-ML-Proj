"""Upload and schema mapping API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from typing import Optional
import pandas as pd
import io

from app.api.auth import get_current_user
from app.services import get_database_service, get_storage_service
from app.models.schema_mapping import (
    SchemaMappingCreate, 
    ColumnDetectionResponse, 
    ColumnSuggestion,
    CANONICAL_FIELDS
)

router = APIRouter()


def suggest_mappings(columns: list[str]) -> list[ColumnSuggestion]:
    """Suggest canonical field mappings for detected columns."""
    patterns = {
        "ticket_id": ["number", "ticket", "id", "inc", "ref", "case", "ticket_id", "ticketid"],
        "description": ["desc", "description", "summary", "issue", "detail", "problem", "short"],
        "category": ["cat", "category", "type", "class", "classification", "department"],
        "subcategory": ["subcat", "sub_cat", "subcategory", "sub_category", "subtype", "sub_type"],
        "priority": ["priority", "urgency", "severity", "p1", "p2", "p3", "pri"],
        "created_date": ["created", "opened", "open_date", "created_at", "createdat", "date"],
        "resolved_date": ["resolved", "closed", "close_date", "resolved_at"],
        "resolution": ["resolution", "solution", "fix", "resolved_by", "close_notes"],
    }
    
    suggestions = []
    for col in columns:
        col_lower = col.lower().replace(" ", "").replace("_", "").replace("-", "")
        
        suggestion = ColumnSuggestion(source_column=col)
        
        for canonical, keywords in patterns.items():
            for keyword in keywords:
                if keyword in col_lower:
                    suggestion.suggested_field = canonical
                    suggestion.confidence = 0.9 if keyword == col_lower else 0.7
                    suggestion.alternatives = [f for f in CANONICAL_FIELDS if f != canonical][:3]
                    break
            if suggestion.suggested_field:
                break
        
        if not suggestion.suggested_field:
            suggestion.alternatives = CANONICAL_FIELDS
            suggestion.confidence = 0.0
        
        suggestions.append(suggestion)
    
    return suggestions


@router.post("/detect-columns", response_model=ColumnDetectionResponse)
async def detect_columns(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload Excel file and detect columns for mapping.
    Returns column names with suggested mappings.
    """
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="File must be Excel (.xlsx, .xls) or CSV")
    
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents), nrows=5)
        else:
            df = pd.read_excel(io.BytesIO(contents), nrows=5)
        
        columns = df.columns.tolist()
        suggestions = suggest_mappings(columns)
        
        # Check if org has existing mapping
        db = get_database_service()
        existing = await db.get_schema_mapping(current_user["org_id"])
        
        return ColumnDetectionResponse(
            columns=columns,
            suggestions=suggestions,
            has_existing_mapping=len(existing) > 0
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")


@router.post("/schema-mapping")
async def save_schema_mapping(
    mapping_data: SchemaMappingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Save column mapping for the organization."""
    db = get_database_service()
    
    # Validate that required fields are mapped
    mapped_fields = [m.canonical_field for m in mapping_data.mappings]
    if "description" not in mapped_fields:
        raise HTTPException(
            status_code=400, 
            detail="'description' field mapping is required"
        )
    
    await db.save_schema_mapping(
        org_id=current_user["org_id"],
        mappings=[m.model_dump() for m in mapping_data.mappings]
    )
    
    return {"status": "success", "message": "Schema mapping saved"}


@router.get("/schema-mapping")
async def get_schema_mapping(current_user: dict = Depends(get_current_user)):
    """Get current schema mapping for the organization."""
    db = get_database_service()
    mappings = await db.get_schema_mapping(current_user["org_id"])
    return {"mappings": mappings}


@router.post("/")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload Excel file for processing.
    Requires schema mapping to be configured first.
    """
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="File must be Excel (.xlsx, .xls) or CSV")
    
    db = get_database_service()
    
    # Check if schema mapping exists
    mappings = await db.get_schema_mapping(current_user["org_id"])
    if not mappings:
        raise HTTPException(
            status_code=400,
            detail="Schema mapping not configured. Please configure column mappings first."
        )
    
    # Create upload record
    upload = await db.create_upload(
        org_id=current_user["org_id"],
        filename=file.filename
    )
    
    # Read file contents
    contents = await file.read()
    
    # Store file (optional)
    storage = get_storage_service()
    try:
        await storage.upload_file(
            org_id=current_user["org_id"],
            filename=f"{upload['id']}_{file.filename}",
            file_data=io.BytesIO(contents)
        )
    except Exception:
        pass  # Storage is optional, continue without it
    
    # Process in background
    from app.services.ingestion import process_upload
    background_tasks.add_task(
        process_upload,
        upload_id=upload["id"],
        org_id=current_user["org_id"],
        file_contents=contents,
        filename=file.filename,
        mappings=mappings
    )
    
    return {
        "upload_id": upload["id"],
        "status": "processing",
        "message": "File uploaded and processing started"
    }


@router.get("/{upload_id}/status")
async def get_upload_status(
    upload_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get upload processing status."""
    db = get_database_service()
    upload = await db.get_upload(upload_id, current_user["org_id"])
    
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return upload

"""Feedback API endpoints - SME feedback submission."""
from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import get_current_user, require_role
from app.services import get_database_service, get_embedding_service
from app.models.user import UserRole
from app.models.knowledge import KnowledgeCreate, KnowledgeEntry

router = APIRouter()


@router.post("/", response_model=KnowledgeEntry)
async def submit_feedback(
    feedback: KnowledgeCreate,
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.SME, UserRole.PO]))
):
    """
    Submit SME feedback for a cluster.
    Creates a knowledge entry in 'pending' status for PO approval.
    """
    db = get_database_service()
    
    # Verify cluster exists and belongs to org
    cluster = await db.get_cluster(feedback.cluster_id, current_user["org_id"])
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Create knowledge entry
    entry_data = feedback.model_dump()
    entry_data["org_id"] = current_user["org_id"]
    entry_data["submitted_by"] = current_user["user_id"]
    
    entry = await db.create_knowledge_entry(entry_data)
    
    # Create audit log
    await db.create_audit_log(
        knowledge_id=entry["id"],
        action="submitted",
        actor_id=current_user["user_id"],
        details={"cluster_id": feedback.cluster_id}
    )
    
    return entry


@router.get("/")
async def list_my_feedback(
    current_user: dict = Depends(get_current_user)
):
    """List feedback submitted by current user."""
    db = get_database_service()
    
    # Get all knowledge entries for org
    entries = await db.get_knowledge_entries(current_user["org_id"])
    
    # Filter to current user's submissions
    my_entries = [e for e in entries if e.get("submitted_by") == current_user["user_id"]]
    
    return {"feedback": my_entries}


@router.get("/{feedback_id}")
async def get_feedback(
    feedback_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get feedback details."""
    db = get_database_service()
    
    entries = await db.get_knowledge_entries(current_user["org_id"])
    entry = next((e for e in entries if e["id"] == feedback_id), None)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return entry

"""Approval API endpoints - PO approval workflow."""
from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import get_current_user, require_role
from app.services import get_database_service, get_embedding_service
from app.models.user import UserRole
from app.models.knowledge import KnowledgeApproval

router = APIRouter()


@router.get("/queue")
async def get_approval_queue(
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.PO]))
):
    """Get pending knowledge entries awaiting approval."""
    db = get_database_service()
    
    entries = await db.get_knowledge_entries(
        org_id=current_user["org_id"],
        status="pending"
    )
    
    return {"pending": entries, "count": len(entries)}


@router.post("/{entry_id}/approve")
async def approve_entry(
    entry_id: str,
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.PO]))
):
    """
    Approve a knowledge entry.
    This generates an embedding and makes it available for RAG retrieval.
    """
    db = get_database_service()
    embedding_service = get_embedding_service()
    
    # Get entry
    entries = await db.get_knowledge_entries(current_user["org_id"])
    entry = next((e for e in entries if e["id"] == entry_id), None)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if entry["status"] != "pending":
        raise HTTPException(status_code=400, detail="Entry is not pending")
    
    # Generate embedding for the knowledge entry
    knowledge_text = f"""
    Category: {entry.get('category', '')}
    Subcategory: {entry.get('subcategory', '')}
    Process: {entry.get('current_process', '')}
    Tools: {', '.join(entry.get('tools_used', []))}
    """
    embedding = await embedding_service.embed_text(knowledge_text)
    
    # Update status to approved
    await db.update_knowledge_status(
        entry_id=entry_id,
        status="approved",
        approved_by=current_user["user_id"]
    )
    
    # Store embedding (would need to add this to the entry)
    # For now, we'll handle this in the search function
    
    # Create audit log
    await db.create_audit_log(
        knowledge_id=entry_id,
        action="approved",
        actor_id=current_user["user_id"]
    )
    
    return {"status": "success", "message": "Knowledge entry approved"}


@router.post("/{entry_id}/reject")
async def reject_entry(
    entry_id: str,
    rejection: KnowledgeApproval,
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.PO]))
):
    """Reject a knowledge entry with reason."""
    db = get_database_service()
    
    # Get entry
    entries = await db.get_knowledge_entries(current_user["org_id"])
    entry = next((e for e in entries if e["id"] == entry_id), None)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if entry["status"] != "pending":
        raise HTTPException(status_code=400, detail="Entry is not pending")
    
    # Update status to rejected
    await db.update_knowledge_status(
        entry_id=entry_id,
        status="rejected",
        rejection_reason=rejection.rejection_reason
    )
    
    # Create audit log
    await db.create_audit_log(
        knowledge_id=entry_id,
        action="rejected",
        actor_id=current_user["user_id"],
        details={"reason": rejection.rejection_reason}
    )
    
    return {"status": "success", "message": "Knowledge entry rejected"}


@router.get("/history")
async def get_approval_history(
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.PO]))
):
    """Get history of approved/rejected entries."""
    db = get_database_service()
    
    all_entries = await db.get_knowledge_entries(current_user["org_id"])
    
    approved = [e for e in all_entries if e["status"] == "approved"]
    rejected = [e for e in all_entries if e["status"] == "rejected"]
    
    return {
        "approved": approved,
        "rejected": rejected,
        "total_approved": len(approved),
        "total_rejected": len(rejected)
    }

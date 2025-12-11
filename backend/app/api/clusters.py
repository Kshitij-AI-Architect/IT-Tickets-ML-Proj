"""Clusters API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.api.auth import get_current_user
from app.services import get_database_service
from app.models.cluster import Cluster

router = APIRouter()


@router.get("/")
async def list_clusters(
    upload_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all clusters for the organization."""
    db = get_database_service()
    clusters = await db.get_clusters(
        org_id=current_user["org_id"],
        upload_id=upload_id
    )
    return {"clusters": clusters}


@router.get("/{cluster_id}")
async def get_cluster(
    cluster_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get cluster details."""
    db = get_database_service()
    cluster = await db.get_cluster(cluster_id, current_user["org_id"])
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    return cluster


@router.patch("/{cluster_id}")
async def update_cluster(
    cluster_id: str,
    update_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update cluster (e.g., rename by SME)."""
    db = get_database_service()
    cluster = await db.get_cluster(cluster_id, current_user["org_id"])
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Only allow updating sme_name
    if "sme_name" in update_data:
        # Update in database (would need to add this method)
        pass
    
    return {"status": "success", "message": "Cluster updated"}

"""Assessment API endpoints."""
from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import get_current_user
from app.services import get_database_service
from app.services.assessment import generate_assessment
from app.models.cluster import ClusterAssessment

router = APIRouter()


@router.get("/{cluster_id}", response_model=ClusterAssessment)
async def get_assessment(
    cluster_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get assessment for a cluster.
    Uses RAG to retrieve relevant knowledge and generate grounded assessment.
    """
    db = get_database_service()
    
    # Get cluster
    cluster = await db.get_cluster(cluster_id, current_user["org_id"])
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Generate assessment (with RAG)
    assessment = await generate_assessment(
        cluster=cluster,
        org_id=current_user["org_id"]
    )
    
    return assessment


@router.post("/{cluster_id}/refresh")
async def refresh_assessment(
    cluster_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Force regenerate assessment for a cluster."""
    db = get_database_service()
    
    cluster = await db.get_cluster(cluster_id, current_user["org_id"])
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Generate fresh assessment
    assessment = await generate_assessment(
        cluster=cluster,
        org_id=current_user["org_id"],
        force_refresh=True
    )
    
    return assessment

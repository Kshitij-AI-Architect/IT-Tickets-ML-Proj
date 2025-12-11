"""Analytics API endpoints."""
from fastapi import APIRouter, Depends

from app.api.auth import get_current_user
from app.services import get_database_service

router = APIRouter()


@router.get("/summary")
async def get_summary(
    current_user: dict = Depends(get_current_user)
):
    """Get overall analytics summary for the organization."""
    db = get_database_service()
    
    # Get clusters
    clusters = await db.get_clusters(current_user["org_id"])
    
    # Get knowledge entries
    knowledge = await db.get_knowledge_entries(current_user["org_id"])
    approved_knowledge = [k for k in knowledge if k["status"] == "approved"]
    pending_knowledge = [k for k in knowledge if k["status"] == "pending"]
    
    # Calculate totals
    total_tickets = sum(c.get("ticket_count", 0) for c in clusters)
    
    return {
        "total_clusters": len(clusters),
        "total_tickets": total_tickets,
        "knowledge_entries": {
            "total": len(knowledge),
            "approved": len(approved_knowledge),
            "pending": len(pending_knowledge)
        },
        "top_clusters": clusters[:5]
    }


@router.get("/by-category")
async def get_by_category(
    current_user: dict = Depends(get_current_user)
):
    """Get analytics breakdown by category."""
    db = get_database_service()
    
    clusters = await db.get_clusters(current_user["org_id"])
    
    # Group by cluster name (as proxy for category)
    categories = {}
    for cluster in clusters:
        name = cluster.get("sme_name") or cluster.get("auto_name", "Unknown")
        if name not in categories:
            categories[name] = {
                "name": name,
                "cluster_count": 0,
                "ticket_count": 0
            }
        categories[name]["cluster_count"] += 1
        categories[name]["ticket_count"] += cluster.get("ticket_count", 0)
    
    return {"categories": list(categories.values())}


@router.get("/knowledge-coverage")
async def get_knowledge_coverage(
    current_user: dict = Depends(get_current_user)
):
    """Get knowledge coverage - which clusters have approved knowledge."""
    db = get_database_service()
    
    clusters = await db.get_clusters(current_user["org_id"])
    knowledge = await db.get_knowledge_entries(current_user["org_id"], status="approved")
    
    # Get cluster IDs with knowledge
    clusters_with_knowledge = set(k.get("cluster_id") for k in knowledge)
    
    covered = [c for c in clusters if c["id"] in clusters_with_knowledge]
    uncovered = [c for c in clusters if c["id"] not in clusters_with_knowledge]
    
    coverage_pct = (len(covered) / len(clusters) * 100) if clusters else 0
    
    return {
        "coverage_percentage": round(coverage_pct, 1),
        "covered_clusters": len(covered),
        "uncovered_clusters": len(uncovered),
        "uncovered_list": uncovered[:10]  # Top 10 uncovered
    }

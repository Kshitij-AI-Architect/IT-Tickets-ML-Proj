"""
Clustering service - Group similar tickets using sklearn clustering.
"""
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from collections import Counter

from app.config import get_settings
from app.services import get_database_service, get_llm_service


async def run_clustering(
    upload_id: str,
    org_id: str,
    ticket_ids: list[str],
    embeddings: list[list[float]],
    descriptions: list[str]
):
    """
    Cluster tickets using Agglomerative Clustering and create cluster records.
    Using sklearn's AgglomerativeClustering as it doesn't require C++ build tools.
    """
    settings = get_settings()
    db = get_database_service()
    llm = get_llm_service()
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings)
    
    # Determine number of clusters (heuristic: sqrt of samples, min 2, max 50)
    n_samples = len(embeddings_array)
    n_clusters = max(2, min(50, int(np.sqrt(n_samples))))
    
    # Run Agglomerative Clustering
    clusterer = AgglomerativeClustering(
        n_clusters=n_clusters,
        metric='euclidean',
        linkage='ward'
    )
    cluster_labels = clusterer.fit_predict(embeddings_array)
    
    # Group tickets by cluster
    cluster_groups = {}
    for idx, label in enumerate(cluster_labels):
        if label == -1:  # Noise points
            continue
        if label not in cluster_groups:
            cluster_groups[label] = {
                "ticket_ids": [],
                "embeddings": [],
                "descriptions": []
            }
        cluster_groups[label]["ticket_ids"].append(ticket_ids[idx])
        cluster_groups[label]["embeddings"].append(embeddings[idx])
        cluster_groups[label]["descriptions"].append(descriptions[idx])
    
    # Create cluster records
    for label, group in cluster_groups.items():
        # Calculate centroid
        centroid = np.mean(group["embeddings"], axis=0).tolist()
        
        # Get sample descriptions for naming
        sample_descriptions = group["descriptions"][:10]
        
        # Generate cluster name using LLM
        cluster_name = await generate_cluster_name(llm, sample_descriptions)
        
        # Create cluster
        cluster = await db.create_cluster({
            "org_id": org_id,
            "upload_id": upload_id,
            "auto_name": cluster_name,
            "summary": f"Cluster of {len(group['ticket_ids'])} similar tickets",
            "ticket_count": len(group["ticket_ids"]),
            "centroid": centroid
        })
        
        # Assign tickets to cluster
        await db.assign_tickets_to_cluster(cluster["id"], group["ticket_ids"])


async def generate_cluster_name(llm, descriptions: list[str]) -> str:
    """Generate a descriptive name for a cluster using LLM."""
    sample_text = "\n".join([f"- {d[:200]}" for d in descriptions[:10]])
    
    prompt = f"""Based on these sample ticket descriptions, generate a short, descriptive name for this cluster (max 5 words):

{sample_text}

Respond with ONLY the cluster name, nothing else."""

    try:
        name = await llm.chat(prompt, temperature=0.0, max_tokens=50)
        return name.strip().strip('"').strip("'")
    except Exception:
        return "Uncategorized Issues"

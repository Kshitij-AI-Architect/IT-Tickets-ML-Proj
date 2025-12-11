"""RAG service - Retrieval Augmented Generation for assessments."""
from app.services import get_database_service, get_embedding_service


async def retrieve_relevant_knowledge(
    org_id: str,
    query_text: str,
    limit: int = 3,
    threshold: float = 0.7
) -> list[dict]:
    """
    Retrieve relevant knowledge entries using vector similarity.
    
    Args:
        org_id: Organization ID for isolation
        query_text: Text to find similar knowledge for
        limit: Max entries to return
        threshold: Minimum similarity threshold
    
    Returns:
        List of relevant knowledge entries
    """
    db = get_database_service()
    embedding_service = get_embedding_service()
    
    # Generate embedding for query
    query_embedding = await embedding_service.embed_text(query_text)
    
    # Search for similar knowledge
    results = await db.search_similar_knowledge(
        org_id=org_id,
        embedding=query_embedding,
        limit=limit,
        threshold=threshold
    )
    
    return results


def build_context_from_knowledge(knowledge_entries: list[dict]) -> str:
    """Build context string from retrieved knowledge for LLM prompt."""
    if not knowledge_entries:
        return ""
    
    context_parts = []
    for entry in knowledge_entries:
        context_parts.append(f"""
--- Knowledge Entry ---
Category: {entry.get('category', 'N/A')}
Subcategory: {entry.get('subcategory', 'N/A')}
Current Process: {entry.get('current_process', 'N/A')}
Automation Level: {entry.get('automation_level', 'N/A')}
Tools Used: {', '.join(entry.get('tools_used', []))}
Blockers: {entry.get('blockers', 'None')}
""")
    
    return "\n".join(context_parts)

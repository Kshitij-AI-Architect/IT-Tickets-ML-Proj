"""Knowledge service - Manage SME feedback and knowledge base."""
from app.services import get_database_service, get_embedding_service


async def create_knowledge_with_embedding(entry_data: dict) -> dict:
    """Create knowledge entry and generate embedding for RAG."""
    db = get_database_service()
    embedding_service = get_embedding_service()
    
    # Create the entry
    entry = await db.create_knowledge_entry(entry_data)
    
    # Generate embedding for future RAG retrieval
    knowledge_text = f"""
    Category: {entry_data.get('category', '')}
    Subcategory: {entry_data.get('subcategory', '')}
    Process: {entry_data.get('current_process', '')}
    Tools: {', '.join(entry_data.get('tools_used', []))}
    """
    embedding = await embedding_service.embed_text(knowledge_text)
    
    # Store embedding (handled when approved)
    return entry


async def get_knowledge_for_category(org_id: str, category: str) -> list[dict]:
    """Get all approved knowledge for a category."""
    db = get_database_service()
    all_knowledge = await db.get_knowledge_entries(org_id, status="approved")
    return [k for k in all_knowledge if k.get("category") == category]

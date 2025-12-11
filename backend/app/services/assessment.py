"""
Assessment service - Generate cluster assessments with RAG.
"""
from typing import Optional
from app.services import get_database_service, get_embedding_service, get_llm_service
from app.models.cluster import ClusterAssessment, ResolutionStep


async def generate_assessment(
    cluster: dict,
    org_id: str,
    force_refresh: bool = False
) -> ClusterAssessment:
    """
    Generate assessment for a cluster using RAG.
    
    1. Generate embedding for cluster
    2. Search for similar approved knowledge
    3. If found: Generate grounded assessment
    4. If not found: Generate generic assessment, flag for SME review
    """
    db = get_database_service()
    embedding_service = get_embedding_service()
    llm = get_llm_service()
    
    # 1. Generate embedding for cluster characteristics
    cluster_text = f"{cluster.get('auto_name', '')} {cluster.get('summary', '')}"
    cluster_embedding = await embedding_service.embed_text(cluster_text)
    
    # 2. Search for similar approved knowledge (RAG)
    similar_knowledge = await db.search_similar_knowledge(
        org_id=org_id,
        embedding=cluster_embedding,
        limit=3,
        threshold=0.7
    )
    
    # 3. Generate assessment based on whether knowledge was found
    if similar_knowledge:
        assessment = await generate_grounded_assessment(
            cluster=cluster,
            knowledge=similar_knowledge,
            llm=llm
        )
    else:
        assessment = await generate_generic_assessment(
            cluster=cluster,
            llm=llm
        )
    
    return assessment


async def generate_grounded_assessment(
    cluster: dict,
    knowledge: list[dict],
    llm
) -> ClusterAssessment:
    """Generate assessment grounded in organizational knowledge."""
    
    # Build context from knowledge
    context_parts = []
    knowledge_ids = []
    for k in knowledge:
        knowledge_ids.append(k["id"])
        context_parts.append(f"""
Category: {k.get('category', 'N/A')}
Process: {k.get('current_process', 'N/A')}
Automation Level: {k.get('automation_level', 'N/A')}
Tools: {', '.join(k.get('tools_used', []))}
Blockers: {k.get('blockers', 'None')}
""")
    
    context = "\n---\n".join(context_parts)
    
    prompt = f"""Assess this ticket cluster for automation potential using the organizational knowledge provided.

CLUSTER:
Name: {cluster.get('auto_name', 'Unknown')}
Ticket Count: {cluster.get('ticket_count', 0)}
Summary: {cluster.get('summary', 'N/A')}

ORGANIZATIONAL KNOWLEDGE:
{context}

Based ONLY on the organizational knowledge above, provide:
1. A brief summary of the cluster
2. Automation potential percentage (0-100)
3. Automation level (fully_automatable, semi_automatable, or manual)
4. Confidence (high, medium, low)
5. Recommendation for automation
6. Resolution steps with classification (auto/semi/manual)

Respond in this exact JSON format:
{{
    "summary": "...",
    "automation_potential": 75,
    "automation_level": "semi_automatable",
    "confidence": "high",
    "recommendation": "...",
    "resolution_steps": [
        {{"step": "...", "classification": "auto", "reason": "..."}},
        {{"step": "...", "classification": "manual", "reason": "..."}}
    ]
}}"""

    response = await llm.chat_json(prompt)
    
    return ClusterAssessment(
        cluster_id=cluster["id"],
        cluster_name=cluster.get("sme_name") or cluster.get("auto_name", "Unknown"),
        ticket_count=cluster.get("ticket_count", 0),
        automation_potential=response.get("automation_potential", 50),
        automation_level=response.get("automation_level", "semi_automatable"),
        confidence=response.get("confidence", "medium"),
        summary=response.get("summary", ""),
        recommendation=response.get("recommendation", ""),
        resolution_steps=[
            ResolutionStep(**step) for step in response.get("resolution_steps", [])
        ],
        source="knowledge_base",
        knowledge_ids=knowledge_ids,
        needs_sme_review=False
    )



async def generate_generic_assessment(
    cluster: dict,
    llm
) -> ClusterAssessment:
    """Generate generic assessment when no organizational knowledge exists."""
    
    prompt = f"""Assess this ticket cluster for automation potential.

CLUSTER:
Name: {cluster.get('auto_name', 'Unknown')}
Ticket Count: {cluster.get('ticket_count', 0)}
Summary: {cluster.get('summary', 'N/A')}

NOTE: No prior organizational knowledge exists for this category.
Provide a generic assessment based on industry best practices.
Flag that this needs SME review for organization-specific context.

Respond in this exact JSON format:
{{
    "summary": "...",
    "automation_potential": 50,
    "automation_level": "semi_automatable",
    "confidence": "low",
    "recommendation": "...",
    "resolution_steps": [
        {{"step": "...", "classification": "auto", "reason": "..."}},
        {{"step": "...", "classification": "manual", "reason": "..."}}
    ]
}}"""

    response = await llm.chat_json(prompt)
    
    return ClusterAssessment(
        cluster_id=cluster["id"],
        cluster_name=cluster.get("sme_name") or cluster.get("auto_name", "Unknown"),
        ticket_count=cluster.get("ticket_count", 0),
        automation_potential=response.get("automation_potential", 50),
        automation_level=response.get("automation_level", "semi_automatable"),
        confidence="low",  # Always low for generic
        summary=response.get("summary", ""),
        recommendation=response.get("recommendation", "") + "\n\n⚠️ This is a generic assessment. Please provide organizational context for more accurate results.",
        resolution_steps=[
            ResolutionStep(**step) for step in response.get("resolution_steps", [])
        ],
        source="llm_generic",
        knowledge_ids=[],
        needs_sme_review=True
    )

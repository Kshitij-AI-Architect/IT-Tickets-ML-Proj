"""
Ingestion service - Process uploaded Excel files.
"""
import pandas as pd
import io
import uuid
from datetime import datetime
from typing import Optional

from app.services import get_database_service, get_embedding_service
from app.services.clustering import run_clustering


async def process_upload(
    upload_id: str,
    org_id: str,
    file_contents: bytes,
    filename: str,
    mappings: list[dict]
):
    """
    Process an uploaded file:
    1. Parse Excel/CSV
    2. Apply schema mapping
    3. Store normalized tickets
    4. Generate embeddings
    5. Run clustering
    """
    db = get_database_service()
    
    try:
        # 1. Parse file
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_contents))
        else:
            df = pd.read_excel(io.BytesIO(file_contents))
        
        # 2. Apply schema mapping
        mapping_dict = {m["source_column"]: m["canonical_field"] for m in mappings}
        
        # Create normalized dataframe
        normalized_data = []
        for _, row in df.iterrows():
            ticket = {
                "id": str(uuid.uuid4()),
                "org_id": org_id,
                "upload_id": upload_id,
                "raw_data": row.to_dict(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Map columns
            for source_col, canonical_field in mapping_dict.items():
                if source_col in row.index:
                    value = row[source_col]
                    # Handle NaN values
                    if pd.isna(value):
                        value = None
                    elif isinstance(value, (int, float)):
                        value = str(value)
                    ticket[canonical_field] = value
            
            # Ensure required fields
            if not ticket.get("ticket_id"):
                ticket["ticket_id"] = ticket["id"][:8]
            if not ticket.get("description"):
                ticket["description"] = "No description"
            
            normalized_data.append(ticket)
        
        # 3. Store tickets
        await db.insert_tickets(normalized_data)
        
        # 4. Generate embeddings
        embedding_service = get_embedding_service()
        descriptions = [t["description"] for t in normalized_data]
        embeddings = await embedding_service.embed_texts(descriptions)
        
        # Update tickets with embeddings
        ticket_ids = [t["id"] for t in normalized_data]
        await db.update_ticket_embeddings(ticket_ids, embeddings)
        
        # 5. Run clustering
        await run_clustering(
            upload_id=upload_id,
            org_id=org_id,
            ticket_ids=ticket_ids,
            embeddings=embeddings,
            descriptions=descriptions
        )
        
        # Update upload status
        await db.update_upload_status(
            upload_id=upload_id,
            status="completed",
            row_count=len(normalized_data)
        )
        
    except Exception as e:
        # Update upload status to failed
        await db.update_upload_status(
            upload_id=upload_id,
            status=f"failed: {str(e)}"
        )
        raise

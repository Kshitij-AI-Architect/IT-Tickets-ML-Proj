"""
Supabase Storage implementation.
"""
from supabase import create_client, Client
from typing import BinaryIO
from .base import StorageService


class SupabaseStorageService(StorageService):
    """Supabase storage service implementation."""
    
    def __init__(self, url: str, key: str, bucket: str = "uploads"):
        self.client: Client = create_client(url, key)
        self.bucket = bucket
    
    def _get_path(self, org_id: str, filename: str) -> str:
        """Generate storage path with org isolation."""
        return f"{org_id}/{filename}"
    
    async def upload_file(self, org_id: str, filename: str, file_data: BinaryIO) -> str:
        """Upload a file to Supabase storage."""
        path = self._get_path(org_id, filename)
        
        # Read file data
        content = file_data.read()
        
        # Upload to Supabase
        self.client.storage.from_(self.bucket).upload(
            path=path,
            file=content,
            file_options={"content-type": "application/octet-stream"}
        )
        
        return path
    
    async def download_file(self, path: str) -> bytes:
        """Download a file from Supabase storage."""
        response = self.client.storage.from_(self.bucket).download(path)
        return response
    
    async def delete_file(self, path: str) -> None:
        """Delete a file from Supabase storage."""
        self.client.storage.from_(self.bucket).remove([path])
    
    async def get_file_url(self, path: str, expires_in: int = 3600) -> str:
        """Get a signed URL for file access."""
        response = self.client.storage.from_(self.bucket).create_signed_url(
            path=path,
            expires_in=expires_in
        )
        return response["signedURL"]

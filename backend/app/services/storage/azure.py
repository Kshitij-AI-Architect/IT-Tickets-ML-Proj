import uuid
from typing import BinaryIO, Optional
from pathlib import Path
from datetime import datetime, timedelta

from .base import StorageService


class AzureBlobStorageService(StorageService):
    """Azure Blob Storage implementation."""

    def __init__(self, connection_string: str, container_name: str):
        try:
            from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
            self.BlobSasPermissions = BlobSasPermissions
            self.generate_blob_sas = generate_blob_sas
        except ImportError:
            raise ImportError("azure-storage-blob is required for Azure storage. Install with: pip install azure-storage-blob")

        self.blob_service = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = container_name
        self.container_client = self.blob_service.get_container_client(container_name)

        # Create container if it doesn't exist
        try:
            self.container_client.create_container()
        except Exception:
            pass  # Container already exists

    async def upload(self, file: BinaryIO, filename: str, content_type: str) -> str:
        """Upload a file to Azure Blob Storage."""
        ext = Path(filename).suffix
        blob_name = f"{uuid.uuid4()}{ext}"

        blob_client = self.container_client.get_blob_client(blob_name)
        content = file.read()
        blob_client.upload_blob(content, content_type=content_type, overwrite=True)

        return blob_name

    async def download(self, path: str) -> bytes:
        """Download a file from Azure Blob Storage."""
        blob_client = self.container_client.get_blob_client(path)
        return blob_client.download_blob().readall()

    async def delete(self, path: str) -> bool:
        """Delete a file from Azure Blob Storage."""
        try:
            blob_client = self.container_client.get_blob_client(path)
            blob_client.delete_blob()
            return True
        except Exception:
            return False

    async def get_url(self, path: str, expires_in: Optional[int] = 3600) -> str:
        """Get a SAS URL for the blob."""
        blob_client = self.container_client.get_blob_client(path)

        sas_token = self.generate_blob_sas(
            account_name=self.blob_service.account_name,
            container_name=self.container_name,
            blob_name=path,
            account_key=self.blob_service.credential.account_key,
            permission=self.BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(seconds=expires_in or 3600),
        )

        return f"{blob_client.url}?{sas_token}"

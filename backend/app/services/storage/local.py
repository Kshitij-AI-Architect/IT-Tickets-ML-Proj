import os
import uuid
from typing import BinaryIO, Optional
from pathlib import Path

from .base import StorageService


class LocalStorageService(StorageService):
    """Local filesystem storage implementation."""

    def __init__(self, base_path: str = "uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload(self, file: BinaryIO, filename: str, content_type: str) -> str:
        """Upload a file to local storage."""
        ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = self.base_path / unique_name

        content = file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        return str(unique_name)

    async def download(self, path: str) -> bytes:
        """Download a file from local storage."""
        file_path = self.base_path / path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with open(file_path, "rb") as f:
            return f.read()

    async def delete(self, path: str) -> bool:
        """Delete a file from local storage."""
        file_path = self.base_path / path
        if file_path.exists():
            os.remove(file_path)
            return True
        return False

    async def get_url(self, path: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for the file (returns local path for local storage)."""
        return f"/uploads/{path}"

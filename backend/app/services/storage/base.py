from abc import ABC, abstractmethod
from typing import BinaryIO, Optional


class StorageService(ABC):
    """Abstract base class for storage services."""

    @abstractmethod
    async def upload(self, file: BinaryIO, filename: str, content_type: str) -> str:
        """Upload a file and return its URL/path."""
        pass

    @abstractmethod
    async def download(self, path: str) -> bytes:
        """Download a file by path."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Delete a file by path."""
        pass

    @abstractmethod
    async def get_url(self, path: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing the file."""
        pass

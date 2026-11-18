from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


class StorageInterface(ABC):

    @abstractmethod
    async def save(
        self,
        file: BinaryIO,
        filename: str,
    ) -> str:
        """Save a file and return its relative storage path."""
        pass

    @abstractmethod
    async def delete(
        self,
        file_path: str,
    ) -> bool:
        """Delete a stored file."""
        pass

    @abstractmethod
    def get_absolute_path(
        self,
        file_path: str,
    ) -> Path:
        """Resolve a relative storage path to an absolute path."""
        pass
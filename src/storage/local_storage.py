import asyncio
from pathlib import Path, PurePosixPath
from typing import BinaryIO
from uuid import uuid4

from src.helpers import get_settings
from src.storage.base import StorageInterface


class LocalStorage(StorageInterface):

    def __init__(self) -> None:
        settings = get_settings()

        self.base_path = Path(settings.CV_STORAGE_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(
        self,
        file: BinaryIO,
        filename: str,
    ) -> str:
        original_name = Path(filename).name
        extension = Path(original_name).suffix.lower()

        if extension not in {".pdf", ".doc", ".docx"}:
            raise ValueError("Only PDF, DOC, and DOCX files are allowed.")

        unique_filename = f"{uuid4().hex}{extension}"
        destination = self.base_path / unique_filename

        content = file.read()

        if not content:
            raise ValueError("Cannot save an empty file.")

        await asyncio.to_thread(destination.write_bytes, content)

        return unique_filename

    async def delete(self, file_path: str) -> bool:
        destination = self._resolve_path(file_path)

        def remove_file() -> bool:
            if not destination.is_file():
                return False

            destination.unlink()
            return True

        return await asyncio.to_thread(remove_file)

    def get_absolute_path(self, file_path: str) -> Path:
        return self._resolve_path(file_path)

    def _resolve_path(self, file_path: str) -> Path:
        relative_path = PurePosixPath(file_path)

        if (
            not file_path
            or relative_path.is_absolute()
            or "\\" in file_path
            or ".." in relative_path.parts
            or len(relative_path.parts) != 1
        ):
            raise ValueError("Invalid storage path.")

        destination = (self.base_path / relative_path.name).resolve()

        if not destination.is_relative_to(self.base_path):
            raise ValueError("Storage path is outside the storage directory.")

        return destination
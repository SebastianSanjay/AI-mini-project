import os
import shutil
from typing import Protocol
from config import settings

import aiofiles

class StorageService(Protocol):
    def save_file(self, source_path: str, destination_key: str) -> str: ...
    async def save_stream(self, stream, destination_key: str) -> str: ...
    def get_file_path(self, key: str) -> str: ...
    def delete_file(self, key: str) -> None: ...
    def create_directory(self, dir_name: str) -> None: ...

class LocalStorageService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        # Ensure standard directories exist
        for d in ["uploads", "audio", "transcripts", "translated", "outputs", "logs"]:
            os.makedirs(os.path.join(self.base_dir, d), exist_ok=True)

    def save_file(self, source_path: str, destination_key: str) -> str:
        dest_path = os.path.join(self.base_dir, destination_key)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(source_path, dest_path)
        return dest_path

    async def save_stream(self, stream, destination_key: str) -> str:
        dest_path = os.path.join(self.base_dir, destination_key)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        async with aiofiles.open(dest_path, 'wb') as out_file:
            while True:
                chunk = await stream.read(1024 * 1024)
                if not chunk:
                    break
                await out_file.write(chunk)
        return dest_path

    def get_file_path(self, key: str) -> str:
        return os.path.join(self.base_dir, key)

    def delete_file(self, key: str) -> None:
        path = os.path.join(self.base_dir, key)
        if os.path.exists(path):
            os.remove(path)

    def create_directory(self, dir_name: str) -> None:
        os.makedirs(os.path.join(self.base_dir, dir_name), exist_ok=True)

# Factory logic for later S3 integration
def get_storage_service() -> StorageService:
    if settings.STORAGE_BACKEND == "local":
        return LocalStorageService(settings.LOCAL_STORAGE_DIR)
    # elif settings.STORAGE_BACKEND == "s3":
    #     return S3StorageService()
    else:
        raise ValueError(f"Unknown storage backend: {settings.STORAGE_BACKEND}")

storage = get_storage_service()

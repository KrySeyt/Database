from functools import lru_cache

from .backend import StorageBackend


@lru_cache()
def get_storage_backend(backend_url: str | None = None) -> StorageBackend:
    backend_location = backend_url or r"http://localhost:8000"
    return StorageBackend(backend_location)

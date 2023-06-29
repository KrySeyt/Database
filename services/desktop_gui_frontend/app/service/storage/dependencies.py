from functools import lru_cache

from .backend import StorageBackend


@lru_cache()
def get_storage_backend(backend_url: str) -> StorageBackend:
    backend_location = backend_url
    return StorageBackend(backend_location)

from functools import lru_cache

from .backend import StatisticsBackend


@lru_cache()
def get_statistics_backend(backend_url: str) -> StatisticsBackend:
    backend_location = backend_url
    return StatisticsBackend(backend_location)

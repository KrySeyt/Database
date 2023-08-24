from functools import lru_cache

from .backend import ForecastsBackend


@lru_cache()
def get_forecasts_backend(backend_url: str) -> ForecastsBackend:
    backend_location = backend_url
    return ForecastsBackend(backend_location)

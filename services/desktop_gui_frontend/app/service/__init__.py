from abc import ABC, abstractmethod

from .storage.service import StorageService
from .storage.backend import StorageBackend
from .statistics.service import StatisticsService
from .statistics.backend import StatisticsBackend
from .forecasts.service import ForecastsService
from .forecasts.backend import ForecastsBackend


__all__ = [
    "ServiceFactory",
    "BackendServiceFactory",
    "StorageService",
    "StatisticsService",
    "ForecastsService"
]


class ServiceFactory(ABC):
    @abstractmethod
    def create_storage_service(self) -> StorageService:
        raise NotImplementedError

    @abstractmethod
    def create_statistics_service(self) -> StatisticsService:
        raise NotImplementedError

    @abstractmethod
    def create_forecasts_service(self) -> ForecastsService:
        raise NotImplementedError


class BackendServiceFactory(ServiceFactory):
    def __init__(self, backend_url: str) -> None:
        self.backend_url = backend_url

    def create_storage_service(self) -> StorageService:
        return StorageService(StorageBackend(self.backend_url))

    def create_statistics_service(self) -> StatisticsService:
        return StatisticsService(StatisticsBackend(self.backend_url))

    def create_forecasts_service(self) -> ForecastsService:
        return ForecastsService(ForecastsBackend(self.backend_url))

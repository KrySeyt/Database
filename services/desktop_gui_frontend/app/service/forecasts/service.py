from abc import ABC, abstractmethod

from app.service.exceptions import BackendConnectionError


class ForecastsImp(ABC):
    @abstractmethod
    def get_title_employees_forecast_growth(self, title_name: str, years_count: int) -> dict[int, int]:
        raise NotImplementedError


class ForecastsService:
    def __init__(self, implementation: ForecastsImp) -> None:
        self.implementation = implementation

    def get_title_employees_forecast_growth(self, title_name: str, years_count: int) -> dict[int, int]:
        try:
            return self.implementation.get_title_employees_forecast_growth(title_name, years_count)
        except BackendConnectionError:
            raise

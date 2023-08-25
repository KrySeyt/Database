from abc import ABC, abstractmethod

from app.service.exceptions import BackendConnectionError
from app.service.storage import schema


class StatisticsImp(ABC):
    @abstractmethod
    def get_title_employees_history_growth(self, title_name: str) -> dict[int, int]:
        raise NotImplementedError

    @abstractmethod
    def get_max_work_duration_employees(self, title_name: str) -> list[schema.Employee]:
        raise NotImplementedError

    @abstractmethod
    def get_highest_paid_employees(self, title_name: str) -> list[schema.Employee]:
        raise NotImplementedError


class StatisticsService:
    def __init__(self, implementation: StatisticsImp) -> None:
        self.implementation = implementation

    def get_title_employees_history_growth(self, title_name: str) -> dict[int, int]:
        try:
            return self.implementation.get_title_employees_history_growth(title_name)
        except BackendConnectionError:
            raise

    def get_max_work_duration_employees(self, employees_count: str) -> list[schema.Employee]:
        try:
            return self.implementation.get_max_work_duration_employees(employees_count)
        except BackendConnectionError:
            raise

    def get_highest_paid_employees(self, employees_count: str) -> list[schema.Employee]:
        try:
            return self.implementation.get_highest_paid_employees(employees_count)
        except BackendConnectionError:
            raise

from abc import ABC, abstractmethod
from typing import Any

from ..exceptions import BackendConnectionError
from . import schema
from .. import mixins


class StorageImp(ABC):
    @abstractmethod
    def add_employee(self, employee: schema.EmployeeIn) -> schema.Employee:
        raise NotImplementedError

    @abstractmethod
    def get_employees(self, skip: int, limit: int) -> list[schema.Employee]:
        raise NotImplementedError

    @abstractmethod
    def update_employee(self, new_employee: schema.EmployeeIn, employee_id: int) -> schema.Employee:
        raise NotImplementedError

    @abstractmethod
    def delete_employees(self, employees_ids: list[int]) -> list[schema.Employee]:
        raise NotImplementedError

    @abstractmethod
    def search_employees(self, search_model: schema.EmployeeSearchModel) -> list[schema.Employee]:
        raise NotImplementedError


class StorageService(mixins.ObservableMixin):
    def __init__(self, implementation: StorageImp, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.implementation = implementation

    def add_employee(self, employee_in: schema.EmployeeIn) -> schema.Employee:
        employee = self.implementation.add_employee(employee_in)
        self.notify_observers()
        return employee

    def get_employees(self, skip: int, limit: int) -> list[schema.Employee]:
        employees = self.implementation.get_employees(skip, limit)
        return employees

    def update_employee(self, employee_in: schema.EmployeeIn, employee_id: int) -> schema.Employee:
        employee = self.implementation.update_employee(employee_in, employee_id)
        self.notify_observers()
        return employee

    def delete_employees(self, employees_ids: list[int]) -> list[schema.Employee]:
        employees = self.implementation.delete_employees(employees_ids)
        self.notify_observers()
        return employees

    def search_employees(self, employee_search_model: schema.EmployeeSearchModel) -> list[schema.Employee]:
        return self.implementation.search_employees(employee_search_model)

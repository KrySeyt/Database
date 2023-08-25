from abc import ABC, abstractmethod


from ..exceptions import BackendConnectionError
from . import schema


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


class StorageService:
    def __init__(self, implementation: StorageImp) -> None:
        self.implementation = implementation

    def add_employee(self, employee_in: schema.EmployeeIn) -> schema.Employee:
        try:
            return self.implementation.add_employee(employee_in)
        except BackendConnectionError:
            raise

    def get_employees(self, skip: int, limit: int) -> list[schema.Employee]:
        try:
            return self.implementation.get_employees(skip, limit)
        except BackendConnectionError:
            raise

    def update_employee(self, employee_in: schema.EmployeeIn, employee_id: int) -> schema.Employee:
        try:
            return self.implementation.update_employee(employee_in, employee_id)
        except BackendConnectionError:
            raise

    def delete_employees(self, employees_ids: list[int]) -> list[schema.Employee]:
        try:
            return self.implementation.delete_employees(employees_ids)
        except BackendConnectionError:
            raise

    def search_employees(self, employee_search_model: schema.EmployeeSearchModel) -> list[schema.Employee]:
        try:
            return self.implementation.search_employees(employee_search_model)
        except BackendConnectionError:
            raise

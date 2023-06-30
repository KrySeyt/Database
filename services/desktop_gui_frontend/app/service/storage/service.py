from .backend import StorageBackend, BackendConnectionError
from . import schema


def add_employee(employee_in: schema.EmployeeIn, backend: StorageBackend, ) -> schema.Employee:
    try:
        return backend.add_employee(employee_in)
    except BackendConnectionError:
        raise


def get_employees(skip: int, limit: int, backend: StorageBackend) -> list[schema.Employee]:
    try:
        return backend.get_employees(skip, limit)
    except BackendConnectionError:
        raise

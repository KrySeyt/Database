from .backend import StorageBackend, BackendConnectionError
from . import schema


def add_employee(backend: StorageBackend, employee_in: schema.EmployeeIn) -> schema.Employee:
    try:
        return backend.add_employee(employee_in)
    except BackendConnectionError:
        raise

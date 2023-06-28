from . import schema
from .backend import StorageBackend


# TODO: add exceptions handling, keep abstraction with exceptions
def add_employee(backend: StorageBackend, employee: schema.EmployeeIn) -> schema.Employee:
    return backend.add_employee(employee)

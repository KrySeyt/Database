from .backend import StorageBackend, BackendConnectionError
from . import schema


def add_employee(employee_in: schema.EmployeeIn, backend: StorageBackend) -> schema.Employee:
    try:
        return backend.add_employee(employee_in)
    except BackendConnectionError:
        raise


def get_employees(skip: int, limit: int, backend: StorageBackend) -> list[schema.Employee]:
    try:
        return backend.get_employees(skip, limit)
    except BackendConnectionError:
        raise


def update_employee(employee_in: schema.EmployeeInWithID, backend: StorageBackend) -> schema.Employee:
    try:
        return backend.update_employee(employee_in)
    except BackendConnectionError:
        raise


def delete_employees(employees_ids: list[int], backend: StorageBackend) -> list[schema.Employee]:
    try:
        return backend.delete_employees(employees_ids)
    except BackendConnectionError:
        raise


def search_employees(
        employee_search_model: schema.EmployeeSearchModel,
        backend: StorageBackend
) -> list[schema.Employee]:

    try:
        return backend.search_employees(employee_search_model)
    except BackendConnectionError:
        raise

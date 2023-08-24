from app.service.exceptions import BackendConnectionError
from app.service.storage import schema
from app.service.statistics.backend import StatisticsBackend


def get_title_employees_history_growth(title_name: str, backend: StatisticsBackend) -> dict[int, int]:
    try:
        return backend.get_title_employees_history_growth(title_name)
    except BackendConnectionError:
        raise


def get_max_work_duration_employees(employees_count: str, backend: StatisticsBackend) -> list[schema.Employee]:
    try:
        return backend.get_max_work_duration_employees(employees_count)
    except BackendConnectionError:
        raise


def get_highest_paid_employees(employees_count: str, backend: StatisticsBackend) -> list[schema.Employee]:
    try:
        return backend.get_highest_paid_employees(employees_count)
    except BackendConnectionError:
        raise

#  TODO: Maybe refactor exceptions and their location

from typing import Any

from app.service.storage import schema


class ServiceError(Exception):
    pass


class BackendConnectionError(ServiceError):
    pass


class BackendServerError(ServiceError):
    pass


class WrongData(ServiceError):
    def __init__(self, errors: list[schema.BackendWrongDataInfo], *args: Any) -> None:
        super().__init__(*args)
        self.errors = errors

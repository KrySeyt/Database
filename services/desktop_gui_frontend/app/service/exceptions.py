from typing import Any

from app.service.storage import schema


class BackendConnectionError(IOError):
    pass


class BackendServerError(IOError):
    pass


class WrongData(IOError):
    def __init__(self, errors: list[schema.BackendWrongDataInfo], *args: Any) -> None:
        super().__init__(*args)
        self.errors = errors

from typing import Any


class ServiceError(Exception):
    pass


class WrongData(ServiceError):  # TODO: Refactor wrong user input exceptions
    def __init__(
            self,
            errors_places: list[tuple[Any, ...]] | None = None,
            messages: list[str] | None = None,
            errors_types: list[str] | None = None,
            *args: Any,
            **kwargs: Any
    ) -> None:

        super().__init__(*args, **kwargs)

        self.errors_places = errors_places or []
        self.messages = messages or []
        self.errors_types = errors_types or []


class BackendConnectionError(ServiceError):
    pass


class BackendServerError(ServiceError):
    pass

from typing import Any

from ..exceptions import ServiceError


class WrongDataErrors(ServiceError):
    def __init__(
            self,
            errors_places: list[tuple[Any, ...]],
            messages: list[str],
            errors_types: list[str],
            *args: Any,
            **kwargs: Any
    ) -> None:

        super().__init__(*args, **kwargs)

        self.errors_places = errors_places
        self.messages = messages
        self.errors_types = errors_types


class WrongEmployeeData(WrongDataErrors):
    pass

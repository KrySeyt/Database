from typing import Callable, TypeVar, Type, Any

import PySimpleGUI as sg

from app.service.storage.backend import WrongData


RT = TypeVar("RT")


def wrong_data_exception_handler(
        catching_exception: Type[WrongData],
        callback: Callable[[sg.Window, WrongData], None],
        window: sg.Window
) -> Callable[
    [Callable[..., RT]],
    Callable[..., RT | None]
]:

    def decorator(callable_: Callable[..., RT]) -> Callable[..., RT | None]:
        def wrapper(*args: Any, **kwargs: Any) -> RT | None:
            try:
                return callable_(*args, **kwargs)
            except catching_exception as err:
                callback(window, err)
                return None

        return wrapper
    return decorator

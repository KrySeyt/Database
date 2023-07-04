from typing import Callable, TypeVar, Type, Any

import PySimpleGUI as sg


RT = TypeVar("RT")
EXC_T = TypeVar("EXC_T", bound=Exception)


def wrong_data_exception_handler(
        catching_exception: Type[EXC_T],
        callback: Callable[[sg.Window, EXC_T], None],
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

from enum import Enum
from typing import Callable, TypeVar

import PySimpleGUI as sg


class Event(Enum):
    pass


class Misc(Event):
    NON_EXISTENT = "-NON-EXISTENT-"


class EmployeeEvent(str, Event):
    ADD_EMPLOYEE = "-ADD-EMPLOYEE-"
    ADD_EMPLOYEE_SUCCESS = "-ADD-EMPLOYEE-SUCCESS-"
    ADD_EMPLOYEE_PROCESSING = "-ADD-EMPLOYEE-PROCESSING"
    ADD_EMPLOYEE_FAIL = "-ADD-EMPLOYEE-FAIL-"


class AppEvent(Event):
    START = "-START-"
    EXIT = "-EXIT-"


AT = TypeVar("AT")
RT = TypeVar("RT")


def raise_status_events(
        window: sg.Window,
        success_event: Event,
        processing_event: Event,
        fail_event: Event,
) -> Callable[
    [Callable[..., RT]],
    Callable[..., RT]
]:
    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        def wrapper(*args: AT, **kwargs: AT) -> RT:
            window.write_event_value(processing_event, None)

            try:
                result = func(*args, **kwargs)
                window.write_event_value(success_event, None)
                return result

            except Exception as err:
                window.write_event_value(fail_event, None)
                raise

        return wrapper
    return decorator
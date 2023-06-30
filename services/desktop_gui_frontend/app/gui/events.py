# Events. Set them as keys for elements that raises events or raise directly

from enum import Enum
from typing import Callable, TypeVar

import PySimpleGUI as sg


class Event(Enum):
    pass


class Misc(Event):
    NON_EXISTENT = "-NON-EXISTENT-"


class EmployeeEvent(str, Event):
    EMPLOYEE_SELECTED = "-EMPLOYEE-SELECTED-"

    ADD_EMPLOYEE = "-ADD-EMPLOYEE-"
    ADD_EMPLOYEE_SUCCESS = "-ADD-EMPLOYEE-SUCCESS-"
    ADD_EMPLOYEE_PROCESSING = "-ADD-EMPLOYEE-PROCESSING"
    ADD_EMPLOYEE_FAIL = "-ADD-EMPLOYEE-FAIL-"

    UPDATE_EMPLOYEE = "-UPDATE-EMPLOYEE-"
    UPDATE_EMPLOYEE_SUCCESS = "-UPDATE-EMPLOYEE-SUCCESS-"
    UPDATE_EMPLOYEE_PROCESSING = "-UPDATE-EMPLOYEE-PROCESSING-"
    UPDATE_EMPLOYEE_FAIL = "-UPDATE-EMPLOYEE-FAIL-"

    DELETE_EMPLOYEES = "-DELETE-EMPLOYEES-"
    DELETE_EMPLOYEES_SUCCESS = "-DELETE-EMPLOYEES-SUCCESS-"
    DELETE_EMPLOYEES_PROCESSING = "-DELETE-EMPLOYEES-PROCESSING-"
    DELETE_EMPLOYEES_FAIL = "-DELETE-EMPLOYEES-FAIL-"
    
    SEARCH_EMPLOYEES = "-SEARCH-EMPLOYEES-"


class AppEvent(Event):
    START = "-START-"
    EXIT = "-EXIT-"


AT = TypeVar("AT")
RT = TypeVar("RT")


# On success return function result in values with event as key, like sg.Window.perform_long_operation
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
                window.write_event_value(success_event, result)
                return result

            except Exception as err:
                window.write_event_value(fail_event, None)
                raise

        return wrapper
    return decorator

# Events. Set them as keys for elements that raises events or raise directly

from enum import Enum
from typing import Callable, TypeVar, Type

import PySimpleGUI as sg

from .keys import Key


class Event(Key, Enum):
    pass


class Misc(Event):
    NON_EXISTENT = "-NON-EXISTENT-"
    REVERT_ACTION = "-REVERT-ACTION-"


class OperationStatus(Event):
    SUCCESS = "-SUCCESS-"
    PROCESSING = "-PROCESSING-"
    FAILED = "-FAILED-"


class EmployeeEvent(Event):
    REFRESH_EMPLOYEES_TABLE = "-REFRESH-EMPLOYEES-TABLE-"
    SHOW_EMPLOYEES = "-SHOW-EMPLOYEES-"
    EMPLOYEE_SELECTED = "-EMPLOYEE-SELECTED-"

    GET_EMPLOYEES = "-GET-EMPLOYEES-"
    ADD_EMPLOYEE = "-ADD-EMPLOYEE-"
    UPDATE_EMPLOYEE = "-UPDATE-EMPLOYEE-"
    DELETE_EMPLOYEES = "-DELETE-EMPLOYEES-"
    SEARCH_EMPLOYEES = "-SEARCH-EMPLOYEES-"
    SELECT_EMPLOYEES = "-SELECT-EMPLOYEES-"


class StatisticsEvent(Event):
    SHOW_MAX_WORK_DURATION = "-SHOW-MAX-WORK-DURATION-EMPLOYEES-"
    SHOW_MAX_WORK_DURATION_DIAGRAM = "-SHOW-MAX-WORK-DURATION-EMPLOYEES-DIAGRAM-"

    SHOW_HIGHEST_PAID_EMPLOYEES = "-SHOW-HIGHEST-PAID-EMPLOYEES-EMPLOYEES-"
    SHOW_HIGHEST_PAID_EMPLOYEES_DIAGRAM = "-SHOW-HIGHEST-PAID-EMPLOYEES-EMPLOYEES-DIAGRAM-"

    SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY = "-SHOW-TITLE-EMPLOYEES-GROWTH-HISTORY-"
    SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_DIAGRAM = "-SHOW-TITLE-EMPLOYEES-GROWTH-HISTORY-DIAGRAM-"

    SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES = "-SHOW-EMPLOYEES-DISTRIBUTION-BY-TITLES-"
    SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_DIAGRAM = "-SHOW-EMPLOYEES-DISTRIBUTION-BY-TITLES-DIAGRAM-"

    SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS = "-SHOW-EMPLOYEES-DISTRIBUTION-BY-TOPICS-"
    SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_DIAGRAM = "-SHOW-EMPLOYEES-DISTRIBUTION-BY-TOPICS-DIAGRAM-"


class ForecastsEvent(Event):
    SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST = "-SHOW-TITLE-EMPLOYEES-GROWTH-FORECAST-"
    SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST_DIAGRAM = "-SHOW-TITLE-EMPLOYEES-GROWTH-FORECAST-DIAGRAM-"


class WindowEvent(Event):
    OPEN = "-OPEN-WINDOW-"
    EXIT = "-EXIT-WINDOW-"
    CLOSED = sg.WINDOW_CLOSED
    OPEN_STATISTICS_WINDOW = "-OPEN-STATISTICS-WINDOW-"
    OPEN_FORECASTS_WINDOW = "-OPEN-FORECASTS-WINDOW-"


AT = TypeVar("AT")
RT = TypeVar("RT")


def raise_status_events(
        window: sg.Window,
        success_event: Event,
        processing_event: Event,
        fail_event: Event,
        handle_exception_type: Type[Exception],
        suppress_exception: bool = False
) -> Callable[
    [Callable[..., RT | None]],
    Callable[..., RT | None]
]:
    """

    Raise events before and after successful/failed Callable call and, optionally, suppress exception

    :param window: events will be triggered on this window
    :param success_event: will be triggered after successful function call
    :param processing_event: will be triggered before function call
    :param fail_event: will be triggered after exception that has handle_exception_type type during function run
    :param handle_exception_type: type of exception that will be caught. Other types exceptions will not be caught
    :param suppress_exception: if True function will return None on exception, if False - reraise exception
    :return:
    """

    def decorator(func: Callable[..., RT | None]) -> Callable[..., RT | None]:
        def wrapper(*args: AT, **kwargs: AT) -> RT | None:
            window.write_event_value(processing_event, None)
            try:
                result = func(*args, **kwargs)
                window.write_event_value(success_event, result)
                return result

            except handle_exception_type as err:
                window.write_event_value(fail_event, err)
                if suppress_exception:
                    return None
                raise

        return wrapper
    return decorator

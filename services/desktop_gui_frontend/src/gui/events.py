from enum import Enum
from typing import Any, Callable, TypeVar

import PySimpleGUI as sg

from service import storage
from . import elements


class Event(Enum):
    pass


class EmployeeEvent(str, Event):
    ADD_EMPLOYEE = "-ADD-EMPLOYEE-"
    ADD_EMPLOYEE_SUCCESS = "-ADD-EMPLOYEE-SUCCESS-"
    ADD_EMPLOYEE_PROCESSING = "-ADD-EMPLOYEE-PROCESSING"
    ADD_EMPLOYEE_FAIL = "-ADD-EMPLOYEE-FAIL-"


class ExitEvent(Event):
    EXIT = "-EXIT-"


AT = TypeVar("AT")
RT = TypeVar("RT")


class EventsHandler:
    def handle_event(
            self,
            window: sg.Window,
            event: Event,
            values: dict[elements.Element, Any],

    ) -> None:

        if event is ExitEvent.EXIT:
            self._exit_handler(window, values)

        elif event == EmployeeEvent.ADD_EMPLOYEE:
            self._add_employee_handler(window, values)

        elif event == EmployeeEvent.ADD_EMPLOYEE_SUCCESS:
            self._add_employee_success_handler(window, values)

        elif event == EmployeeEvent.ADD_EMPLOYEE_PROCESSING:
            self._add_employee_processing_handler(window, values)

        elif event == EmployeeEvent.ADD_EMPLOYEE_FAIL:
            self._add_employee_fail_handler(window, values)

    def _add_employee_handler(
            self,
            window: sg.Window,
            values: dict[elements.Element, Any],
            backend: storage.backend.StorageBackend = storage.dependencies.get_storage_backend()
    ) -> None:

        employee = storage.schema.EmployeeIn(
            first_name=values[elements.AddEmployeeForm.FIRST_NAME],
            last_name=values[elements.AddEmployeeForm.LAST_NAME],
            patronymic=values[elements.AddEmployeeForm.PATRONYMIC]
        )

        @self.raise_status_events(window)
        def call_add_employee() -> None:
            storage.service.add_employee(backend, employee)

        window.perform_long_operation(
            call_add_employee,
            end_key=EmployeeEvent.ADD_EMPLOYEE_SUCCESS
        )

    @staticmethod
    def _add_employee_success_handler(
            window: sg.Window,
            values: dict[elements.Element, Any],
    ) -> None:

        window[elements.AddEmployeeForm.ADD_EMPLOYEE_STATUS].update(
            value="Success!",
            text_color="white",
            background_color="green",
            visible=True,
        )

    @staticmethod
    def _add_employee_fail_handler(
            window: sg.Window,
            values: dict[elements.Element, Any],
    ) -> None:

        window[elements.AddEmployeeForm.ADD_EMPLOYEE_STATUS].update(
            value="Fail!",
            text_color="white",
            background_color="red",
            visible=True,
        )

    @staticmethod
    def _add_employee_processing_handler(
            window: sg.Window,
            values: dict[elements.Element, Any],
    ) -> None:

        window[elements.AddEmployeeForm.ADD_EMPLOYEE_STATUS].update(
            value="Processing...",
            text_color="white",
            background_color="grey",
            visible=True,
        )

    def _exit_handler(
            self,
            window: sg.Window,
            values: dict[elements.Element, Any]
    ) -> None:

        window.close()
        
        assert window.is_closed()

    @staticmethod
    def raise_status_events(window: sg.Window) -> Callable[
        [Callable[..., RT]],
        Callable[..., RT]
    ]:
        def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
            def wrapper(*args: AT, **kwargs: AT) -> RT:
                window.write_event_value(EmployeeEvent.ADD_EMPLOYEE_PROCESSING, None)

                try:
                    result = func(*args, **kwargs)
                except Exception as err:
                    window.write_event_value(EmployeeEvent.ADD_EMPLOYEE_FAIL, None)
                    raise err

                return result

            return wrapper
        return decorator

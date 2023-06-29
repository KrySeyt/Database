from typing import Any

import PySimpleGUI as sg

from app.config import get_settings
from app.service.storage.dependencies import get_storage_backend
from . import events
from . import elements
from . import service


class EventsHandler:
    def handle_event(
            self,
            window: sg.Window,
            event: events.Event,
            values: dict[elements.Element, Any],

    ) -> None:

        if event is events.AppEvent.EXIT:
            self._exit_handler(window, values)

        elif event == events.EmployeeEvent.ADD_EMPLOYEE:
            self._add_employee_handler(window, values)

        elif event == events.EmployeeEvent.ADD_EMPLOYEE_SUCCESS:
            self._add_employee_success_handler(window, values)

        elif event == events.EmployeeEvent.ADD_EMPLOYEE_PROCESSING:
            self._add_employee_processing_handler(window, values)

        elif event == events.EmployeeEvent.ADD_EMPLOYEE_FAIL:
            self._add_employee_fail_handler(window, values)

        elif event == events.AppEvent.START:
            self._startup_handler(window, values)

    @staticmethod
    def _add_employee_handler(
            window: sg.Window,
            values: dict[elements.Element, Any],
    ) -> None:

        backend = get_storage_backend(get_settings().backend_location)
        service.add_employee(window, values, backend)

    @staticmethod
    def _add_employee_success_handler(
            window: sg.Window,
            values: dict[elements.Element, Any],
    ) -> None:

        service.show_success(window)

    @staticmethod
    def _add_employee_fail_handler(
            window: sg.Window,
            values: dict[elements.Element, Any],
    ) -> None:

        service.show_fail(window)

    @staticmethod
    def _add_employee_processing_handler(
            window: sg.Window,
            values: dict[elements.Element, Any],
    ) -> None:

        service.show_processing(window)

    @staticmethod
    def _startup_handler(
            window: sg.Window,
            values: dict[elements.Element, Any]
    ) -> None:

        service.update_db_list(window)

    @staticmethod
    def _exit_handler(
            window: sg.Window,
            values: dict[elements.Element, Any]
    ) -> None:

        service.close_window(window)

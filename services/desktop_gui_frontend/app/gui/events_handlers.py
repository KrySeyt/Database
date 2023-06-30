import time
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
            values: dict[elements.Element | events.Event, Any],

    ) -> None:

        if event is events.EmployeeEvent.EMPLOYEE_SELECTED:
            self._employee_entry_selected(window, values)

        elif event is events.AppEvent.EXIT:
            self._exit_handler(window, values)

        elif event is events.EmployeeEvent.ADD_EMPLOYEE:
            self._add_employee_handler(window, values)

        elif event is events.EmployeeEvent.ADD_EMPLOYEE_SUCCESS:
            self._add_employee_success_handler(window, values)

        elif event is events.EmployeeEvent.ADD_EMPLOYEE_PROCESSING:
            self._add_employee_processing_handler(window, values)

        elif event is events.EmployeeEvent.ADD_EMPLOYEE_FAIL:
            self._add_employee_fail_handler(window, values)

        elif event is events.AppEvent.START:
            self._startup_handler(window, values)

    @staticmethod
    def _add_employee_handler(
            window: sg.Window,
            values: dict[elements.Element | events.Event, Any],
    ) -> None:

        backend = get_storage_backend(get_settings().backend_location)
        service.add_employee(window, values, backend)

    @staticmethod
    def _add_employee_success_handler(
            window: sg.Window,
            values: dict[elements.Element | events.Event, Any],
    ) -> None:

        service.show_success(window)
        backend = get_storage_backend(get_settings().backend_location)
        service.update_db_list(window, backend)

    @staticmethod
    def _add_employee_fail_handler(
            window: sg.Window,
            values: dict[elements.Element | events.Event, Any],
    ) -> None:

        service.show_fail(window)

    @staticmethod
    def _add_employee_processing_handler(
            window: sg.Window,
            values: dict[elements.Element | events.Event, Any],
    ) -> None:

        service.show_processing(window)

    @staticmethod
    def _startup_handler(
            window: sg.Window,
            values: dict[elements.Element | events.Event, Any]
    ) -> None:

        backend = get_storage_backend(get_settings().backend_location)
        service.update_db_list(window, backend)

    @staticmethod
    def _employee_entry_selected(
            window: sg.Window,
            values: dict[elements.Element | events.Event, Any],
    ) -> None:
        
        if values[events.EmployeeEvent.EMPLOYEE_SELECTED]:
            service.insert_selected_employee_to_form(window, values)

    @staticmethod
    def _exit_handler(
            window: sg.Window,
            values: dict[elements.Element | events.Event, Any]
    ) -> None:

        service.close_window(window)

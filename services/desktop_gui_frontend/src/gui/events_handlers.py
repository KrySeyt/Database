from typing import Any

import PySimpleGUI as sg

from service import storage
from . import events
from . import elements


class EventsHandler:
    def handle_event(
            self,
            window: sg.Window,
            event: events.Event,
            values: dict[elements.Element, Any],

    ) -> None:

        if event is events.ExitEvent.EXIT:
            self._exit_handler(window, values)

        elif event == events.EmployeeEvent.ADD_EMPLOYEE:
            self._add_employee_handler(window, values)

        elif event == events.EmployeeEvent.ADD_EMPLOYEE_SUCCESS:
            self._add_employee_success_handler(window, values)

        elif event == events.EmployeeEvent.ADD_EMPLOYEE_PROCESSING:
            self._add_employee_processing_handler(window, values)

        elif event == events.EmployeeEvent.ADD_EMPLOYEE_FAIL:
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

        @events.raise_status_events(
            window,
            events.EmployeeEvent.ADD_EMPLOYEE_SUCCESS,
            events.EmployeeEvent.ADD_EMPLOYEE_PROCESSING,
            events.EmployeeEvent.ADD_EMPLOYEE_FAIL
        )
        def call_add_employee() -> None:
            storage.service.add_employee(backend, employee)

        window.perform_long_operation(call_add_employee, end_key=events.Misc.NON_EXISTENT)

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

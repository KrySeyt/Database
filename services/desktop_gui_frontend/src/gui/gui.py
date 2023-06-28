from typing import Any, TypeVar, Callable

import PySimpleGUI as sg

from service import storage
from . import elements
from . import events
from . import layouts


sg.theme("BluePurple")

AT = TypeVar("AT")
RT = TypeVar("RT")


class GUI:
    def __init__(self) -> None:
        self.main_window_layout = layouts.MAIN_WINDOW_LAYOUT
        self.windows_child_relations: dict[sg.Window, list[sg.Window]] = {}

    def start(self) -> None:
        self.run_main_window()
        self._input_handler()

    def run_main_window(self) -> sg.Window:
        main_window = sg.Window(
            "Database",
            self.main_window_layout,
            location=(200, 200),
            finalize=True
        )
        self.windows_child_relations[main_window] = []
        return main_window

    def close_window(self, window: sg.Window) -> None:
        assert window in self.windows_child_relations.keys()

        window.close()
        for child_window in self.windows_child_relations[window]:
            self.close_window(child_window)

    def _input_handler(self) -> None:
        while True:
            window, event, values = sg.read_all_windows()
            if not window:
                return
            event = event or events.ExitEvent.EXIT
            self._event_handler(window, event, values)

    def _event_handler(  # move it to events.py
            self,
            window: sg.Window,
            event: events.Event,
            values: dict[elements.Element, Any]
    ) -> None:

        if event is events.ExitEvent.EXIT:
            self.close_window(window)

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

        @self.raise_status_events(window)
        def call_add_employee() -> None:
            storage.service.add_employee(backend, employee)

        window.perform_long_operation(
            call_add_employee,
            end_key=events.EmployeeEvent.ADD_EMPLOYEE_SUCCESS
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

    @staticmethod
    def raise_status_events(window: sg.Window) -> Callable[
        [Callable[..., RT]],
        Callable[..., RT]
    ]:
        def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
            def wrapper(*args: AT, **kwargs: AT) -> RT:
                window.write_event_value(events.EmployeeEvent.ADD_EMPLOYEE_PROCESSING, None)

                try:
                    result = func(*args, **kwargs)
                except Exception as err:
                    window.write_event_value(events.EmployeeEvent.ADD_EMPLOYEE_FAIL, None)
                    raise err

                return result

            return wrapper
        return decorator

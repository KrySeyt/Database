import time
from typing import Any

import PySimpleGUI as sg

from src.service import storage
from . import elements
from . import events
from . import layouts


sg.theme("BluePurple")


Is_Exit = bool


class GUI:
    def __init__(self) -> None:
        self.main_window_layout = layouts.MAIN_WINDOW_LAYOUT
        self.windows_child_relations: dict[sg.Window, list[sg.Window]] = {}

    def start(self) -> None:
        self.run_main_window()
        self.input_handler()

    def run_main_window(self) -> None:
        main_window = sg.Window(
            "Database",
            self.main_window_layout,
            location=(200, 200),
            finalize=True
        )

        self.windows_child_relations[main_window] = []

    def input_handler(self) -> None:
        while True:
            window, event, values = sg.read_all_windows()
            if not window:
                return
            self.event_handler(window, event, values)

    def event_handler(self, window: sg.Window, event: events.Event, values: dict[elements.Element, Any]) -> Is_Exit:
        if event in (events.WINDOW_CLOSED, events.EXIT):
            self.close_window(window)

        elif event == events.EmployeeEvent.ADD_EMPLOYEE:
            self.add_employee(values)

        return False

    def add_employee(self, values: dict[elements.Element, Any]) -> None:
        employee = storage.schema.EmployeeIn(
            first_name=values[elements.EmployeeInput.FIRST_NAME],
            last_name=values[elements.EmployeeInput.LAST_NAME],
            patronymic=values[elements.EmployeeInput.PATRONYMIC]
        )
        added_employee = storage.service.add_employee(employee)
        print(added_employee)

    def close_window(self, window: sg.Window) -> None:
        window.close()
        for child_window in self.windows_child_relations[window]:
            self.close_window(child_window)

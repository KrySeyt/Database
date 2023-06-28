from typing import TypeVar

import PySimpleGUI as sg

from . import events
from . import layouts


sg.theme("BluePurple")

AT = TypeVar("AT")
RT = TypeVar("RT")


class GUI:
    def __init__(self) -> None:
        self.events_handler = events.EventsHandler()

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

    def _input_handler(self) -> None:
        while True:
            window, event, values = sg.read_all_windows()
            if not window:
                return
            event = event or events.ExitEvent.EXIT
            self.events_handler.handle_event(window, event, values)

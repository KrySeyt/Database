from typing import Callable

import PySimpleGUI as sg

from . import events_handlers
from . import events
from . import layouts
from . import windows


sg.theme("BluePurple")


class GUI:
    def __init__(self, windows_factory: Callable[..., sg.Window]) -> None:
        self.windows_factory = windows_factory
        self.events_handler = events_handlers.EventsHandler()
        self.main_window_layout = layouts.MAIN_WINDOW_LAYOUT

    def start(self) -> None:
        self._run_main_window()
        self._run_input_handler()

    def _run_main_window(self) -> sg.Window:
        main_window = self.windows_factory(
            "Database",
            self.main_window_layout,
            location=(200, 200),
            finalize=True
        )
        return main_window

    def _run_input_handler(self) -> None:
        while True:
            window, event, values = windows.HierarchicalWindow.read_all_windows()

            if not window:
                return
            event = event or events.ExitEvent.EXIT
            assert values

            self.events_handler.handle_event(window, event, values)

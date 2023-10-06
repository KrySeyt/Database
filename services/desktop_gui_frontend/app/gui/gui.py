import PySimpleGUI as sg

from .commands.history import CommandsHistory
from . import events
from . import windows


sg.theme("BluePurple")


class GUI:
    def __init__(self, windows_factory: windows.WindowsFactory, commands_history: "CommandsHistory") -> None:
        self.windows: list[windows.AppWindow] = []
        self.windows_factory = windows_factory
        self.commands_history = commands_history

    def start(self) -> None:
        self.create_main_window()
        self._run_input_handler()

    def exit(self) -> None:
        for window in self.windows:
            window.close()

    def create_main_window(self) -> windows.MainWindow:
        main_window = self.windows_factory.create_main_window(self, self.commands_history)
        self.windows.append(main_window)
        main_window.write_event_value(events.WindowEvent.OPEN, None)
        return main_window

    def create_statistics_window(self) -> windows.StatisticsWindow:
        statistics_window = self.windows_factory.create_statistics_window(self, self.commands_history)
        self.windows.append(statistics_window)
        statistics_window.write_event_value(events.WindowEvent.OPEN, None)
        return statistics_window

    def create_forecasts_window(self) -> windows.ForecastsWindow:
        forecasts_window = self.windows_factory.create_forecasts_window(self, self.commands_history)
        self.windows.append(forecasts_window)
        forecasts_window.write_event_value(events.WindowEvent.OPEN, None)
        return forecasts_window

    def create_diagram_window(self, title: str) -> windows.DiagramWindow:
        diagram_window = self.windows_factory.create_diagram_window(title, self, self.commands_history)
        self.windows.append(diagram_window)
        diagram_window.write_event_value(events.WindowEvent.OPEN, None)
        return diagram_window

    def _run_input_handler(self) -> None:
        while True:
            window, event, values = windows.read_all_windows()

            if __debug__:
                print(window, event, values)

            if not window:
                return

            if values is None:
                return

            event = event or events.WindowEvent.EXIT

            window.handle_event(event, values)

from typing import Any, Self

import PySimpleGUI as sg

from .keys import Key
from . import events


# Mypy see sg.Window as Any, but this is not the case
class HierarchicalWindow(sg.Window):  # type: ignore
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.child_windows: list[Self] = []

    def create_child_window(self, *args: Any, **kwargs: Any) -> Self:
        new_window = type(self)(*args, **kwargs)
        self.child_windows.append(new_window)
        return new_window

    def close(self) -> None:
        super().close()
        assert self.is_closed()

        for child in self.child_windows:
            child.close()
            assert child.is_closed()

    # In return type annotation, Pycharm says AppWindow doesn't exist, but mypy --strict says all ok
    @classmethod
    def read_all_windows(cls) -> tuple[
        Self | None,
        events.Event | None,
        dict[Key, Any] | None
    ]:
        window, event, values = sg.read_all_windows()
        assert isinstance(window, cls) or window is None
        return window, event, values

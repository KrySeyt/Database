from typing import Any, Self

import PySimpleGUI as sg

from . import events
from . import elements


# Mypy see sg.Window as Any, but this is not the case
class HierarchicalWindow(sg.Window):  # type: ignore
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.child_windows: list[Self] = []

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
        dict[elements.Element | events.Event, Any] | None
    ]:
        window, event, values = sg.read_all_windows()
        assert isinstance(window, cls) or window is None
        return window, event, values

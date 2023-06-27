from enum import Enum

from PySimpleGUI import WIN_CLOSED


EXIT = "Exit"
WINDOW_CLOSED = WIN_CLOSED


class Event(str, Enum):
    pass


class EmployeeEvent(Event):
    ADD_EMPLOYEE = "-ADD-EMPLOYEE-"


__all__ = [
    EXIT,
    WINDOW_CLOSED,
    EmployeeEvent
]

from enum import Enum


class Event(Enum):
    pass


class EmployeeEvent(str, Event):
    ADD_EMPLOYEE = "-ADD-EMPLOYEE-"
    ADD_EMPLOYEE_SUCCESS = "-ADD-EMPLOYEE-SUCCESS-"
    ADD_EMPLOYEE_PROCESSING = "-ADD-EMPLOYEE-PROCESSING"
    ADD_EMPLOYEE_FAIL = "-ADD-EMPLOYEE-FAIL-"


class ExitEvent(Event):
    EXIT = "-EXIT-"


__all__ = [
    Event,
    EmployeeEvent,
    ExitEvent,
]

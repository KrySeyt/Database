from typing import Any

import PySimpleGUI as sg

from app.service import storage
from . import events
from . import elements


def update_db_list(window: sg.Window) -> None:
    employees = [
        {
            "name": "NameFirst",
            "surname": "Surname1",
            "patronymic": "patronymic1",
        },
        {
            "name": "NameSecond",
            "surname": "Surname2",
            "patronymic": "patronymic2",
        },
        {
            "name": "NameThird",
            "surname": "Surname3",
            "patronymic": "patronymic3",
        }
    ]

    window[elements.EmployeeList.TABLE].update(values=[list(i.values()) for i in employees])


def add_employee(
        window: sg.Window,
        values: dict[elements.Element, Any],
        backend: storage.backend.StorageBackend
) -> None:

    employee = storage.schema.EmployeeIn(
        name=values[elements.EmployeeForm.FIRST_NAME],
        surname=values[elements.EmployeeForm.LAST_NAME],
        patronymic=values[elements.EmployeeForm.PATRONYMIC]
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


def show_success(window: sg.Window) -> None:
    window[elements.EmployeeForm.ADD_EMPLOYEE_STATUS].update(
        value="Success!",
        text_color="white",
        background_color="green",
        visible=True,
    )


def show_fail(window: sg.Window) -> None:
    window[elements.EmployeeForm.ADD_EMPLOYEE_STATUS].update(
        value="Fail!",
        text_color="white",
        background_color="red",
        visible=True,
    )


def show_processing(window: sg.Window) -> None:
    window[elements.EmployeeForm.ADD_EMPLOYEE_STATUS].update(
        value="Processing...",
        text_color="white",
        background_color="grey",
        visible=True,
    )


def close_window(window: sg.Window) -> None:
    window.close()
    assert window.is_closed()

from typing import Any

import PySimpleGUI as sg

from app.service import storage
from . import events
from . import elements


def add_employee(
        window: sg.Window,
        values: dict[elements.Element | events.Event, Any],
        backend: storage.backend.StorageBackend
) -> None:

    employee = storage.schema.EmployeeIn(
        name=values[elements.EmployeeForm.NAME],
        surname=values[elements.EmployeeForm.SURNAME],
        patronymic=values[elements.EmployeeForm.PATRONYMIC]
    )

    @events.raise_status_events(
        window,
        events.EmployeeEvent.ADD_EMPLOYEE_SUCCESS,
        events.EmployeeEvent.ADD_EMPLOYEE_PROCESSING,
        events.EmployeeEvent.ADD_EMPLOYEE_FAIL
    )
    def call_add_employee() -> None:
        storage.service.add_employee(employee, backend)

    window.perform_long_operation(call_add_employee, end_key=events.Misc.NON_EXISTENT)


def update_db_list(window: sg.Window, backend: storage.backend.StorageBackend) -> None:
    employees = storage.service.get_employees(0, 100, backend)
    window[events.EmployeeEvent.EMPLOYEE_SELECTED].update(values=[list(i.dict().values()) for i in employees])


def insert_selected_employee_to_form(
        window: sg.Window,
        values: dict[elements.Element | events.Event, Any]
) -> None:

    assert values[events.EmployeeEvent.EMPLOYEE_SELECTED]

    employee_entry_id = values[events.EmployeeEvent.EMPLOYEE_SELECTED][-1]
    employee_entry = window[events.EmployeeEvent.EMPLOYEE_SELECTED].get()[employee_entry_id]

    window[elements.EmployeeForm.NAME].update(value=employee_entry[0])
    window[elements.EmployeeForm.SURNAME].update(value=employee_entry[1])
    window[elements.EmployeeForm.PATRONYMIC].update(value=employee_entry[2])


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

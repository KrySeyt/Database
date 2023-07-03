from typing import Any

import PySimpleGUI as sg

from app.service import storage
from .keys import Key
from . import events
from . import elements
from . import user_input
from .errors_handlers import wrong_data_exception_handler


def show_wrong_employee_data(window: sg.Window, error: storage.backend.WrongData) -> None:
    element_keys = []
    for err in error.errors:
        key = f"-EMPLOYEE-{'-'.join(err.loc[1:])}-".upper().replace("_", "-")
        element_keys.append(key)

    for key in element_keys:
        window[key].update(background_color="red")


def clear_wrong_employee_data(window: sg.Window) -> None:
    for key in elements.EmployeeForm:
        window[key].update(background_color="white")


def add_employee(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:

    employee = user_input.Employee.get_employee(values)

    @wrong_data_exception_handler(
        storage.backend.WrongData,
        show_wrong_employee_data,
        window
    )
    @events.raise_status_events(
        window,
        events.EmployeeEvent.ADD_EMPLOYEE_SUCCESS,
        events.EmployeeEvent.ADD_EMPLOYEE_PROCESSING,
        events.EmployeeEvent.ADD_EMPLOYEE_FAIL
    )
    def call_add_employee() -> storage.schema.Employee:
        return storage.service.add_employee(employee, backend)

    window.perform_long_operation(call_add_employee, end_key=events.Misc.NON_EXISTENT)


def update_employee(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:

    if not values[events.EmployeeEvent.EMPLOYEE_SELECTED]:
        return

    employee_id_in_list = values[events.EmployeeEvent.EMPLOYEE_SELECTED][-1]
    employee_id = window[events.EmployeeEvent.EMPLOYEE_SELECTED].get()[employee_id_in_list][0]
    employee = user_input.Employee.get_employee(values)

    employee_with_id = storage.schema.EmployeeInWithID(
        **employee.dict(),
        id=employee_id
    )

    @wrong_data_exception_handler(
        storage.backend.WrongData,
        show_wrong_employee_data,
        window
    )
    @events.raise_status_events(
        window,
        events.EmployeeEvent.UPDATE_EMPLOYEE_SUCCESS,
        events.EmployeeEvent.UPDATE_EMPLOYEE_PROCESSING,
        events.EmployeeEvent.UPDATE_EMPLOYEE_FAIL
    )
    def call_update_employee() -> storage.schema.Employee:
        return storage.service.update_employee(employee_with_id, backend)

    window.perform_long_operation(call_update_employee, end_key=events.Misc.NON_EXISTENT)


def delete_employees(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:

    selected_employees_ids_in_list = values[events.EmployeeEvent.EMPLOYEE_SELECTED]
    all_employees_in_list = window[events.EmployeeEvent.EMPLOYEE_SELECTED].get()
    selected_employees_ids = [int(all_employees_in_list[i][0]) for i in selected_employees_ids_in_list]

    @events.raise_status_events(
        window,
        events.EmployeeEvent.DELETE_EMPLOYEES_SUCCESS,
        events.EmployeeEvent.DELETE_EMPLOYEES_PROCESSING,
        events.EmployeeEvent.DELETE_EMPLOYEES_FAIL
    )
    def call_delete_employees() -> list[storage.schema.Employee]:
        return storage.service.delete_employees(selected_employees_ids, backend)

    window.perform_long_operation(call_delete_employees, end_key=events.Misc.NON_EXISTENT)


def search_employees(
        window: sg.Window,
        values: dict[Key, Any],
) -> None:

    search_attrs_as_entry = [
        values[elements.EmployeeForm.NAME] or None,
        values[elements.EmployeeForm.SURNAME] or None,
        values[elements.EmployeeForm.PATRONYMIC] or None
    ]

    if not any(search_attrs_as_entry):
        return

    employees_entries = window[events.EmployeeEvent.EMPLOYEE_SELECTED].get()

    matched_entries_numbers = []
    for entry_number, entry in enumerate(employees_entries):
        for i, employee_attr in enumerate(entry[1:]):  # Skip employee ID
            if employee_attr == search_attrs_as_entry[i]:
                matched_entries_numbers.append(entry_number)
                continue

    window[events.EmployeeEvent.EMPLOYEE_SELECTED].update(select_rows=matched_entries_numbers)


def update_employees(window: sg.Window, backend: storage.backend.StorageBackend) -> None:

    @events.raise_status_events(
        window,
        events.EmployeeEvent.GET_EMPLOYEES_SUCCESS,
        events.EmployeeEvent.GET_EMPLOYEES_PROCESSING,
        events.EmployeeEvent.GET_EMPLOYEES_FAIL
    )
    def call_get_employees() -> list[storage.schema.Employee]:
        return storage.service.get_employees(0, 100, backend)

    window.perform_long_operation(call_get_employees, end_key=events.Misc.NON_EXISTENT)


def show_employees(window: sg.Window, values: dict[Key, Any]) -> None:
    employees = values[events.EmployeeEvent.GET_EMPLOYEES_SUCCESS]
    employees_out = [storage.schema.EmployeeOut(**i.dict()) for i in employees]

    table_rows = []
    for emp in employees_out:
        table_rows.append(
            [
                emp.id, emp.name, emp.surname, emp.patronymic, emp.service_number, emp.department_number,
                str(emp.employment_date), emp.topic.number, emp.topic.name, emp.post.code, emp.post.name,
                emp.salary.amount, emp.salary.currency.name, ", ".join([title.name for title in emp.titles])
            ]
        )

    window[events.EmployeeEvent.EMPLOYEE_SELECTED].update(values=table_rows)


def insert_selected_employee_to_form(
        window: sg.Window,
        values: dict[Key, Any]
) -> None:

    assert values[events.EmployeeEvent.EMPLOYEE_SELECTED]

    employee_id_in_list = values[events.EmployeeEvent.EMPLOYEE_SELECTED][-1]
    employee_entry_in_list = window[events.EmployeeEvent.EMPLOYEE_SELECTED].get()[employee_id_in_list]

    window[elements.EmployeeForm.NAME].update(value=employee_entry_in_list[1])
    window[elements.EmployeeForm.SURNAME].update(value=employee_entry_in_list[2])
    window[elements.EmployeeForm.PATRONYMIC].update(value=employee_entry_in_list[3])


def show_success(window: sg.Window) -> None:
    window[elements.Misc.OPERATION_STATUS_FIELD].update(
        value="Success!",
        text_color="white",
        background_color="green",
        visible=True,
    )


def show_fail(window: sg.Window) -> None:
    window[elements.Misc.OPERATION_STATUS_FIELD].update(
        value="Fail!",
        text_color="white",
        background_color="red",
        visible=True,
    )


def show_processing(window: sg.Window) -> None:
    window[elements.Misc.OPERATION_STATUS_FIELD].update(
        value="Processing...",
        text_color="white",
        background_color="grey",
        visible=True,
    )


def close_window(window: sg.Window) -> None:
    window.close()
    assert window.is_closed()

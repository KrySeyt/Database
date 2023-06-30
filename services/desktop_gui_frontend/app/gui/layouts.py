import PySimpleGUI as sg

from .elements import EmployeeForm
from .events import EmployeeEvent, AppEvent


MAIN_WINDOW_LAYOUT = [
    [sg.Table(
        headings=["ID", "Name", "Surname", "Patronymic"], values=[], key=EmployeeEvent.EMPLOYEE_SELECTED,
        auto_size_columns=False, max_col_width=1000, def_col_width=30, vertical_scroll_only=False,
        enable_events=True, num_rows=40
    )],
    [sg.Text('Name:', size=(15, 1)), sg.Input(key=EmployeeForm.NAME)],
    [sg.Text('Surname:', size=(15, 1)), sg.Input(key=EmployeeForm.SURNAME)],
    [sg.Text('Patronymic:', size=(15, 1)), sg.Input(key=EmployeeForm.PATRONYMIC)],
    [sg.Button('Add employee', key=EmployeeEvent.ADD_EMPLOYEE),
     sg.Button("Update employee", key=EmployeeEvent.UPDATE_EMPLOYEE),
     sg.Button("Delete employee", key=EmployeeEvent.DELETE_EMPLOYEES),
     sg.Button("Search employee", key=EmployeeEvent.SEARCH_EMPLOYEES),
     sg.Exit(key=AppEvent.EXIT), sg.Text(key=EmployeeForm.ADD_EMPLOYEE_STATUS, visible=False)]
]

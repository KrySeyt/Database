import PySimpleGUI as sg

from .elements import EmployeeForm, EmployeeList
from .events import EmployeeEvent, AppEvent


MAIN_WINDOW_LAYOUT = [
    [sg.Table(headings=["Name", "Surname", "Patronymic"], values=[], key=EmployeeList.TABLE,
              auto_size_columns=False, max_col_width=1000, def_col_width=30, vertical_scroll_only=False)],
    [sg.Text('First name:', size=(15, 1)), sg.Input(key=EmployeeForm.FIRST_NAME)],
    [sg.Text('Last name:', size=(15, 1)), sg.Input(key=EmployeeForm.LAST_NAME)],
    [sg.Text('Patronymic:', size=(15, 1)), sg.Input(key=EmployeeForm.PATRONYMIC)],
    [sg.Button('Add employee', key=EmployeeEvent.ADD_EMPLOYEE), sg.Exit(key=AppEvent.EXIT),
     sg.Button(key="-GET-INFO-BUTTON-"), sg.Text(key=EmployeeForm.ADD_EMPLOYEE_STATUS, visible=False)]
]

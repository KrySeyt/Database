import PySimpleGUI as sg

from .elements import AddEmployeeForm
from .events import EmployeeEvent, ExitEvent


MAIN_WINDOW_LAYOUT = [
    [sg.Text('First name:', size=(15, 1)), sg.Input(key=AddEmployeeForm.FIRST_NAME)],
    [sg.Text('Last name:', size=(15, 1)), sg.Input(key=AddEmployeeForm.LAST_NAME)],
    [sg.Text('Patronymic:', size=(15, 1)), sg.Input(key=AddEmployeeForm.PATRONYMIC)],
    [sg.Button('Add employee', key=EmployeeEvent.ADD_EMPLOYEE), sg.Exit(key=ExitEvent.EXIT),
     sg.Text(key=AddEmployeeForm.ADD_EMPLOYEE_STATUS, visible=False)]
]

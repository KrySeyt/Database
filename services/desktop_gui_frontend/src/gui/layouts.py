import PySimpleGUI as sg

from .elements import EmployeeInput
from .events import EmployeeEvent


MAIN_WINDOW_LAYOUT = [
    [sg.Text('First name:', size=(15, 1)), sg.Input(key=EmployeeInput.FIRST_NAME)],
    [sg.Text('Last name:', size=(15, 1)), sg.Input(key=EmployeeInput.LAST_NAME)],
    [sg.Text('Patronymic:', size=(15, 1)), sg.Input(key=EmployeeInput.PATRONYMIC)],
    [sg.Button('Add employee', key=EmployeeEvent.ADD_EMPLOYEE), sg.Exit()]
]

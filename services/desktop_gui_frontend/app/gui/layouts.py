import PySimpleGUI as sg

from .elements import EmployeeForm, Misc
from .events import EmployeeEvent, AppEvent


MAIN_WINDOW_LAYOUT = [
    [sg.Table(
        headings=["ID", "Name", "Surname", "Patronymic", "Service number", "Department number", "Employment date",
                  "Topic number", "Topic name", "Post code", "Post name", "Salary amount", "Salary currency", "Titles"],
        values=[], key=EmployeeEvent.EMPLOYEE_SELECTED,
        auto_size_columns=False, max_col_width=1000, def_col_width=15, vertical_scroll_only=False,
        enable_events=True, num_rows=30
    )],
    [sg.Text("Name:", size=(15, 1)), sg.Input(key=EmployeeForm.NAME, default_text="Name"),
     sg.Text("Topic number:", size=(15, 1)), sg.Input(key=EmployeeForm.TOPIC_NUMBER, size=(4, 1), default_text="1")],
    [sg.Text("Surname:", size=(15, 1)), sg.Input(key=EmployeeForm.SURNAME, default_text="Surname"),
     sg.Text("Topic name:", size=(15, 1)), sg.Input(key=EmployeeForm.TOPIC_NAME, size=(15, 1), default_text="Topic")],
    [sg.Text("Patronymic:", size=(15, 1)), sg.Input(key=EmployeeForm.PATRONYMIC, default_text="Patronymic"),
     sg.Text("Post code:", size=(15, 1)), sg.Input(key=EmployeeForm.POST_CODE, size=(15, 1), default_text="1")],
    [sg.Text("Service number:", size=(15, 1)), sg.Input(key=EmployeeForm.SERVICE_NUMBER, size=(5, 1), default_text="1"),
     sg.Text("Employment date:", size=(15, 1)), sg.Input(key=EmployeeForm.EMPLOYMENT_DATE, size=(10, 1),
                                                         default_text="2023-07-03"),
     sg.Text("Post name:", size=(15, 1)), sg.Input(key=EmployeeForm.POST_NAME, size=(15, 1), default_text="Post")],
    [sg.Text("Titles:", size=(15, 1)), sg.Input(key=EmployeeForm.TITLES, size=(15, 1), default_text="First, Second"),
     sg.Text("Department number:", size=(15, 1)), sg.Input(key=EmployeeForm.DEPARTMENT_NUMBER, size=(15, 1),
                                                           default_text="1")],
    [sg.Text("Salary amount:", size=(15, 1)), sg.Input(key=EmployeeForm.SALARY_AMOUNT, size=(15, 1),
                                                       default_text="1500"),
     sg.Text("Salary currency:", size=(15, 1)), sg.Input(key=EmployeeForm.SALARY_CURRENCY, size=(15, 1),
                                                         default_text="USD")],
    [sg.Button('Add employee', key=EmployeeEvent.ADD_EMPLOYEE),
     sg.Button("Update employee", key=EmployeeEvent.UPDATE_EMPLOYEE),
     sg.Button("Delete employee", key=EmployeeEvent.DELETE_EMPLOYEES),
     sg.Button("Search employee", key=EmployeeEvent.SEARCH_EMPLOYEES),
     sg.Exit(key=AppEvent.EXIT), sg.Text(key=Misc.OPERATION_STATUS_FIELD, visible=False)]
]

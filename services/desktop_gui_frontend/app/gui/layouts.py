# You should to deepcopy layout when you create a window, not use layout directly,
# because layout must be unique for window

import PySimpleGUI as sg

from .elements import EmployeeForm, Misc as ElementsMisc, Statistics, Forecasts, Diagrams
from .events import EmployeeEvent, WindowEvent, StatisticsEvent, ForecastsEvent, Misc as EventsMisc

MAIN_WINDOW_LAYOUT = [
    [sg.Table(
        headings=[
            "ID", "Name", "Surname", "Patronymic", "Service number", "Department number", "Employment date",
            "Work duration in months", "Topic number", "Topic name", "Post code", "Post name", "Salary amount",
            "Salary currency", "Titles"
        ],
        col_widths=[
            6, 20, 20, 20, 15, 20, 15, 20, 15, 30, 15, 30, 15, 15, 40
        ],
        values=[], key=EmployeeEvent.EMPLOYEE_SELECTED,
        auto_size_columns=False, max_col_width=1000, vertical_scroll_only=False,
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
     sg.Exit(key=WindowEvent.EXIT), sg.Text(key=ElementsMisc.OPERATION_STATUS_FIELD, visible=False)],
    [sg.Button("Statistics", key=WindowEvent.OPEN_STATISTICS_WINDOW),
     sg.Button("Forecasts", key=WindowEvent.OPEN_FORECASTS_WINDOW)],
    [sg.Text(visible=False, key=ElementsMisc.MESSAGE_FIELD)]
]

STATISTICS_WINDOW_LAYOUT = [
    [sg.Button("Max work duration", key=StatisticsEvent.SHOW_MAX_WORK_DURATION),
     sg.Text("Count:"), sg.Input(default_text="3", key=Statistics.MAX_WORK_DURATION_EMPLOYEES_COUNT)],
    [sg.Button("Highest paid employees", key=StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES),
     sg.Text("Count:"), sg.Input(default_text="3", key=Statistics.HIGHEST_PAID_EMPLOYEES_COUNT)],
    [sg.Button("Title employees growth history", key=StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY),
     sg.Text("Title name:"), sg.Input(key=Statistics.TITLE_EMPLOYEES_GROWTH_HISTORY_TITLE_NAME)],
    [sg.Button("Employees distribution by titles", key=StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES)],
    [sg.Button("Employees distribution by topics", key=StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS)],
    [sg.Text(key=ElementsMisc.OPERATION_STATUS_FIELD, visible=False)]
]

DIAGRAM_WINDOW = [
    [sg.Canvas(key=Diagrams.DIAGRAM_CANVAS, expand_x=True, expand_y=True)]
]

STATISTICS_MAX_WORK_DURATION_EMPLOYEES_GRAPH_WINDOW = [
    [sg.Canvas(key=Statistics.MAX_WORK_DURATION_EMPLOYEES_CANVAS, expand_x=True, expand_y=True)]
]

STATISTICS_HIGHEST_PAID_EMPLOYEES_GRAPH_WINDOW = [
    [sg.Canvas(key=Statistics.HIGHEST_PAID_EMPLOYEES_CANVAS, expand_x=True, expand_y=True)]
]

STATISTICS_TITLE_EMPLOYEES_GROWTH_HISTORY_GRAPH_WINDOW = [
    [sg.Canvas(key=Statistics.TITLE_EMPLOYEES_GROWTH_HISTORY_CANVAS, expand_x=True, expand_y=True)]
]

STATISTICS_EMPLOYEES_DISTRIBUTION_BY_TITLES_GRAPH_WINDOW = [
    [sg.Canvas(key=Statistics.EMPLOYEES_DISTRIBUTION_BY_TITLES_CANVAS, expand_x=True, expand_y=True)]
]

STATISTICS_EMPLOYEES_DISTRIBUTION_BY_TOPICS_GRAPH_WINDOW = [
    [sg.Canvas(key=Statistics.EMPLOYEES_DISTRIBUTION_BY_TOPICS_CANVAS, expand_x=True, expand_y=True)]
]

FORECASTS_WINDOW_LAYOUT = [
    [sg.Button("Title employees growth", key=ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST)],
    [sg.Text("Title name:"), sg.Input(key=Forecasts.TITLE_EMPLOYEES_GROWTH_FORECAST_TITLE_NAME)],
    [sg.Text("Years count:"), sg.Input(key=Forecasts.TITLE_EMPLOYEES_GROWTH_FORECAST_YEARS_COUNT)],
    [sg.Text(key=ElementsMisc.OPERATION_STATUS_FIELD, visible=False)]
]

FORECASTS_TITLE_EMPLOYEES_GROWTH_FORECAST_GRAPH_WINDOW = [
    [sg.Canvas(key=Forecasts.TITLE_EMPLOYEES_GROWTH_FORECAST_CANVAS, expand_x=True, expand_y=True)]
]

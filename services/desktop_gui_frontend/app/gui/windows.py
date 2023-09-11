import datetime
from typing import Any
from abc import ABC
from copy import deepcopy

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
from matplotlib.figure import Figure  # type: ignore
from dateutil.relativedelta import relativedelta

from ..service.mixins import Observer
from ..service.storage import schema
from ..service import ServiceFactory, StorageService
from . import elements
from . import keys
from . import layouts
from . import events
from . import gui
from . import commands


# PySimpleGUI have no typing stubs
class AppWindow(sg.Window, ABC):  # type: ignore
    layout: list[list[sg.Element]]

    def __init__(
            self,
            title: str,
            parent_gui: "gui.GUI",
            events_handlers: dict[events.Event, commands.Command],
            *args: Any,
            **kwargs: Any
    ) -> None:

        super().__init__(title, *args, **kwargs)
        self.parent_gui = parent_gui
        self.events_handlers = events_handlers

    def handle_event(self, event: events.Event, values: dict[keys.Key, Any]) -> None:
        if event in self.events_handlers:
            self.events_handlers[event](self, values)


class MainWindow(AppWindow, Observer):
    def __init__(self, observable_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__("Database", layout=deepcopy(layouts.MAIN_WINDOW_LAYOUT), *args, **kwargs)
        self.table_employees: list[schema.Employee] = []
        observable_service.attach_observer(self)

    def update_employees_table(self, employees: list[schema.Employee]) -> None:
        self.table_employees = employees
        self.refresh_employees_table()

    def refresh_employees_table(self) -> None:
        employees_out = [schema.EmployeeOut(**i.dict()) for i in self.table_employees]

        table_rows = []
        for emp in employees_out:
            work_duration_timedelta = relativedelta(datetime.date.today(), emp.employment_date)
            work_duration_in_months = (work_duration_timedelta.years * 12) + work_duration_timedelta.months
            table_rows.append(
                [
                    emp.id, emp.name, emp.surname, emp.patronymic, emp.service_number, emp.department_number,
                    str(emp.employment_date), str(work_duration_in_months), emp.topic.number, emp.topic.name,
                    emp.post.code,
                    emp.post.name, emp.salary.amount,
                    emp.salary.currency.name, ", ".join([title.name for title in emp.titles])
                ]
            )

        self[events.EmployeeEvent.EMPLOYEE_SELECTED].update(values=table_rows)

    def get_employee(self) -> schema.EmployeeIn:
        return schema.EmployeeIn(
            name=self[elements.EmployeeForm.NAME].get(),
            surname=self[elements.EmployeeForm.SURNAME].get(),
            patronymic=self[elements.EmployeeForm.PATRONYMIC].get(),
            service_number=self[elements.EmployeeForm.SERVICE_NUMBER].get(),
            department_number=self[elements.EmployeeForm.DEPARTMENT_NUMBER].get(),
            employment_date=self[elements.EmployeeForm.EMPLOYMENT_DATE].get(),
            titles=self.get_titles(),
            post=self.get_post(),
            topic=self.get_topic(),
            salary=self.get_salary()
        )

    def get_topic(self) -> schema.TopicIn:
        return schema.TopicIn(
            name=self[elements.EmployeeForm.TOPIC_NAME].get(),
            number=self[elements.EmployeeForm.TOPIC_NUMBER].get()
        )

    def get_post(self) -> schema.PostIn:
        return schema.PostIn(
            name=self[elements.EmployeeForm.POST_NAME].get(),
            code=self[elements.EmployeeForm.POST_CODE].get()
        )

    def get_salary(self) -> schema.SalaryIn:
        return schema.SalaryIn(
            amount=self[elements.EmployeeForm.SALARY_AMOUNT].get(),
            currency=self.get_currency(),
        )

    def get_currency(self) -> schema.CurrencyIn:
        return schema.CurrencyIn(name=self[elements.EmployeeForm.SALARY_CURRENCY].get())

    def get_titles(self) -> list[schema.TitleIn]:
        return [schema.TitleIn(name=title_name) for title_name in self[elements.EmployeeForm.TITLES].get().split(", ")]

    def show_operation_status(self, status: events.OperationStatus) -> None:
        text = ""
        background_color = "white"

        match status:
            case events.OperationStatus.SUCCESS:
                text = "Success!"
                background_color = "green"

            case events.OperationStatus.PROCESSING:
                text = "Processing..."
                background_color = "grey"

            case events.OperationStatus.FAILED:
                text = "Fail!"
                background_color = "red"

        self[elements.Misc.OPERATION_STATUS_FIELD].update(
            value=text,
            text_color="white",
            background_color=background_color,
            visible=True,
        )

    def show_errors(self, errors_fields: list[elements.EmployeeForm]) -> None:
        for field in errors_fields:
            self[field].update(background_color="red")

    def show_error_message(self, message: str) -> None:
        self[elements.Misc.MESSAGE_FIELD].update(
            visible=True,
            text_color="white",
            background_color="red",
            value=message
        )

    def notify(self) -> None:
        self.write_event_value(events.EmployeeEvent.REFRESH_EMPLOYEES_TABLE, None)


class StatisticsWindow(AppWindow):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__("Statistics", layout=deepcopy(layouts.STATISTICS_WINDOW_LAYOUT), *args, **kwargs)


class DiagramWindow(AppWindow):
    def __init__(self, title: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(title, layout=deepcopy(layouts.DIAGRAM_WINDOW), *args, **kwargs)

    def draw_figure(self, figure: Figure) -> None:
        canvas = self[elements.Diagrams.DIAGRAM_CANVAS].TKCanvas
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


class WindowsFactory:
    def __init__(self, service_factory: ServiceFactory) -> None:
        self.storage_service = service_factory.create_storage_service()
        self.statistics_service = service_factory.create_statistics_service()

    def create_main_window(self, parent_gui: "gui.GUI") -> MainWindow:
        main_window_events_handlers = {
            events.WindowEvent.OPEN: commands.RefreshEmployeesTable(self.storage_service),
            events.WindowEvent.EXIT: commands.CloseAllWindows(),
            events.WindowEvent.CLOSED: commands.CloseAllWindows(),
            events.EmployeeEvent.REFRESH_EMPLOYEES_TABLE: commands.RefreshEmployeesTable(self.storage_service),
            events.EmployeeEvent.SHOW_EMPLOYEES: commands.ShowEmployees(),
            events.EmployeeEvent.ADD_EMPLOYEE: commands.AddEmployee(self.storage_service),
            events.EmployeeEvent.UPDATE_EMPLOYEE: commands.UpdateEmployee(self.storage_service),
            events.EmployeeEvent.DELETE_EMPLOYEES: commands.DeleteEmployees(self.storage_service),
            events.WindowEvent.OPEN_STATISTICS_WINDOW: commands.OpenStatisticsWindow(),
            events.OperationStatus.SUCCESS: commands.ShowStatus(events.OperationStatus.SUCCESS),
            events.OperationStatus.PROCESSING: commands.ShowStatus(events.OperationStatus.PROCESSING),
            events.OperationStatus.FAILED: commands.MultiCommand([
                commands.ShowStatus(events.OperationStatus.FAILED),
                commands.ShowWrongEmployeeData(),
                ])
        }
        return MainWindow(
            parent_gui=parent_gui,
            observable_service=self.storage_service,
            events_handlers=main_window_events_handlers,
            location=(200, 200),
            size=(1000, 850),
            finalize=True,
            resizable=True,
        )

    def create_statistics_window(self, parent_gui: "gui.GUI") -> StatisticsWindow:
        statistics_window_events_handlers = {
            events.WindowEvent.CLOSED: commands.CloseWindow(),
            events.StatisticsEvent.SHOW_MAX_WORK_DURATION: commands.ShowMaxWorkDuration(self.statistics_service),
            events.StatisticsEvent.SHOW_MAX_WORK_DURATION_DIAGRAM: commands.ShowDiagramMaxWorkDurationDiagram(),
            events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES: commands.ShowHighestPaidEmployees(
                self.statistics_service
            ),
            events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_DIAGRAM: commands.ShowHighestPaidEmployeesDiagram()
        }
        return StatisticsWindow(
            parent_gui=parent_gui,
            events_handlers=statistics_window_events_handlers,
            location=(400, 800),
            size=(800, 300),
            finalize=True,
            resizable=True,
        )

    def create_diagram_window(self, title: str, parent_gui: "gui.GUI") -> DiagramWindow:
        diagram_window_events_handlers: dict[events.Event, commands.Command] = {}
        return DiagramWindow(
            title=title,
            parent_gui=parent_gui,
            events_handlers=diagram_window_events_handlers,
            location=(400, 400),
            size=(800, 800),
            element_justification="center",
            finalize=True,
            resizable=True,
        )


def read_all_windows(
        timeout: int | None = None,
        timeout_key: keys.Key = sg.TIMEOUT_KEY
) -> tuple[AppWindow, events.Event, dict[keys.Key, Any] | None]:

    window, event, values = sg.read_all_windows(timeout, timeout_key)
    assert isinstance(window, AppWindow) or not window, f"All windows must be subclasses of {__file__}.AppWindow"
    return window, event, values

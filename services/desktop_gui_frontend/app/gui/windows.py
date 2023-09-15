import datetime
from typing import Any, Iterable
from abc import ABC, abstractmethod
from copy import deepcopy

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
from matplotlib.figure import Figure  # type: ignore
from dateutil.relativedelta import relativedelta

from ..service.forecasts.exceptions import WrongForecastsData
from ..service.statistics.exceptions import WrongStatisticsData
from ..service.storage.exceptions import WrongEmployeeData
from ..service.exceptions import WrongData
from ..service.mixins import Observer
from ..service.storage import schema
from ..service import ServiceFactory, StorageService
from ..diagrams.diagrams import DiagramsFactory
from .errors_handling import (
    get_wrong_employee_data_fields,
    get_wrong_forecasts_data_fields,
    get_wrong_statistics_data_fields
)
from . import elements
from . import keys
from . import layouts
from . import events
from . import gui
from . import commands


# PySimpleGUI have no typing stubs
class WindowWithOperationStatus(sg.Window, ABC):  # type: ignore
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


class CanShowErrors(ABC):
    @abstractmethod
    def show_errors(self, exception: WrongData) -> None:
        raise NotImplementedError

    @abstractmethod
    def hide_errors(self) -> None:
        raise NotImplementedError


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


class MainWindow(AppWindow, WindowWithOperationStatus, CanShowErrors, Observer):
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

    def show_errors(self, exception: WrongData) -> None:
        if isinstance(exception, WrongEmployeeData):
            employee_errors_fields = get_wrong_employee_data_fields(exception)
            self.show_employee_form_errors(employee_errors_fields)

    def show_employee_form_errors(self, fields: Iterable[elements.EmployeeForm]) -> None:
        for field in fields:
            self[field].update(background_color="red")

    def hide_errors(self) -> None:
        self.hide_employee_form_errors()
        self.hide_error_message()

    def hide_employee_form_errors(self) -> None:
        for field in elements.EmployeeForm:
            self[field].update(background_color="white")

    def show_error_message(self, message: str) -> None:
        self[elements.Misc.MESSAGE_FIELD].update(
            visible=True,
            text_color="white",
            background_color="red",
            value=message
        )

    def hide_error_message(self) -> None:
        self[elements.Misc.MESSAGE_FIELD].update(
            visible=False
        )

    def notify(self) -> None:
        self.write_event_value(events.EmployeeEvent.REFRESH_EMPLOYEES_TABLE, None)


class StatisticsWindow(AppWindow, WindowWithOperationStatus, CanShowErrors):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__("Statistics", layout=deepcopy(layouts.STATISTICS_WINDOW_LAYOUT), *args, **kwargs)

    def get_max_work_duration_employees_count(self) -> int:
        element = elements.Statistics.MAX_WORK_DURATION_EMPLOYEES_COUNT
        try:
            return int(self[element].get())
        except ValueError:
            raise WrongStatisticsData(errors_places=[(element.value,)])

    def get_highest_paid_employees_count(self) -> int:
        element = elements.Statistics.HIGHEST_PAID_EMPLOYEES_COUNT
        try:
            return int(self[element].get())
        except ValueError:
            raise WrongStatisticsData(errors_places=[(element.value,)])

    def get_title_employees_growth_title_name(self) -> str:
        element = elements.Statistics.TITLE_EMPLOYEES_GROWTH_HISTORY_TITLE_NAME
        title_name = str(self[element].get())
        if not title_name:
            raise WrongStatisticsData(errors_places=[(element.value,)])
        return title_name

    def show_errors(self, exception: WrongData) -> None:
        if isinstance(exception, WrongStatisticsData):
            errors_fields = get_wrong_statistics_data_fields(exception)
            self.show_statistics_fields_errors(errors_fields)

    def show_statistics_fields_errors(self, fields: Iterable[elements.Statistics]) -> None:
        for field in fields:
            self[field].update(background_color="red")

    def hide_errors(self) -> None:
        self.hide_errors_fields()

    def hide_errors_fields(self) -> None:
        for field in elements.Statistics:
            self[field].update(background_color="white")


class ForecastsWindow(AppWindow, WindowWithOperationStatus, CanShowErrors):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__("Forecasts", layout=deepcopy(layouts.FORECASTS_WINDOW_LAYOUT), *args, **kwargs)

    def get_title_employees_growth_title_name(self) -> str:
        element = elements.Forecasts.TITLE_EMPLOYEES_GROWTH_FORECAST_TITLE_NAME
        title_name = str(self[element].get())
        if not title_name:
            raise WrongForecastsData(errors_places=[(element.value,)])
        return title_name

    def get_title_employees_growth_years_count(self) -> int:
        element = elements.Forecasts.TITLE_EMPLOYEES_GROWTH_FORECAST_YEARS_COUNT
        try:
            return int(self[element].get())
        except ValueError:
            raise WrongForecastsData(errors_places=[(element.value,)])

    def show_errors(self, exception: WrongData) -> None:
        if isinstance(exception, WrongForecastsData):
            errors_fields = get_wrong_forecasts_data_fields(exception)
            self.show_forecasts_fields_errors(errors_fields)

    def show_forecasts_fields_errors(self, fields: Iterable[elements.Forecasts]) -> None:
        for field in fields:
            self[field].update(background_color="red")

    def hide_errors(self) -> None:
        self.hide_errors_fields()

    def hide_errors_fields(self) -> None:
        for field in elements.Forecasts:
            self[field].update(background_color="white")


class DiagramWindow(AppWindow):
    def __init__(self, title: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(title, layout=deepcopy(layouts.DIAGRAM_WINDOW), *args, **kwargs)

    def draw_diagram(self, figure: Figure) -> None:
        canvas = self[elements.Diagrams.DIAGRAM_CANVAS].TKCanvas
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


class WindowsFactory:
    def __init__(self, service_factory: ServiceFactory, diagrams_factory: DiagramsFactory) -> None:
        self.storage_service = service_factory.create_storage_service()
        self.statistics_service = service_factory.create_statistics_service()
        self.forecasts_service = service_factory.create_forecasts_service()
        self.diagrams_factory = diagrams_factory

    def create_main_window(self, parent_gui: "gui.GUI") -> MainWindow:
        main_window_events_handlers = {
            events.WindowEvent.OPEN:
                commands.RefreshEmployeesTable(self.storage_service),
            events.WindowEvent.EXIT:
                commands.CloseAllWindows(),
            events.WindowEvent.CLOSED:
                commands.CloseAllWindows(),
            events.EmployeeEvent.REFRESH_EMPLOYEES_TABLE:
                commands.RefreshEmployeesTable(self.storage_service),
            events.EmployeeEvent.SHOW_EMPLOYEES:
                commands.ShowEmployees(),
            events.EmployeeEvent.ADD_EMPLOYEE:
                commands.MultiCommand(
                    commands.HideErrors(),
                    commands.AddEmployee(self.storage_service)
                ),
            events.EmployeeEvent.UPDATE_EMPLOYEE:
                commands.MultiCommand(
                    commands.HideErrors(),
                    commands.UpdateEmployee(self.storage_service),
                ),
            events.EmployeeEvent.DELETE_EMPLOYEES:
                commands.MultiCommand(
                    commands.HideErrors(),
                    commands.DeleteEmployees(self.storage_service),
                ),
            events.WindowEvent.OPEN_STATISTICS_WINDOW:
                commands.OpenStatisticsWindow(),
            events.WindowEvent.OPEN_FORECASTS_WINDOW:
                commands.OpenForecastsWindow(),
            events.OperationStatus.SUCCESS:
                commands.ShowStatus(events.OperationStatus.SUCCESS),
            events.OperationStatus.PROCESSING:
                commands.ShowStatus(events.OperationStatus.PROCESSING),
            events.OperationStatus.FAILED:
                commands.MultiCommand(
                    commands.ShowStatus(events.OperationStatus.FAILED),
                    commands.ShowWrongData(),
                )
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
            events.WindowEvent.EXIT:
                commands.CloseWindow(),
            events.WindowEvent.CLOSED:
                commands.CloseWindow(),
            events.StatisticsEvent.SHOW_MAX_WORK_DURATION:
                commands.MultiCommand(
                    commands.HideErrors(),
                    commands.ShowMaxWorkDuration(self.statistics_service)
                ),
            events.StatisticsEvent.SHOW_MAX_WORK_DURATION_DIAGRAM:
                commands.ShowDiagramMaxWorkDurationDiagram(self.diagrams_factory),
            events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES:
                commands.MultiCommand(
                    commands.HideErrors(),
                    commands.ShowHighestPaidEmployees(self.statistics_service),
                ),
            events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_DIAGRAM:
                commands.ShowHighestPaidEmployeesDiagram(self.diagrams_factory),
            events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY:
                commands.MultiCommand(
                    commands.HideErrors(),
                    commands.ShowTitleEmployeesGrowthHistory(self.statistics_service),
                ),
            events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_DIAGRAM:
                commands.ShowTitleEmployeesGrowthHistoryDiagram(self.diagrams_factory),
            events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES:
                commands.MultiCommand(
                    commands.HideErrors(),
                    commands.ShowEmployeesDistributionByTitles(self.storage_service),
                ),
            events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_DIAGRAM:
                commands.ShowEmployeesDistributionByTitlesDiagram(self.diagrams_factory),
            events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS:
                commands.MultiCommand(
                    commands.HideErrors(),
                    commands.ShowEmployeesDistributionByTopics(self.storage_service),
                ),
            events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_DIAGRAM:
                commands.ShowEmployeesDistributionByTopicsDiagram(self.diagrams_factory),
            events.OperationStatus.SUCCESS:
                commands.ShowStatus(events.OperationStatus.SUCCESS),
            events.OperationStatus.PROCESSING:
                commands.ShowStatus(events.OperationStatus.PROCESSING),
            events.OperationStatus.FAILED:
                commands.MultiCommand(
                    commands.ShowStatus(events.OperationStatus.FAILED),
                    commands.ShowWrongData()
                )

        }
        return StatisticsWindow(
            parent_gui=parent_gui,
            events_handlers=statistics_window_events_handlers,
            location=(400, 800),
            size=(800, 300),
            finalize=True,
            resizable=True,
        )

    def create_forecasts_window(self, parent_gui: "gui.GUI") -> ForecastsWindow:
        forecasts_window_events_handlers = {
            events.WindowEvent.EXIT:
                commands.CloseWindow(),
            events.WindowEvent.CLOSED:
                commands.CloseWindow(),
            events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST:
                commands.MultiCommand(
                    commands.HideErrors(),
                    commands.ShowTitleEmployeesGrowthForecast(self.forecasts_service),
                ),
            events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST_DIAGRAM:
                commands.ShowTitleEmployeesGrowthForecastDiagram(self.diagrams_factory),
            events.OperationStatus.SUCCESS:
                commands.ShowStatus(events.OperationStatus.SUCCESS),
            events.OperationStatus.PROCESSING:
                commands.ShowStatus(events.OperationStatus.PROCESSING),
            events.OperationStatus.FAILED:
                commands.MultiCommand(
                    commands.ShowStatus(events.OperationStatus.FAILED),
                    commands.ShowWrongData()
                )
        }
        return ForecastsWindow(
            parent_gui=parent_gui,
            events_handlers=forecasts_window_events_handlers,
            location=(400, 800),
            size=(800, 300),
            finalize=True,
            resizable=True,
        )

    def create_diagram_window(self, title: str, parent_gui: "gui.GUI") -> DiagramWindow:
        diagram_window_events_handlers: dict[events.Event, commands.Command] = {
            events.WindowEvent.EXIT: commands.CloseWindow(),
            events.WindowEvent.CLOSED: commands.CloseWindow(),
        }
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

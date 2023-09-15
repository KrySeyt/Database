from abc import ABC, abstractmethod
from typing import Any

import matplotlib.pyplot as plt  # type: ignore
from matplotlib.figure import Figure  # type: ignore

from ..service.forecasts.exceptions import WrongForecastsData
from ..service.statistics.exceptions import WrongStatisticsData
from ..service.storage import schema
from ..service.exceptions import ServiceError, WrongData
from ..service import StorageService, StatisticsService, ForecastsService
from ..diagrams.diagrams import DiagramsFactory
from .keys import Key
from . import windows
from . import events
from . import elements


# TODO: Add commands reverting


class Command(ABC):
    @abstractmethod
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        raise NotImplementedError


class MultiCommand(Command):
    def __init__(self, *commands: Command) -> None:
        self.commands = commands

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        for command in self.commands:
            command(event_window, values)


class AddEmployee(Command):
    def __init__(self, storage_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.storage_service = storage_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.MainWindow):
            return

        employee = event_window.get_employee()
        event_window.write_event_value(events.OperationStatus.PROCESSING, None)

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            ServiceError,
            suppress_exception=True
        )
        def operation() -> schema.Employee:
            return self.storage_service.add_employee(employee)

        event_window.perform_long_operation(operation, events.Misc.NON_EXISTENT)


class UpdateEmployee(Command):
    def __init__(self, storage_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.storage_service = storage_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.MainWindow):
            return

        employee_id_in_list = values[events.EmployeeEvent.EMPLOYEE_SELECTED][-1]
        employee = event_window.table_employees[employee_id_in_list]
        new_employee_data = event_window.get_employee()

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            ServiceError,
            suppress_exception=True
        )
        def operation() -> schema.Employee:
            return self.storage_service.update_employee(new_employee_data, employee.id)

        event_window.perform_long_operation(operation, events.Misc.NON_EXISTENT)


class DeleteEmployees(Command):
    def __init__(self, storage_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.storage_service = storage_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.MainWindow):
            return

        selected_employees_ids_in_list = values[events.EmployeeEvent.EMPLOYEE_SELECTED]
        selected_employees = [event_window.table_employees[i] for i in selected_employees_ids_in_list]
        selected_employees_ids = [employee.id for employee in selected_employees]

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            ServiceError,
            suppress_exception=True
        )
        def operation() -> list[schema.Employee]:
            return self.storage_service.delete_employees(selected_employees_ids)

        event_window.perform_long_operation(operation, events.Misc.NON_EXISTENT)


class RefreshEmployeesTable(Command):
    def __init__(self, storage_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.storage_service = storage_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.MainWindow):
            return

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            ServiceError,
            suppress_exception=True
        )
        def operation() -> list[schema.Employee]:
            return self.storage_service.get_employees(0, 99999)

        event_window.perform_long_operation(operation, events.EmployeeEvent.SHOW_EMPLOYEES)


class ShowEmployees(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.MainWindow):
            return

        employees = values[events.EmployeeEvent.SHOW_EMPLOYEES]
        event_window.update_employees_table(employees)


class ShowWrongData(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:

        if not isinstance(event_window, windows.CanShowErrors):
            return

        wrong_data_exception = values[events.OperationStatus.FAILED]

        if not isinstance(wrong_data_exception, WrongData):
            return

        event_window.show_errors(wrong_data_exception)


class HideErrors(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.CanShowErrors):
            return

        event_window.hide_errors()


class CloseWindow(Command):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        event_window.close()


class CloseAllWindows(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        event_window.parent_gui.exit()


class ShowStatus(Command):
    def __init__(self, status: events.OperationStatus) -> None:
        self.status = status

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.WindowWithOperationStatus):
            return

        event_window.show_operation_status(self.status)


class OpenStatisticsWindow(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        gui = event_window.parent_gui
        gui.create_statistics_window()


class ShowMaxWorkDuration(Command):
    def __init__(self, statistics_service: StatisticsService) -> None:
        self.statistics_service = statistics_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.StatisticsWindow):
            return

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=WrongStatisticsData,
            suppress_exception=True
        )
        def get_employees_count() -> int:
            return event_window.get_max_work_duration_employees_count()

        employees_count = get_employees_count()

        if not employees_count:
            return

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=ServiceError,
            suppress_exception=True
        )
        def operation() -> list[schema.Employee]:
            return self.statistics_service.get_max_work_duration_employees(employees_count)

        event_window.perform_long_operation(operation, events.StatisticsEvent.SHOW_MAX_WORK_DURATION_DIAGRAM)


class ShowDiagramMaxWorkDurationDiagram(Command):
    def __init__(self, diagrams_factory: DiagramsFactory) -> None:
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        employees = values[events.StatisticsEvent.SHOW_MAX_WORK_DURATION_DIAGRAM]
        if employees is None:
            return

        diagram = self.diagrams_factory.create_max_employees_work_duration_diagram(employees)
        diagram_window = event_window.parent_gui.create_diagram_window("Max work duration")
        diagram_window.draw_diagram(diagram)


class ShowHighestPaidEmployees(Command):
    def __init__(self, statistics_service: StatisticsService) -> None:
        self.statistics_service = statistics_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.StatisticsWindow):
            return

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=WrongStatisticsData,
            suppress_exception=True
        )
        def get_employees_count() -> int:
            return event_window.get_highest_paid_employees_count()

        employees_count = get_employees_count()

        if not employees_count:
            return

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=ServiceError,
            suppress_exception=True
        )
        def operation() -> list[schema.Employee]:
            return self.statistics_service.get_max_work_duration_employees(employees_count)

        event_window.perform_long_operation(operation, events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_DIAGRAM)


class ShowHighestPaidEmployeesDiagram(Command):
    def __init__(self, diagrams_factory: DiagramsFactory) -> None:
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        highest_paid_employees = values[events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_DIAGRAM]
        if highest_paid_employees is None:
            return

        diagram = self.diagrams_factory.create_highest_paid_employees_diagram(highest_paid_employees)
        diagram_window = event_window.parent_gui.create_diagram_window("Highest paid employees")
        diagram_window.draw_diagram(diagram)


class ShowTitleEmployeesGrowthHistory(Command):
    def __init__(self, statistics_service: StatisticsService) -> None:
        self.statistics_service = statistics_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.StatisticsWindow):
            return

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=WrongStatisticsData,
            suppress_exception=True
        )
        def get_title_name() -> str:
            return event_window.get_title_employees_growth_title_name()

        title_name = get_title_name()

        if title_name is None:
            return

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=ServiceError,
            suppress_exception=True
        )
        def operation() -> dict[int, int]:
            growth_history = self.statistics_service.get_title_employees_history_growth(title_name)
            if not growth_history:
                raise WrongStatisticsData(errors_places=[("-TITLE-EMPLOYEES-GROWTH-HISTORY-TITLE-NAME-",)])
            return growth_history

        event_window.perform_long_operation(
            operation,
            events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_DIAGRAM
        )


class ShowTitleEmployeesGrowthHistoryDiagram(Command):
    def __init__(self, diagrams_factory: DiagramsFactory) -> None:
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        titles_employees_growth_history = values[events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_DIAGRAM]
        diagram = self.diagrams_factory.create_title_employees_growth_diagram(titles_employees_growth_history)
        diagram_window = event_window.parent_gui.create_diagram_window("Title employees count growth history")
        diagram_window.draw_diagram(diagram)


class ShowEmployeesDistributionByTitles(Command):
    def __init__(self, storage_service: StorageService) -> None:
        self.storage_service = storage_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=ServiceError,
            suppress_exception=True
        )
        def operation() -> list[schema.Employee]:
            return self.storage_service.get_employees(0, 999999999999)

        event_window.perform_long_operation(
            operation,
            events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_DIAGRAM
        )


class ShowEmployeesDistributionByTitlesDiagram(Command):
    def __init__(self, diagrams_factory: DiagramsFactory) -> None:
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        employees = values[events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_DIAGRAM]
        if employees is None:
            return

        diagram = self.diagrams_factory.create_employees_distribution_by_titles_diagram(employees)
        diagram_window = event_window.parent_gui.create_diagram_window("Employees distribution by titles")
        diagram_window.draw_diagram(diagram)


class ShowEmployeesDistributionByTopics(Command):
    def __init__(self, storage_service: StorageService) -> None:
        self.storage_service = storage_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=ServiceError,
            suppress_exception=True
        )
        def operation() -> list[schema.Employee]:
            return self.storage_service.get_employees(0, 999999999999)

        event_window.perform_long_operation(
            operation,
            events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_DIAGRAM
        )


class ShowEmployeesDistributionByTopicsDiagram(Command):
    def __init__(self, diagrams_factory: DiagramsFactory) -> None:
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        employees = values[events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_DIAGRAM]
        if employees is None:
            return

        diagram = self.diagrams_factory.create_employees_distribution_by_topics_diagram(employees)
        diagram_window = event_window.parent_gui.create_diagram_window("Employees distribution by topics")
        diagram_window.draw_diagram(diagram)


class OpenForecastsWindow(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        gui = event_window.parent_gui
        gui.create_forecasts_window()


class ShowTitleEmployeesGrowthForecast(Command):
    def __init__(self, forecasts_service: ForecastsService) -> None:
        self.forecasts_service = forecasts_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.ForecastsWindow):
            return

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=WrongForecastsData,
            suppress_exception=True
        )
        def get_title_name() -> str:
            return event_window.get_title_employees_growth_title_name()

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=WrongForecastsData,
            suppress_exception=True
        )
        def get_years_count() -> int:
            return event_window.get_title_employees_growth_years_count()

        title_name = get_title_name()
        years_count = get_years_count()

        if title_name is None or years_count is None:
            return

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            handle_exception_type=ServiceError,
            suppress_exception=True
        )
        def operation() -> dict[int, int]:
            growth_forecast = self.forecasts_service.get_title_employees_forecast_growth(title_name, years_count)
            if not growth_forecast:
                raise WrongForecastsData(errors_places=[
                    (elements.Forecasts.TITLE_EMPLOYEES_GROWTH_FORECAST_TITLE_NAME.value,)
                ])
            return growth_forecast

        event_window.perform_long_operation(
            operation,
            events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST_DIAGRAM
        )


class ShowTitleEmployeesGrowthForecastDiagram(Command):
    def __init__(self, diagrams_factory: DiagramsFactory) -> None:
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        titles_employees_growth_forecast = values[events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST_DIAGRAM]
        if titles_employees_growth_forecast is None:
            return

        diagram = self.diagrams_factory.create_title_employees_growth_diagram(titles_employees_growth_forecast)
        diagram_window = event_window.parent_gui.create_diagram_window("Title employees count growth forecast")
        diagram_window.draw_diagram(diagram)

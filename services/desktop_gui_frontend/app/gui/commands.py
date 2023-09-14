import datetime
from abc import ABC, abstractmethod
from collections import Counter
from typing import Any

import matplotlib.pyplot as plt  # type: ignore
from matplotlib.figure import Figure  # type: ignore
from dateutil import relativedelta

from ..service.forecasts.exceptions import WrongForecastsData
from ..service.statistics.exceptions import WrongStatisticsData
from ..service.storage.exceptions import WrongEmployeeData
from ..service.storage import schema
from ..service.exceptions import ServiceError, WrongData
from ..service import StorageService, StatisticsService, ForecastsService
from .keys import Key
from . import windows
from . import events
from . import elements


# TODO: Add commands reverting
# TODO: Move diagrams building to special class/classes


class Command(ABC):
    @abstractmethod
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        raise NotImplementedError


class MultiCommand(Command):
    def __init__(self, commands: list[Command]) -> None:
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
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        employees = values[events.StatisticsEvent.SHOW_MAX_WORK_DURATION_DIAGRAM]

        if not employees:
            return

        employees_count = len(employees)

        today = datetime.date.today()
        employees_names = []
        work_durations_in_month = []
        for emp in employees:
            work_timedelta = relativedelta.relativedelta(today, emp.employment_date)
            work_months = (work_timedelta.years * 12) + work_timedelta.months
            work_durations_in_month.append(work_months)

            emp_name = f"{emp.name}\n{emp.surname}\n{emp.patronymic}\n({emp.id})"
            employees_names.append(emp_name)

        max_work_duration = max(work_durations_in_month)
        figure, ax = plt.subplots(figsize=(3 * employees_count, (0.2 * max_work_duration) + 2),
                                  layout='constrained')
        ax.bar(employees_names, work_durations_in_month)

        for i, duration in enumerate(work_durations_in_month):
            ax.annotate(duration, xy=(i, duration))

        diagram_window = event_window.parent_gui.create_diagram_window("Max work duration")
        diagram_window.draw_figure(figure)


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
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        highest_paid_employees = values[events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_DIAGRAM]

        if not highest_paid_employees:
            return

        employees_names = []
        employees_salaries_sizes_places: list[int] = []
        for i in range(len(highest_paid_employees)):
            if not employees_salaries_sizes_places:
                employees_salaries_sizes_places.append(1)
            elif highest_paid_employees[i].salary.amount == highest_paid_employees[i - 1].salary.amount and \
                    highest_paid_employees[i].salary.currency.name == highest_paid_employees[
                i - 1].salary.currency.name:
                employees_salaries_sizes_places.append(employees_salaries_sizes_places[-1])
            else:
                employees_salaries_sizes_places.append(employees_salaries_sizes_places[-1] + 1)

        employees_salaries_reprs = []
        for emp in highest_paid_employees:
            emp_salary_repr = f"{emp.salary.amount} {emp.salary.currency.name}"
            employees_salaries_reprs.append(emp_salary_repr)

            emp_name = f"{emp.name}\n{emp.surname}\n{emp.patronymic}\n({emp.id})"
            employees_names.append(emp_name)

        employees_count = len(highest_paid_employees)
        figure, ax = plt.subplots(
            figsize=(3 * employees_count, max(employees_salaries_sizes_places) + 2),
            layout='constrained'
        )

        graphs_sizes = [max(employees_salaries_sizes_places) - i + 1 for i in employees_salaries_sizes_places]
        ax.bar(employees_names, graphs_sizes)

        plt.yticks([])

        for i, salary_place in enumerate(employees_salaries_sizes_places):
            ax.annotate(employees_salaries_reprs[i], xy=(i, graphs_sizes[i]))

        diagram_window = event_window.parent_gui.create_diagram_window("Highest paid employees")
        diagram_window.draw_figure(figure)


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

        if not title_name:
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
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        titles_employees_growth_history = values[events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_DIAGRAM]

        if not titles_employees_growth_history:
            return

        years = []
        employees_growth_per_year = []
        for year in titles_employees_growth_history:
            years.append(year)
            employees_growth_per_year.append(titles_employees_growth_history[year])

        max_employees_growth = max(employees_growth_per_year)
        figure, ax = plt.subplots(figsize=(20, max_employees_growth + 2), layout='constrained')

        ax.bar(years, employees_growth_per_year)
        plt.xticks(years)
        plt.yticks(employees_growth_per_year)

        for i, year in enumerate(years):
            ax.annotate(employees_growth_per_year[i], xy=(year, employees_growth_per_year[i]))

        diagram_window = event_window.parent_gui.create_diagram_window("Title employees count growth history")
        diagram_window.draw_figure(figure)


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
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        employees = values[events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_DIAGRAM]

        if not employees:
            return

        emps_count_per_title: Counter[str] = Counter()
        for emp in employees:
            for title in emp.titles:
                emps_count_per_title[title.name] += 1

        figure, ax = plt.subplots(figsize=(
            20,
            10
        ), layout='constrained')

        titles: list[str] = []
        emps_counts: list[int] = []
        for title in emps_count_per_title:
            titles.append(title)
            emps_counts.append(emps_count_per_title[title])

        ax.bar(titles, emps_counts)
        plt.xticks(titles)
        plt.yticks(emps_counts)

        for i, emps_count in enumerate(emps_counts):
            ax.annotate(emps_count, xy=(i, emps_count))

        diagram_window = event_window.parent_gui.create_diagram_window("Employees distribution by titles")
        diagram_window.draw_figure(figure)


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
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        employees = values[events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_DIAGRAM]

        if not employees:
            return

        emps_count_per_topic: Counter[str] = Counter()
        for emp in employees:
            emps_count_per_topic[emp.topic.name] += 1

        figure, ax = plt.subplots(figsize=(
            20,
            10
        ), layout='constrained')

        topics: list[str] = []
        emps_counts: list[int] = []
        for topic in emps_count_per_topic:
            topics.append(topic)
            emps_counts.append(emps_count_per_topic[topic])

        ax.bar(topics, emps_counts)
        plt.xticks(topics)
        plt.yticks(emps_counts)

        for i, emps_count in enumerate(emps_counts):
            ax.annotate(emps_count, xy=(i, emps_count))

        diagram_window = event_window.parent_gui.create_diagram_window("Employees distribution by topics")
        diagram_window.draw_figure(figure)


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

        if not title_name or not years_count:
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
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        titles_employees_growth_forecast = values[events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST_DIAGRAM]

        if not titles_employees_growth_forecast:
            return

        years = []
        employees_growth_per_year = []
        for year in titles_employees_growth_forecast:
            years.append(year)
            employees_growth_per_year.append(titles_employees_growth_forecast[year])

        max_employees_growth = max(employees_growth_per_year)
        figure, ax = plt.subplots(figsize=(20, max_employees_growth + 2), layout='constrained')

        ax.bar(years, employees_growth_per_year)
        plt.xticks(years)
        plt.yticks(employees_growth_per_year)

        for i, year in enumerate(years):
            ax.annotate(employees_growth_per_year[i], xy=(year, employees_growth_per_year[i]))

        diagram_window = event_window.parent_gui.create_diagram_window("Title employees count growth forecast")
        diagram_window.draw_figure(figure)

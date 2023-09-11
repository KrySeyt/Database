import datetime
from abc import ABC, abstractmethod
from typing import Any

import matplotlib.pyplot as plt  # type: ignore
from matplotlib.figure import Figure  # type: ignore
from dateutil import relativedelta

from ..service.storage.exceptions import WrongEmployeeData
from ..service.storage import schema
from ..service.exceptions import ServiceError
from ..service import StorageService, StatisticsService
from .keys import Key
from .errors_handling import get_wrong_employee_data_fields
from . import windows
from . import events
from . import elements


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
            suppress_exception=False
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
            suppress_exception=False
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
            suppress_exception=False
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


class ShowWrongEmployeeData(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:

        if not isinstance(event_window, windows.MainWindow):
            return

        wrong_data_exception = values[events.OperationStatus.FAILED]

        if not isinstance(wrong_data_exception, WrongEmployeeData):
            return

        wrong_data_fields = get_wrong_employee_data_fields(wrong_data_exception)
        event_window.show_errors(wrong_data_fields)

        error_message = wrong_data_exception.messages[0]
        event_window.show_error_message(error_message)


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
        if not isinstance(event_window, windows.MainWindow):
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
        employees_count = values[elements.Statistics.MAX_WORK_DURATION_EMPLOYEES_COUNT]

        def operation() -> list[schema.Employee]:
            return self.statistics_service.get_max_work_duration_employees(employees_count)

        event_window.perform_long_operation(operation, events.StatisticsEvent.SHOW_MAX_WORK_DURATION_DIAGRAM)


class ShowDiagramMaxWorkDurationDiagram(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        employees = values[events.StatisticsEvent.SHOW_MAX_WORK_DURATION_DIAGRAM]
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
        employees_count = values[elements.Statistics.HIGHEST_PAID_EMPLOYEES_COUNT]

        def operation() -> list[schema.Employee]:
            return self.statistics_service.get_max_work_duration_employees(employees_count)

        event_window.perform_long_operation(operation, events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_DIAGRAM)


class ShowHighestPaidEmployeesDiagram(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        highest_paid_employees = values[events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_DIAGRAM]

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

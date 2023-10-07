from abc import ABC, abstractmethod
from typing import Any

import matplotlib.pyplot as plt  # type: ignore
from matplotlib.figure import Figure  # type: ignore

from app.service.forecasts.exceptions import WrongForecastsData
from app.service.statistics.exceptions import WrongStatisticsData
from app.service.storage import schema
from app.service.exceptions import ServiceError, WrongData
from app.service import StorageService, StatisticsService, ForecastsService
from app.diagrams.diagrams import DiagramsFactory
from app.gui.commands import editors
from app.gui.commands import history
from app.gui.keys import Key
from app.gui import windows
from app.gui import events
from app.gui import elements


class Command(ABC):
    def __init__(self, commands_history: "history.CommandsHistory") -> None:
        self.commands_history = commands_history
        
    @abstractmethod
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        raise NotImplementedError

    def reverse(self) -> None:
        pass

    # TODO: Change to memento
    def copy(self) -> "Command":
        return type(self)(**self.__dict__)

    def accept_editing(self, editor: "editors.CommandEditor") -> None:
        pass


class MultiCommand(Command):
    def __init__(
            self, *commands: Command,
            local_commands_history: "history.MultiCommandHistory | None" = None,
            **kwargs: Any
    ) -> None:

        super().__init__(**kwargs)
        self.commands = list(commands)
        self.local_commands_history = local_commands_history or self.create_local_commands_history()
        for cmd in self.commands:
            cmd.commands_history = self.local_commands_history

    def create_local_commands_history(self) -> "history.MultiCommandHistory":
        return history.MultiCommandHistory(self.commands_history)

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        self.local_commands_history.clear()

        for cmd in self.commands:
            cmd(event_window, values)

        self.commands_history.add_command(self.copy())

    def reverse(self) -> None:
        if self.local_commands_history:
            self.local_commands_history.revert_all()
        else:
            self.commands_history.revert_prev_command()

    def copy(self) -> "MultiCommand":
        cmd_copy = MultiCommand(
            *self.commands,
            commands_history=self.commands_history,
            local_commands_history=self.local_commands_history
        )

        # Commands adds to history with some delay in another thread, they are linked to our local commands history.
        # Because of this we are using local history copy for this instance, not for history copy
        self.local_commands_history = self.local_commands_history.copy()
        self.commands = [cmd.copy() for cmd in self.commands]
        for cmd in self.commands:
            cmd.commands_history = self.local_commands_history

        return cmd_copy

    def accept_editing(self, editor: "editors.CommandEditor") -> None:
        editor.edit_multicommand(self)


class RevertCommand(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        self.commands_history.revert_prev_command()


class AddEmployee(Command):
    def __init__(self, storage_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.storage_service = storage_service
        self.added_employee_id: int | None = None

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.MainWindow):
            return

        employee = event_window.get_employee()

        @events.raise_status_events(
            event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            ServiceError,
            suppress_exception=True
        )
        def add_employee() -> schema.Employee:
            added_employee = self.storage_service.add_employee(employee)
            self.added_employee_id = added_employee.id
            self.commands_history.add_command(self.copy())
            return added_employee

        event_window.perform_long_operation(add_employee, events.Misc.NON_EXISTENT)

    def reverse(self) -> None:
        if self.added_employee_id:
            self.storage_service.delete_employees([self.added_employee_id])

    def copy(self) -> "AddEmployee":
        command = AddEmployee(self.storage_service, self.commands_history)
        command.added_employee_id = self.added_employee_id
        return command

    def accept_editing(self, editor: "editors.CommandEditor") -> None:
        editor.edit_add_employee(self)


class UpdateEmployee(Command):
    def __init__(self, storage_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.storage_service = storage_service
        self.employee_before_update: schema.Employee | None = None
        self.event_window: windows.AppWindow | None = None

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
            updated_employee = self.storage_service.update_employee(new_employee_data, employee.id)
            self.commands_history.add_command(self.copy())
            return updated_employee

        self.employee_before_update = employee
        self.event_window = event_window

        event_window.perform_long_operation(operation, events.Misc.NON_EXISTENT)

    def reverse(self) -> None:
        if not self.employee_before_update or not self.event_window:
            return

        employee_in = schema.EmployeeIn(**self.employee_before_update.dict())
        employee_id = self.employee_before_update.id

        @events.raise_status_events(
            self.event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            ServiceError,
            suppress_exception=True
        )
        def operation() -> schema.Employee:
            return self.storage_service.update_employee(
                employee_in,
                employee_id
            )

        self.event_window.perform_long_operation(operation, events.Misc.NON_EXISTENT)

    def copy(self) -> "UpdateEmployee":
        command = UpdateEmployee(self.storage_service, self.commands_history)
        command.employee_before_update = self.employee_before_update
        command.event_window = self.event_window
        return command

    def accept_editing(self, editor: "editors.CommandEditor") -> None:
        editor.edit_update_employee(self)


class DeleteEmployees(Command):
    def __init__(self, storage_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.storage_service = storage_service
        self.deleted_employees: list[schema.Employee] = []
        self.event_window: windows.AppWindow | None = None

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
            deleted_employees = self.storage_service.delete_employees(selected_employees_ids)
            self.commands_history.add_command(self.copy())
            return deleted_employees

        self.deleted_employees = selected_employees
        self.event_window = event_window

        event_window.perform_long_operation(operation, events.Misc.NON_EXISTENT)

    def reverse(self) -> None:
        if not self.deleted_employees or not self.event_window:
            return

        @events.raise_status_events(
            self.event_window,
            events.OperationStatus.SUCCESS,
            events.OperationStatus.PROCESSING,
            events.OperationStatus.FAILED,
            ServiceError,
            suppress_exception=True
        )
        def create_employees() -> list[schema.Employee]:
            created_employees = []
            for employee in self.deleted_employees:
                created_employee = self.storage_service.add_employee(schema.EmployeeIn(**employee.dict()))
                created_employees.append(created_employee)

            self.commands_history.employees_ids_changed(
                [emp.id for emp in self.deleted_employees],
                [emp.id for emp in created_employees]
            )

            return created_employees

        self.event_window.perform_long_operation(create_employees, events.Misc.NON_EXISTENT)

    def copy(self) -> "DeleteEmployees":
        command = DeleteEmployees(self.storage_service, self.commands_history)
        command.deleted_employees = self.deleted_employees
        command.event_window = self.event_window
        return command

    def accept_editing(self, editor: "editors.CommandEditor") -> None:
        editor.edit_delete_employees(self)


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
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        event_window.close()


class CloseAllWindows(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        event_window.parent_gui.exit()


class ShowStatus(Command):
    def __init__(self, status: events.OperationStatus, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.status = status

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.WindowWithOperationStatus):
            return

        event_window.show_operation_status(self.status)


class SearchEmployees(Command):
    def __init__(self, storage_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.storage_service = storage_service

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.MainWindow):
            return

        search_model = event_window.get_employee_search_model()

        if not search_model:
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
            return self.storage_service.search_employees(search_model)

        event_window.perform_long_operation(operation, events.EmployeeEvent.SELECT_EMPLOYEES)


class SelectEmployeesInTable(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        if not isinstance(event_window, windows.MainWindow):
            return

        employees = values[events.EmployeeEvent.SELECT_EMPLOYEES]
        
        if not employees:
            return

        event_window.select_employees_rows([emp.id for emp in employees])


class OpenStatisticsWindow(Command):
    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        gui = event_window.parent_gui
        gui.create_statistics_window()


class ShowMaxWorkDuration(Command):
    def __init__(self, statistics_service: StatisticsService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
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
    def __init__(self, diagrams_factory: DiagramsFactory, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        employees = values[events.StatisticsEvent.SHOW_MAX_WORK_DURATION_DIAGRAM]
        if employees is None:
            return

        diagram = self.diagrams_factory.create_max_employees_work_duration_diagram(employees)
        diagram_window = event_window.parent_gui.create_diagram_window("Max work duration")
        diagram_window.draw_diagram(diagram)


class ShowHighestPaidEmployees(Command):
    def __init__(self, statistics_service: StatisticsService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
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
    def __init__(self, diagrams_factory: DiagramsFactory, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        highest_paid_employees = values[events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_DIAGRAM]
        if highest_paid_employees is None:
            return

        diagram = self.diagrams_factory.create_highest_paid_employees_diagram(highest_paid_employees)
        diagram_window = event_window.parent_gui.create_diagram_window("Highest paid employees")
        diagram_window.draw_diagram(diagram)


class ShowTitleEmployeesGrowthHistory(Command):
    def __init__(self, statistics_service: StatisticsService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
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
    def __init__(self, diagrams_factory: DiagramsFactory, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        titles_employees_growth_history = values[events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_DIAGRAM]
        diagram = self.diagrams_factory.create_title_employees_growth_diagram(titles_employees_growth_history)
        diagram_window = event_window.parent_gui.create_diagram_window("Title employees count growth history")
        diagram_window.draw_diagram(diagram)


class ShowEmployeesDistributionByTitles(Command):
    def __init__(self, storage_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
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
    def __init__(self, diagrams_factory: DiagramsFactory, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        employees = values[events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_DIAGRAM]
        if employees is None:
            return

        diagram = self.diagrams_factory.create_employees_distribution_by_titles_diagram(employees)
        diagram_window = event_window.parent_gui.create_diagram_window("Employees distribution by titles")
        diagram_window.draw_diagram(diagram)


class ShowEmployeesDistributionByTopics(Command):
    def __init__(self, storage_service: StorageService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
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
    def __init__(self, diagrams_factory: DiagramsFactory, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
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
    def __init__(self, forecasts_service: ForecastsService, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
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
    def __init__(self, diagrams_factory: DiagramsFactory, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.diagrams_factory = diagrams_factory

    def __call__(self, event_window: "windows.AppWindow", values: dict[Key, Any]) -> None:
        titles_employees_growth_forecast = values[events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST_DIAGRAM]
        if titles_employees_growth_forecast is None:
            return

        diagram = self.diagrams_factory.create_title_employees_growth_diagram(titles_employees_growth_forecast)
        diagram_window = event_window.parent_gui.create_diagram_window("Title employees count growth forecast")
        diagram_window.draw_diagram(diagram)

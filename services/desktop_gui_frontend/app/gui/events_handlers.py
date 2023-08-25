from typing import Any

import PySimpleGUI as sg

from app.service import ServiceFactory
from .keys import Key
from . import events
from . import service


class EventsHandler:
    def __init__(self, service_factory: ServiceFactory) -> None:
        self.service_factory = service_factory

    def handle_event(
            self,
            window: sg.Window,
            event: events.Event,
            values: dict[Key, Any],
    ) -> None:

        match event:
            case events.EmployeeEvent.EMPLOYEE_SELECTED:
                self._employee_entry_selected_handler(window, values)

            case events.EmployeeEvent.GET_EMPLOYEES_SUCCESS:
                self._get_employees_success_handler(window, values)

            case events.EmployeeEvent.GET_EMPLOYEES_PROCESSING:
                self._get_employees_processing_handler(window, values)

            case events.EmployeeEvent.GET_EMPLOYEES_FAIL:
                self._get_employees_fail_handler(window, values)

            case events.EmployeeEvent.ADD_EMPLOYEE:
                self._add_employee_handler(window, values)

            case events.EmployeeEvent.ADD_EMPLOYEE_SUCCESS:
                self._add_employee_success_handler(window, values)

            case events.EmployeeEvent.ADD_EMPLOYEE_PROCESSING:
                self._add_employee_processing_handler(window, values)

            case events.EmployeeEvent.ADD_EMPLOYEE_FAIL:
                self._add_employee_fail_handler(window, values)

            case events.EmployeeEvent.UPDATE_EMPLOYEE:
                self._update_employee_handler(window, values)

            case events.EmployeeEvent.UPDATE_EMPLOYEE_SUCCESS:
                self._update_employee_success_handler(window, values)

            case events.EmployeeEvent.UPDATE_EMPLOYEE_PROCESSING:
                self._update_employee_processing_handler(window, values)

            case events.EmployeeEvent.UPDATE_EMPLOYEE_FAIL:
                self._update_employee_fail_handler(window, values)

            case events.EmployeeEvent.DELETE_EMPLOYEES:
                self._delete_employees_handler(window, values)

            case events.EmployeeEvent.DELETE_EMPLOYEES_SUCCESS:
                self._delete_employees_success_handler(window, values)

            case events.EmployeeEvent.DELETE_EMPLOYEES_PROCESSING:
                self._delete_employees_processing_handler(window, values)

            case events.EmployeeEvent.DELETE_EMPLOYEES_FAIL:
                self._delete_employees_fail_handler(window, values)

            case events.EmployeeEvent.SEARCH_EMPLOYEES:
                self._search_employees_handler(window, values)

            case events.StatisticsEvent.SHOW_MAX_WORK_DURATION_EMPLOYEES:
                self._show_max_work_duration_employees_handler(window, values)

            case events.StatisticsEvent.SHOW_MAX_WORK_DURATION_EMPLOYEES_SUCCESS:
                self._show_max_work_duration_employees_success_handler(window, values)

            case events.StatisticsEvent.SHOW_MAX_WORK_DURATION_EMPLOYEES_PROCESSING:
                self._show_max_work_duration_employees_processing_handler(window, values)

            case events.StatisticsEvent.SHOW_MAX_WORK_DURATION_EMPLOYEES_FAIL:
                self._show_max_work_duration_employees_fail_handler(window, values)

            case events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES:
                self._show_highest_paid_employees_handler(window, values)

            case events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_SUCCESS:
                self._show_highest_paid_employees_success_handler(window, values)

            case events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_PROCESSING:
                self._show_highest_paid_employees_processing_handler(window, values)

            case events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_FAIL:
                self._show_highest_paid_employees_fail_handler(window, values)

            case events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY:
                self._show_title_employees_growth_history_handler(window, values)

            case events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_SUCCESS:
                self._show_title_employees_growth_history_success_handler(window, values)

            case events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_PROCESSING:
                self._show_title_employees_growth_history_processing_handler(window, values)

            case events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_FAIL:
                self._show_title_employees_growth_history_fail_handler(window, values)

            case events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES:
                self._show_employees_distribution_by_titles_handler(window, values)

            case events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_SUCCESS:
                self._show_employees_distribution_by_titles_success_handler(window, values)

            case events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_PROCESSING:
                self._show_employees_distribution_by_titles_processing_handler(window, values)

            case events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_FAIL:
                self._show_employees_distribution_by_titles_fail_handler(window, values)

            case events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS:
                self._show_employees_distribution_by_topics_handler(window, values)

            case events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_SUCCESS:
                self._show_employees_distribution_by_topics_success_handler(window, values)

            case events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_PROCESSING:
                self._show_employees_distribution_by_topics_processing_handler(window, values)

            case events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_FAIL:
                self._show_employees_distribution_by_topics_fail_handler(window, values)

            case events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST:
                self._show_title_employees_growth_forecast_handler(window, values)

            case events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST_SUCCESS:
                self._show_title_employees_growth_forecast_success_handler(window, values)

            case events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST_PROCESSING:
                self._show_title_employees_growth_forecast_processing_handler(window, values)

            case events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST_FAIL:
                self._show_title_employees_growth_forecast_fail_handler(window, values)

            case events.WindowEvent.OPEN_STATISTICS_WINDOW:
                self._open_statistics_window_handler(window, values)

            case events.WindowEvent.OPEN_FORECASTS_WINDOW:
                self._open_forecasts_window_handler(window, values)

            case events.WindowEvent.OPEN:
                self._startup_handler(window, values)

            case events.WindowEvent.CLOSE:
                self._exit_handler(window, values)

    def _get_employees_success_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.show_employees(window, values)
        service.show_success(window)

    def _get_employees_fail_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.show_fail(window)

    def _get_employees_processing_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.show_processing(window)

    def _add_employee_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.clear_wrong_employee_data(window)

        storage_service = self.service_factory.create_storage_service()
        service.add_employee(window, values, storage_service)

    def _add_employee_success_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.show_success(window)
        storage_service = self.service_factory.create_storage_service()
        service.update_employees_list(window, storage_service)

    @staticmethod
    def _add_employee_fail_handler(
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.show_fail(window)

    @staticmethod
    def _add_employee_processing_handler(
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.show_processing(window)

    def _update_employee_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.clear_wrong_employee_data(window)

        storage_service = self.service_factory.create_storage_service()
        service.update_employee(window, values, storage_service)

    def _update_employee_success_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_success(window)
        storage_service = self.service_factory.create_storage_service()
        service.update_employees_list(window, storage_service)

    def _update_employee_processing_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_processing(window)

    def _update_employee_fail_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_fail(window)


    def _delete_employees_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        storage_service = self.service_factory.create_storage_service()
        service.delete_employees(window, values, storage_service)

    def _delete_employees_success_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_success(window)
        storage_service = self.service_factory.create_storage_service()
        service.update_employees_list(window, storage_service)

    def _delete_employees_processing_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_processing(window)

    def _delete_employees_fail_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_fail(window)

    def _search_employees_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.search_employees(window, values)

    def _startup_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        storage_service = self.service_factory.create_storage_service()
        service.update_employees_list(window, storage_service)

    def _employee_entry_selected_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        if values[events.EmployeeEvent.EMPLOYEE_SELECTED]:
            service.insert_selected_employee_to_form(window, values)

    def _open_statistics_window_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.open_statistics_window(window)

    def _open_forecasts_window_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.open_forecasts_window(window)

    def _show_max_work_duration_employees_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        statistics_service = self.service_factory.create_statistics_service()
        service.show_max_work_duration_employees(window, values, statistics_service)

    def _show_max_work_duration_employees_success_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_success(window)
        service.show_max_work_duration_employees_graph(window, values)

    def _show_max_work_duration_employees_processing_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_processing(window)

    def _show_max_work_duration_employees_fail_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_fail(window)

    def _show_highest_paid_employees_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        statistics_service = self.service_factory.create_statistics_service()
        service.show_highest_paid_employees(window, values, statistics_service)

    def _show_highest_paid_employees_success_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_success(window)
        service.show_highest_paid_employees_graph(window, values)

    def _show_highest_paid_employees_processing_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_processing(window)

    def _show_highest_paid_employees_fail_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_fail(window)

    def _show_title_employees_growth_history_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        statistics_service = self.service_factory.create_statistics_service()
        service.show_title_employees_history_growth(window, values, statistics_service)

    def _show_title_employees_growth_history_success_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_success(window)
        service.show_title_employees_history_growth_graph(window, values)

    def _show_title_employees_growth_history_processing_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_processing(window)

    def _show_title_employees_growth_history_fail_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_fail(window)

    def _show_employees_distribution_by_titles_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        storage_service = self.service_factory.create_storage_service()
        service.show_employees_distribution_by_titles(window, values, storage_service)

    def _show_employees_distribution_by_titles_success_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_success(window)
        service.show_employees_distribution_by_titles_graph(window, values)

    def _show_employees_distribution_by_titles_processing_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_processing(window)

    def _show_employees_distribution_by_titles_fail_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_fail(window)

    def _show_employees_distribution_by_topics_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        storage_service = self.service_factory.create_storage_service()
        service.show_employees_distribution_by_topics(window, values, storage_service)

    def _show_employees_distribution_by_topics_success_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_success(window)
        service.show_employees_distribution_by_topics_graph(window, values)

    def _show_employees_distribution_by_topics_processing_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_processing(window)

    def _show_employees_distribution_by_topics_fail_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_fail(window)

    def _show_title_employees_growth_forecast_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        forecasts_service = self.service_factory.create_forecasts_service()
        service.show_title_employees_forecast_growth(window, values, forecasts_service)

    def _show_title_employees_growth_forecast_success_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_success(window)
        service.show_employees_distribution_by_titles_graph(window, values)

    def _show_title_employees_growth_forecast_processing_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_processing(window)

    def _show_title_employees_growth_forecast_fail_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any],
    ) -> None:

        service.show_fail(window)

    def _exit_handler(
            self,
            window: sg.Window,
            values: dict[Key, Any]
    ) -> None:

        service.close_window(window)

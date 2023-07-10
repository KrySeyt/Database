import datetime
from collections import Counter
from copy import deepcopy
from typing import Any

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib
import PySimpleGUI as sg
from dateutil import relativedelta

from app.service import storage
from .keys import Key
from . import events
from . import elements
from . import user_input
from . import windows
from . import layouts
from .errors_handlers import wrong_data_exception_handler

matplotlib.use("TkAgg")


def show_wrong_employee_data_from_backend(window: sg.Window, error: storage.backend.WrongData) -> None:
    element_keys = []
    for err in error.errors:
        while "0" in err.loc:
            err.loc.remove("0")
        key = f"-EMPLOYEE-{'-'.join(err.loc[1:])}-".upper().replace("_", "-")
        element_keys.append(key)

    for key in element_keys:
        window[key].update(background_color="red")


def clear_wrong_employee_data(window: sg.Window) -> None:
    for key in elements.EmployeeForm:
        window[key].update(background_color="white")


def add_employee(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:
    @wrong_data_exception_handler(
        storage.backend.WrongData,
        show_wrong_employee_data_from_backend,
        window
    )
    @events.raise_status_events(
        window,
        events.EmployeeEvent.ADD_EMPLOYEE_SUCCESS,
        events.EmployeeEvent.ADD_EMPLOYEE_PROCESSING,
        events.EmployeeEvent.ADD_EMPLOYEE_FAIL
    )
    def call_add_employee() -> storage.schema.Employee:
        employee = user_input.Employee.get_employee(values)
        return storage.service.add_employee(employee, backend)

    window.perform_long_operation(call_add_employee, end_key=events.Misc.NON_EXISTENT)


def update_employee(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:
    if not values[events.EmployeeEvent.EMPLOYEE_SELECTED]:
        return

    employee_id_in_list = values[events.EmployeeEvent.EMPLOYEE_SELECTED][-1]
    employee_id = int(window[events.EmployeeEvent.EMPLOYEE_SELECTED].get()[employee_id_in_list][0])
    employee = user_input.Employee.get_employee(values)

    @wrong_data_exception_handler(
        storage.backend.WrongData,
        show_wrong_employee_data_from_backend,
        window
    )
    @events.raise_status_events(
        window,
        events.EmployeeEvent.UPDATE_EMPLOYEE_SUCCESS,
        events.EmployeeEvent.UPDATE_EMPLOYEE_PROCESSING,
        events.EmployeeEvent.UPDATE_EMPLOYEE_FAIL
    )
    def call_update_employee() -> storage.schema.Employee:
        return storage.service.update_employee(employee, employee_id, backend)

    window.perform_long_operation(call_update_employee, end_key=events.Misc.NON_EXISTENT)


def delete_employees(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:
    selected_employees_ids_in_list = values[events.EmployeeEvent.EMPLOYEE_SELECTED]
    all_employees_in_list = window[events.EmployeeEvent.EMPLOYEE_SELECTED].get()
    selected_employees_ids = [int(all_employees_in_list[i][0]) for i in selected_employees_ids_in_list]

    @events.raise_status_events(
        window,
        events.EmployeeEvent.DELETE_EMPLOYEES_SUCCESS,
        events.EmployeeEvent.DELETE_EMPLOYEES_PROCESSING,
        events.EmployeeEvent.DELETE_EMPLOYEES_FAIL
    )
    def call_delete_employees() -> list[storage.schema.Employee]:
        return storage.service.delete_employees(selected_employees_ids, backend)

    window.perform_long_operation(call_delete_employees, end_key=events.Misc.NON_EXISTENT)


def search_employees(
        window: sg.Window,
        values: dict[Key, Any],
) -> None:
    search_attrs_as_entry = [
        values[elements.EmployeeForm.NAME] or None,
        values[elements.EmployeeForm.SURNAME] or None,
        values[elements.EmployeeForm.PATRONYMIC] or None
    ]

    if not any(search_attrs_as_entry):
        return

    employees_entries = window[events.EmployeeEvent.EMPLOYEE_SELECTED].get()

    matched_entries_numbers = []
    for entry_number, entry in enumerate(employees_entries):
        for i, employee_attr in enumerate(entry[1:]):  # Skip employee ID
            if employee_attr == search_attrs_as_entry[i]:
                matched_entries_numbers.append(entry_number)
                continue

    window[events.EmployeeEvent.EMPLOYEE_SELECTED].update(select_rows=matched_entries_numbers)


def update_employees(window: sg.Window, backend: storage.backend.StorageBackend) -> None:
    @events.raise_status_events(
        window,
        events.EmployeeEvent.GET_EMPLOYEES_SUCCESS,
        events.EmployeeEvent.GET_EMPLOYEES_PROCESSING,
        events.EmployeeEvent.GET_EMPLOYEES_FAIL
    )
    def call_get_employees() -> list[storage.schema.Employee]:
        return storage.service.get_employees(0, 99999, backend)

    window.perform_long_operation(call_get_employees, end_key=events.Misc.NON_EXISTENT)


def show_employees(window: sg.Window, values: dict[Key, Any]) -> None:
    employees = values[events.EmployeeEvent.GET_EMPLOYEES_SUCCESS]
    employees_out = [storage.schema.EmployeeOut(**i.dict()) for i in employees]

    table_rows = []
    for emp in employees_out:
        work_duration_timedelta = relativedelta.relativedelta(datetime.date.today(), emp.employment_date)
        work_duration_in_months = (work_duration_timedelta.years * 12) + work_duration_timedelta.months
        table_rows.append(
            [
                emp.id, emp.name, emp.surname, emp.patronymic, emp.service_number, emp.department_number,
                str(emp.employment_date), str(work_duration_in_months), emp.topic.number, emp.topic.name, emp.post.code,
                emp.post.name, emp.salary.amount,
                emp.salary.currency.name, ", ".join([title.name for title in emp.titles])
            ]
        )

    window[events.EmployeeEvent.EMPLOYEE_SELECTED].update(values=table_rows)


def insert_selected_employee_to_form(
        window: sg.Window,
        values: dict[Key, Any]
) -> None:
    assert values[events.EmployeeEvent.EMPLOYEE_SELECTED]

    employee_id_in_list = values[events.EmployeeEvent.EMPLOYEE_SELECTED][-1]
    employee_entry_in_list = window[events.EmployeeEvent.EMPLOYEE_SELECTED].get()[employee_id_in_list]

    window[elements.EmployeeForm.NAME].update(value=employee_entry_in_list[1])
    window[elements.EmployeeForm.SURNAME].update(value=employee_entry_in_list[2])
    window[elements.EmployeeForm.PATRONYMIC].update(value=employee_entry_in_list[3])


def show_success(window: sg.Window) -> None:
    window[elements.Misc.OPERATION_STATUS_FIELD].update(
        value="Success!",
        text_color="white",
        background_color="green",
        visible=True,
    )


def show_fail(window: sg.Window) -> None:
    window[elements.Misc.OPERATION_STATUS_FIELD].update(
        value="Fail!",
        text_color="white",
        background_color="red",
        visible=True,
    )


def show_processing(window: sg.Window) -> None:
    window[elements.Misc.OPERATION_STATUS_FIELD].update(
        value="Processing...",
        text_color="white",
        background_color="grey",
        visible=True,
    )


def open_statistics_window(window: sg.Window) -> sg.Window:
    if not isinstance(window, windows.HierarchicalWindow):
        raise NotImplementedError

    window.create_child_window(
        "Statistics",
        layout=deepcopy(layouts.STATISTICS_WINDOW_LAYOUT),
        location=(200, 200),
        size=(500, 300),
        finalize=True,
    )

    return window


def open_forecasts_window(window: sg.Window) -> sg.Window:
    if not isinstance(window, windows.HierarchicalWindow):
        raise NotImplementedError

    window.create_child_window(
        "Forecasts",
        layout=deepcopy(layouts.FORECASTS_WINDOW_LAYOUT),
        location=(200, 200),
        size=(500, 300),
        finalize=True,
    )

    return window


def show_max_work_duration_employees(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:
    employees_count = values[elements.Statistics.MAX_WORK_DURATION_EMPLOYEES_COUNT]

    @events.raise_status_events(
        window,
        events.StatisticsEvent.SHOW_MAX_WORK_DURATION_EMPLOYEES_SUCCESS,
        events.StatisticsEvent.SHOW_MAX_WORK_DURATION_EMPLOYEES_PROCESSING,
        events.StatisticsEvent.SHOW_MAX_WORK_DURATION_EMPLOYEES_FAIL
    )
    def call_get_max_work_duration_employees() -> list[storage.schema.Employee]:
        return storage.service.get_max_work_duration_employees(employees_count, backend)

    window.perform_long_operation(call_get_max_work_duration_employees, end_key=events.Misc.NON_EXISTENT)


def show_max_work_duration_employees_graph(window: sg.Window, values: dict[Key, Any]) -> None:
    if not isinstance(window, windows.HierarchicalWindow):
        raise NotImplementedError

    max_work_duration_employees = values[events.StatisticsEvent.SHOW_MAX_WORK_DURATION_EMPLOYEES_SUCCESS]

    today = datetime.date.today()
    employees_names = []
    work_durations_in_month = []
    for emp in max_work_duration_employees:
        work_timedelta = relativedelta.relativedelta(today, emp.employment_date)
        work_months = (work_timedelta.years * 12) + work_timedelta.months
        work_durations_in_month.append(work_months)

        emp_name = f"{emp.name}\n{emp.surname}\n{emp.patronymic}\n({emp.id})"
        employees_names.append(emp_name)

    employees_count = len(max_work_duration_employees)
    max_work_duration = max(work_durations_in_month)
    fig, ax = plt.subplots(figsize=(3 * employees_count, (0.2 * max_work_duration) + 2), layout='constrained')
    ax.bar(employees_names, work_durations_in_month)

    for i, duration in enumerate(work_durations_in_month):
        print(duration)
        ax.annotate(duration, xy=(i, duration))

    graph_window = window.create_child_window(
        "Employees work duration",
        layout=deepcopy(layouts.STATISTICS_MAX_WORK_DURATION_EMPLOYEES_GRAPH_WINDOW),
        finalize=True,
        resizable=True,
        element_justification="center",
    )
    canvas = graph_window[elements.Statistics.MAX_WORK_DURATION_EMPLOYEES_CANVAS].TKCanvas
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


def show_highest_paid_employees(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:
    employees_count = values[elements.Statistics.HIGHEST_PAID_EMPLOYEES_COUNT]

    @events.raise_status_events(
        window,
        events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_SUCCESS,
        events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_PROCESSING,
        events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_FAIL
    )
    def call_get_highest_paid_employees() -> list[storage.schema.Employee]:
        return storage.service.get_highest_paid_employees(employees_count, backend)

    window.perform_long_operation(call_get_highest_paid_employees, end_key=events.Misc.NON_EXISTENT)


def show_highest_paid_employees_graph(window: sg.Window, values: dict[Key, Any]) -> None:
    if not isinstance(window, windows.HierarchicalWindow):
        raise NotImplementedError

    highest_paid_employees = values[events.StatisticsEvent.SHOW_HIGHEST_PAID_EMPLOYEES_SUCCESS]
    print(len(highest_paid_employees))

    employees_names = []
    employees_salaries_sizes_places: list[int] = []
    for i in range(len(highest_paid_employees)):
        if not employees_salaries_sizes_places:
            employees_salaries_sizes_places.append(1)
        elif highest_paid_employees[i].salary.amount == highest_paid_employees[i - 1].salary.amount and \
                highest_paid_employees[i].salary.currency.name == highest_paid_employees[i - 1].salary.currency.name:
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
    fig, ax = plt.subplots(
        figsize=(3 * employees_count, max(employees_salaries_sizes_places) + 2),
        layout='constrained'
    )

    graphs_sizes = [max(employees_salaries_sizes_places) - i + 1 for i in employees_salaries_sizes_places]
    ax.bar(employees_names, graphs_sizes)

    plt.yticks([])

    for i, salary_place in enumerate(employees_salaries_sizes_places):
        ax.annotate(employees_salaries_reprs[i], xy=(i, graphs_sizes[i]))

    graph_window = window.create_child_window(
        "Highest paid employees",
        layout=deepcopy(layouts.STATISTICS_HIGHEST_PAID_EMPLOYEES_GRAPH_WINDOW),
        finalize=True,
        resizable=True,
        element_justification="center",
    )
    canvas = graph_window[elements.Statistics.HIGHEST_PAID_EMPLOYEES_CANVAS].TKCanvas
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


def show_title_employees_history_growth(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:

    title_name = values[elements.Statistics.TITLE_EMPLOYEES_GROWTH_HISTORY_TITLE_NAME]

    @events.raise_status_events(
        window,
        events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_SUCCESS,
        events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_PROCESSING,
        events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_FAIL
    )
    def call_get_title_employees_history_growth() -> dict[int, int]:
        return storage.service.get_title_employees_history_growth(title_name, backend)

    window.perform_long_operation(call_get_title_employees_history_growth, end_key=events.Misc.NON_EXISTENT)


def show_title_employees_history_growth_graph(window: sg.Window, values: dict[Key, Any]) -> None:
    if not isinstance(window, windows.HierarchicalWindow):
        raise NotImplementedError

    titles_employees_growth_history = values[events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_SUCCESS]

    if not titles_employees_growth_history:
        return

    years = []
    employees_growth_per_year = []
    for year in titles_employees_growth_history:
        years.append(year)
        employees_growth_per_year.append(titles_employees_growth_history[year])

    max_employees_growth = max(employees_growth_per_year)
    fig, ax = plt.subplots(figsize=(20, max_employees_growth + 2), layout='constrained')

    ax.bar(years, employees_growth_per_year)
    plt.xticks(years)
    plt.yticks(employees_growth_per_year)

    for i, year in enumerate(years):
        ax.annotate(employees_growth_per_year[i], xy=(year, employees_growth_per_year[i]))

    graph_window = window.create_child_window(
        "Title employees growth history",
        layout=deepcopy(layouts.STATISTICS_TITLE_EMPLOYEES_GROWTH_HISTORY_GRAPH_WINDOW),
        finalize=True,
        resizable=True,
        element_justification="center",
    )
    canvas = graph_window[elements.Statistics.TITLE_EMPLOYEES_GROWTH_HISTORY_CANVAS].TKCanvas
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


def show_title_employees_forecast_growth(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:

    title_name = values[elements.Forecasts.TITLE_EMPLOYEES_GROWTH_FORECAST_TITLE_NAME]
    years_count = values[elements.Forecasts.TITLE_EMPLOYEES_GROWTH_FORECAST_YEARS_COUNT]

    @events.raise_status_events(
        window,
        events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_SUCCESS,
        events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_PROCESSING,
        events.StatisticsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_HISTORY_FAIL
    )
    def call_get_title_employees_forecast_growth() -> dict[int, int]:
        return storage.service.get_title_employees_forecast_growth(title_name, years_count, backend)

    window.perform_long_operation(call_get_title_employees_forecast_growth, end_key=events.Misc.NON_EXISTENT)


def show_title_employees_forecast_growth_graph(window: sg.Window, values: dict[Key, Any]) -> None:
    if not isinstance(window, windows.HierarchicalWindow):
        raise NotImplementedError

    titles_employees_growth_forecast = values[events.ForecastsEvent.SHOW_TITLE_EMPLOYEES_GROWTH_FORECAST_SUCCESS]

    if not titles_employees_growth_forecast:
        return

    years = []
    employees_growth_per_year = []
    for year in titles_employees_growth_forecast:
        years.append(year)
        employees_growth_per_year.append(titles_employees_growth_forecast[year])

    max_employees_growth = max(employees_growth_per_year)
    fig, ax = plt.subplots(figsize=(20, max_employees_growth + 2), layout='constrained')

    ax.bar(years, employees_growth_per_year)
    plt.xticks(years)
    plt.yticks(employees_growth_per_year)

    for i, year in enumerate(years):
        ax.annotate(employees_growth_per_year[i], xy=(year, employees_growth_per_year[i]))

    graph_window = window.create_child_window(
        "Title employees growth history",
        layout=deepcopy(layouts.FORECASTS_TITLE_EMPLOYEES_GROWTH_FORECAST_GRAPH_WINDOW),
        finalize=True,
        resizable=True,
        element_justification="center",
    )
    canvas = graph_window[elements.Forecasts.TITLE_EMPLOYEES_GROWTH_FORECAST_CANVAS].TKCanvas
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


def show_employees_distribution_by_topics(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:

    @events.raise_status_events(
        window,
        events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_SUCCESS,
        events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_PROCESSING,
        events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_FAIL
    )
    def call_get_employees() -> list[storage.schema.Employee]:
        return storage.service.get_employees(0, 9999999999, backend)

    window.perform_long_operation(call_get_employees, end_key=events.Misc.NON_EXISTENT)


def show_employees_distribution_by_topics_graph(window: sg.Window, values: dict[Key, Any]) -> None:
    if not isinstance(window, windows.HierarchicalWindow):
        raise NotImplementedError

    employees = values[events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TOPICS_SUCCESS]

    if not employees:
        return

    emps_count_per_topic: Counter[str] = Counter()
    for emp in employees:
        emps_count_per_topic[emp.topic.name] += 1

    fig, ax = plt.subplots(figsize=(
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

    graph_window = window.create_child_window(
        "Employees distribution by topics",
        layout=deepcopy(layouts.STATISTICS_EMPLOYEES_DISTRIBUTION_BY_TOPICS_GRAPH_WINDOW),
        finalize=True,
        resizable=True,
        element_justification="center",
    )
    canvas = graph_window[elements.Statistics.EMPLOYEES_DISTRIBUTION_BY_TOPICS_CANVAS].TKCanvas
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


def show_employees_distribution_by_titles(
        window: sg.Window,
        values: dict[Key, Any],
        backend: storage.backend.StorageBackend
) -> None:

    @events.raise_status_events(
        window,
        events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_SUCCESS,
        events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_PROCESSING,
        events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_FAIL
    )
    def call_get_employees() -> list[storage.schema.Employee]:
        return storage.service.get_employees(0, 9999999999, backend)

    window.perform_long_operation(call_get_employees, end_key=events.Misc.NON_EXISTENT)


def show_employees_distribution_by_titles_graph(window: sg.Window, values: dict[Key, Any]) -> None:
    if not isinstance(window, windows.HierarchicalWindow):
        raise NotImplementedError

    employees = values[events.StatisticsEvent.SHOW_EMPLOYEES_DISTRIBUTION_BY_TITLES_SUCCESS]

    if not employees:
        return

    emps_count_per_title: Counter[str] = Counter()
    for emp in employees:
        for title in emp.titles:
            emps_count_per_title[title.name] += 1

    fig, ax = plt.subplots(figsize=(
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

    graph_window = window.create_child_window(
        "Employees distribution by topics",
        layout=deepcopy(layouts.STATISTICS_EMPLOYEES_DISTRIBUTION_BY_TITLES_GRAPH_WINDOW),
        finalize=True,
        resizable=True,
        element_justification="center",
    )
    canvas = graph_window[elements.Statistics.EMPLOYEES_DISTRIBUTION_BY_TITLES_CANVAS].TKCanvas
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


def close_window(window: sg.Window) -> None:
    window.close()
    assert window.is_closed()

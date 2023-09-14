from ..service.forecasts.exceptions import WrongForecastsData
from ..service.statistics.exceptions import WrongStatisticsData
from ..service.storage.exceptions import WrongEmployeeData
from . import elements


def get_wrong_employee_data_fields(exception: WrongEmployeeData) -> list[elements.EmployeeForm]:
    error_fields: list[elements.EmployeeForm] = []
    for err_place in exception.errors_places:
        match err_place:
            case ["name" | "surname" | "patronymic" as field]:
                error_fields.append(elements.EmployeeForm(f"-EMPLOYEE-{field.upper()}-"))
            case ["department_number" | "service_number" | "employment_date" as field]:
                formatted_field = field.replace("_", "-")
                error_fields.append(elements.EmployeeForm(f"-EMPLOYEE-{formatted_field.upper()}-"))
            case ["titles" as field, *_]:
                error_fields.append(elements.EmployeeForm(f"-EMPLOYEE-{field.upper()}-NAME-"))
            case ["topic" as topic, "name" | "number" as topic_part]:
                error_fields.append(elements.EmployeeForm(f"-EMPLOYEE-{topic.upper()}-{topic_part.upper()}-"))
            case ["topic"]:
                error_fields += elements.EmployeeForm.TOPIC_NAME, elements.EmployeeForm.TOPIC_NUMBER
            case ["post" as post, "name" | "code" as post_part]:
                error_fields.append(elements.EmployeeForm(f"-EMPLOYEE-{post.upper()}-{post_part.upper()}-"))
            case ["post"]:
                error_fields += elements.EmployeeForm.POST_NAME, elements.EmployeeForm.POST_CODE
            case ["salary" as salary, "amount" | "currency" as salary_part, *_]:
                error_fields.append(elements.EmployeeForm(f"-EMPLOYEE-{salary.upper()}-{salary_part.upper()}-"))
            case ["salary"]:
                error_fields += elements.EmployeeForm.SALARY_CURRENCY, elements.EmployeeForm.SALARY_AMOUNT

    return error_fields


# TODO: Refactor this with user wrong input exceptions
def get_wrong_statistics_data_fields(exception: WrongStatisticsData) -> list[elements.Statistics]:
    error_fields: list[elements.Statistics] = []
    for err_place in exception.errors_places:
        error_fields.append(elements.Statistics(err_place[0]))

    return error_fields


# TODO: Refactor this with user wrong input exceptions
def get_wrong_forecasts_data_fields(exception: WrongForecastsData) -> list[elements.Forecasts]:
    error_fields: list[elements.Forecasts] = []
    for err_place in exception.errors_places:
        error_fields.append(elements.Forecasts(err_place[0]))

    return error_fields

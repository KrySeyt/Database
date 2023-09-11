from typing import Any

from .keys import Key
from .elements import EmployeeForm
from app.service import storage


def get_employee(values: dict[Key, Any]) -> storage.schema.EmployeeIn:
    return storage.schema.EmployeeIn(
        name=values[EmployeeForm.NAME],
        surname=values[EmployeeForm.SURNAME],
        patronymic=values[EmployeeForm.PATRONYMIC],
        service_number=values[EmployeeForm.SERVICE_NUMBER],
        department_number=values[EmployeeForm.DEPARTMENT_NUMBER],
        employment_date=values[EmployeeForm.EMPLOYMENT_DATE],
        titles=get_titles(values),
        post=get_post(values),
        topic=get_topic(values),
        salary=get_salary(values)
    )


def get_topic(values: dict[Key, Any]) -> storage.schema.TopicIn:
    return storage.schema.TopicIn(
        name=values[EmployeeForm.TOPIC_NAME],
        number=values[EmployeeForm.TOPIC_NUMBER]
    )


def get_post(values: dict[Key, Any]) -> storage.schema.PostIn:
    return storage.schema.PostIn(
        name=values[EmployeeForm.POST_NAME],
        code=values[EmployeeForm.POST_CODE]
    )


def get_salary(values: dict[Key, Any]) -> storage.schema.SalaryIn:
    return storage.schema.SalaryIn(
        amount=values[EmployeeForm.SALARY_AMOUNT],
        currency=get_currency(values),
    )


def get_currency(values: dict[Key, Any]) -> storage.schema.CurrencyIn:
    return storage.schema.CurrencyIn(name=values[EmployeeForm.SALARY_CURRENCY])


def get_titles(values: dict[Key, Any]) -> list[storage.schema.TitleIn]:
    return [storage.schema.TitleIn(name=title_name) for title_name in values[EmployeeForm.TITLES].split(", ")]

from typing import Any

from .keys import Key
from .elements import EmployeeForm
from app.service import storage


class Employee:
    @classmethod
    def get_employee(cls, values: dict[Key, Any]) -> storage.schema.EmployeeIn:
        return storage.schema.EmployeeIn(
            name=values[EmployeeForm.NAME],
            surname=values[EmployeeForm.SURNAME],
            patronymic=values[EmployeeForm.PATRONYMIC],
            service_number=values[EmployeeForm.SERVICE_NUMBER],
            department_number=values[EmployeeForm.DEPARTMENT_NUMBER],
            employment_date=values[EmployeeForm.EMPLOYMENT_DATE],
            titles=cls.get_titles(values),
            post=cls.get_post(values),
            topic=cls.get_topic(values),
            salary=cls.get_salary(values)
        )

    @classmethod
    def get_topic(cls, values: dict[Key, Any]) -> storage.schema.TopicIn:
        return storage.schema.TopicIn(
            name=values[EmployeeForm.TOPIC_NAME],
            number=values[EmployeeForm.TOPIC_NUMBER]
        )

    @classmethod
    def get_post(cls, values: dict[Key, Any]) -> storage.schema.PostIn:
        return storage.schema.PostIn(
            name=values[EmployeeForm.POST_NAME],
            code=values[EmployeeForm.POST_CODE]
        )

    @classmethod
    def get_salary(cls, values: dict[Key, Any]) -> storage.schema.SalaryIn:
        return storage.schema.SalaryIn(
            amount=values[EmployeeForm.SALARY_AMOUNT],
            currency=cls.get_currency(values),
        )

    @classmethod
    def get_currency(cls, values: dict[Key, Any]) -> storage.schema.CurrencyIn:
        return storage.schema.CurrencyIn(name=values[EmployeeForm.SALARY_CURRENCY])

    @classmethod
    def get_titles(cls, values: dict[Key, Any]) -> list[storage.schema.TitleIn]:
        return [storage.schema.TitleIn(name=title_name) for title_name in values[EmployeeForm.TITLES].split(", ")]

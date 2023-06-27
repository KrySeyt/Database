from enum import Enum


class Element(str, Enum):
    pass


class EmployeeInput(Element):
    FIRST_NAME = "-EMPLOYEE-FIRST-NAME-"
    LAST_NAME = "-EMPLOYEE-LAST-NAME-"
    PATRONYMIC = "-EMPLOYEE-PATRONYMIC-"

from enum import Enum


class Element(str, Enum):
    pass


class EmployeeList(Element):
    TABLE = "-TABLE-"


class EmployeeForm(Element):
    FIRST_NAME = "-EMPLOYEE-FIRST-NAME-"
    LAST_NAME = "-EMPLOYEE-LAST-NAME-"
    PATRONYMIC = "-EMPLOYEE-PATRONYMIC-"
    ADD_EMPLOYEE_STATUS = "-ADD-EMPLOYEE-STATUS-"

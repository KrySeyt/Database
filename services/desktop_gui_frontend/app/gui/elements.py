#  Keys for elements that not raises events. If elements raises event - set event as key


from enum import Enum


class Element(str, Enum):
    pass


class EmployeeList(Element):
    PAGE = "-EMPLOYEE-LIST-PAGE"


class EmployeeForm(Element):
    ID = "-EMPLOYEE-ID-"
    NAME = "-EMPLOYEE-NAME-"
    SURNAME = "-EMPLOYEE-SURNAME-"
    PATRONYMIC = "-EMPLOYEE-PATRONYMIC-"
    ADD_EMPLOYEE_STATUS = "-ADD-EMPLOYEE-STATUS-"

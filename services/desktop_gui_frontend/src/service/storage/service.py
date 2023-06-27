from . import schema


def add_employee(employee: schema.EmployeeIn) -> schema.Employee:
    return schema.Employee.from_orm(employee)

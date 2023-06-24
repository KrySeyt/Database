from . import schema


async def create_employee(employee: schema.EmployeeIn) -> schema.Employee:
    return schema.Employee.from_orm(employee)

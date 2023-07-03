from sqlalchemy.ext.asyncio import AsyncSession

from database_app.service.storage import schema, crud


async def is_service_number_occupied(db: AsyncSession, service_number: int) -> bool:
    return await crud.is_service_number_occupied(db, service_number)


async def create_employee(db: AsyncSession, employee_in: schema.EmployeeIn) -> schema.Employee:
    db_employee = await crud.create_employee(db, employee_in)
    return schema.Employee.from_orm(db_employee)


async def get_employee(db: AsyncSession, employee_id: int) -> schema.Employee | None:
    db_employee = await crud.get_employee(db, employee_id)
    if db_employee is None:
        return None
    return schema.Employee.from_orm(db_employee)


async def get_employees(db: AsyncSession, skip: int, limit: int) -> list[schema.Employee]:
    db_employees = await crud.get_employees(db, skip, limit)
    return [schema.Employee.from_orm(db_emp) for db_emp in db_employees]


async def update_employee(db: AsyncSession, employee_in: schema.EmployeeInWithID) -> schema.Employee | None:
    db_employee = await crud.update_employee(db, employee_in)
    if not db_employee:
        return None
    return schema.Employee.from_orm(db_employee)


async def delete_employee(db: AsyncSession, employee_id: int) -> schema.Employee | None:
    db_employee = await crud.delete_employee(db, employee_id)
    if db_employee is None:
        return None
    return schema.Employee.from_orm(db_employee)


async def search_employees(db: AsyncSession, search_model: schema.EmployeeSearchModel) -> list[schema.Employee]:
    db_employees = await crud.search_employees(db, search_model)
    return [schema.Employee.from_orm(i) for i in db_employees]

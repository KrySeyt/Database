from sqlalchemy.ext.asyncio import AsyncSession

from database_app.service.storage import schema, crud


async def create_employee(db: AsyncSession, employee_in: schema.EmployeeIn) -> schema.Employee:
    db_employee = await crud.add_employee(db, employee_in)
    return schema.Employee.from_orm(db_employee)

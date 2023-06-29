from sqlalchemy.ext.asyncio import AsyncSession

from . import schema
from . import models


async def add_employee(db: AsyncSession, employee_in: schema.EmployeeIn) -> models.Employee:
    db_employee = models.Employee(**employee_in.dict())
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee

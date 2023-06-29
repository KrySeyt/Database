from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import schema
from . import models


async def create_employee(db: AsyncSession, employee_in: schema.EmployeeIn) -> models.Employee:
    db_employee = models.Employee(**employee_in.dict())
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def get_employee(db: AsyncSession, employee_id: int) -> models.Employee | None:
    db_employee = await db.get(models.Employee, employee_id)
    return db_employee


async def get_employees(db: AsyncSession, skip: int, limit: int) -> list[models.Employee]:
    stmt = select(models.Employee).offset(skip).limit(limit)
    return list((await db.scalars(stmt)).all())


async def update_employee(db: AsyncSession, employee_in: schema.EmployeeInWithID) -> models.Employee | None:
    db_employee = await get_employee(db, employee_in.id)
    if not db_employee:
        return None

    for key in employee_in.dict():
        setattr(db_employee, key, getattr(employee_in, key))

    await db.commit()
    await db.refresh(db_employee)
    return db_employee

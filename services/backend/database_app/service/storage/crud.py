from sqlalchemy import select, asc
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
    stmt = select(models.Employee).offset(skip).limit(limit).order_by(asc(models.Employee.id))
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


async def delete_employee(db: AsyncSession, employee_id: int) -> models.Employee | None:
    db_employee = await get_employee(db, employee_id)
    if not db_employee:
        return None

    await db.delete(db_employee)
    await db.commit()

    return db_employee


async def search_employees(db: AsyncSession, search_model: schema.EmployeeSearchModel) -> list[models.Employee]:
    search_params = {k: v for k, v in search_model.dict().items() if v is not None}

    stmt = select(models.Employee).where(
        *[getattr(models.Employee, key) == search_params[key] for key in search_params]
    )
    db_employees = list((await db.scalars(stmt)).all())
    return db_employees

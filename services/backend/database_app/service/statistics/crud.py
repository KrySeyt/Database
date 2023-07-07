from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from ..storage import models as storage_models


async def get_work_longest_employees(db: AsyncSession, employees_count: int) -> list[storage_models.Employee]:
    stmt = select(storage_models.Employee).order_by(asc(storage_models.Employee.employment_date)).limit(employees_count)
    db_employees = (await db.scalars(stmt)).all()
    return list(db_employees)

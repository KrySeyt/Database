from sqlalchemy.ext.asyncio import AsyncSession

from ..storage import schema as storage_schema
from ..storage import utils as storage_utils
from ..storage import service as storage_service
from . import crud


async def get_highest_paid_employees(db: AsyncSession, employees_count: int) -> list[storage_schema.Employee]:
    employees = await storage_service.get_all_employees(db)

    usd_currency = storage_schema.Currency(id=0, name="USD")
    employees_with_usd_salaries = []
    for emp in employees:
        employee_salary_currency_course_to_usd = await storage_utils.get_currency_course(
            emp.salary.currency,
            usd_currency,
        )
        employees_with_usd_salaries.append((emp, emp.salary.amount * employee_salary_currency_course_to_usd))

    employees_with_usd_salaries.sort(key=lambda entry: entry[1], reverse=True)
    return [storage_schema.Employee.from_orm(i[0]) for i in employees_with_usd_salaries[:employees_count]]


async def get_work_longest_employee(db: AsyncSession, employees_count: int) -> list[storage_schema.Employee]:
    db_employees = await crud.get_work_longest_employees(db, employees_count)
    if not db_employees:
        return []
    return [storage_schema.Employee.from_orm(i) for i in db_employees]


async def get_title_employees_growth_history(
        db: AsyncSession,
        title: storage_schema.TitleIn
) -> dict[int, int]:

    title_employees_growth = {}
    title_employees = await storage_service.get_employees_by_title(db, title)

    for emp in title_employees:
        if emp.employment_date.year not in title_employees_growth:
            title_employees_growth[emp.employment_date.year] = 1
        else:
            title_employees_growth[emp.employment_date.year] += 1

    min_year = min(title_employees_growth)
    max_year = max(title_employees_growth)

    for year in range(min_year + 1, max_year + 1):
        if year not in title_employees_growth:
            title_employees_growth[year] = 0

    return title_employees_growth

from sqlalchemy.ext.asyncio import AsyncSession

from ..storage import schema as storage_schema
from ..storage import utils as storage_utils
from ..storage import service as storage_service


async def get_highest_paid_employee(db: AsyncSession) -> storage_schema.Employee | None:
    employees = await storage_service.get_all_employees(db)

    usd_currency = storage_schema.Currency(id=0, name="USD")
    employees_with_usd_salaries = []
    for emp in employees:
        employee_salary_currency_course_to_usd = await storage_utils.get_currency_course(
            emp.salary.currency,
            usd_currency,
        )
        employees_with_usd_salaries.append((emp, emp.salary.amount * employee_salary_currency_course_to_usd))

    highest_paid_employee, _ = max(employees_with_usd_salaries, key=lambda entry: entry[1])
    return storage_schema.Employee.from_orm(highest_paid_employee)

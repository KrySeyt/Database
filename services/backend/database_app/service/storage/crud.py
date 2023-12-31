import decimal

from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from . import schema
from . import models


async def is_employee_id_exist(db: AsyncSession, employee_id: int) -> bool:
    db_employee = await db.get(models.Employee, employee_id)
    return bool(db_employee)


async def is_service_number_occupied(db: AsyncSession, service_number: int) -> bool:
    stmt = select(models.Employee).where(models.Employee.service_number == service_number)
    return bool((await db.execute(stmt)).first())


async def get_topic_by_name_and_number(db: AsyncSession, topic_name: str, topic_number: int) -> models.Topic | None:
    db_topic = await db.execute(select(models.Topic).where(
        models.Topic.name == topic_name,
        models.Topic.number == topic_number
    ))
    return db_topic.scalar()


async def get_post_by_name_and_code(db: AsyncSession, post_name: str, post_code: int) -> models.Post | None:
    db_post = await db.execute(select(models.Post).where(
        models.Post.name == post_name,
        models.Post.code == post_code
    ))
    return db_post.scalar()


async def get_title_by_name(db: AsyncSession, title_name: str) -> models.Title | None:
    db_title = await db.execute(select(models.Title).where(models.Title.name == title_name))
    return db_title.scalar()


async def get_currency_by_name(db: AsyncSession, currency_name: str) -> models.Currency | None:
    db_currency = await db.execute(select(models.Currency).where(models.Currency.name == currency_name))
    return db_currency.scalar()


async def create_salary(db: AsyncSession, salary_in: schema.SalaryIn) -> models.Salary:
    db_currency = await get_currency_by_name(db, salary_in.currency.name) \
                  or models.Currency(**salary_in.currency.dict())
    db_salary = models.Salary(
        amount=salary_in.amount,
        currency=db_currency
    )
    db.add(db_salary)
    await db.commit()
    await db.refresh(db_salary)
    return db_salary


async def get_salary_by_amount_and_currency(
        db: AsyncSession,
        salary_amount: decimal.Decimal,
        salary_currency: schema.CurrencyIn
) -> models.Salary | None:
    db_currency = await get_currency_by_name(db, salary_currency.name) or models.Currency(**salary_currency.dict())
    if not db_currency:
        return None
    db_salary = await db.execute(select(models.Salary).where(
        models.Salary.amount == salary_amount,
        models.Salary.currency_id == db_currency.id
    ))
    return db_salary.scalar()


async def create_employee(db: AsyncSession, employee_in: schema.EmployeeIn) -> models.Employee:
    db_topic = await get_topic_by_name_and_number(
        db,
        employee_in.topic.name,
        employee_in.topic.number
    ) or models.Topic(**employee_in.topic.dict())

    db_post = await get_post_by_name_and_code(
        db,
        employee_in.post.name,
        employee_in.post.code
    ) or models.Post(**employee_in.post.dict())

    db_salary = await get_salary_by_amount_and_currency(
        db,
        employee_in.salary.amount,
        employee_in.salary.currency
    ) or await create_salary(db, employee_in.salary)

    db_titles = [
        await get_title_by_name(
            db,
            i.name
        ) or models.Title(**i.dict())
        for i in employee_in.titles
    ]

    db_employee = models.Employee(
        name=employee_in.name,
        surname=employee_in.surname,
        patronymic=employee_in.patronymic,
        department_number=employee_in.department_number,
        service_number=employee_in.service_number,
        employment_date=employee_in.employment_date,
        topic=db_topic,
        post=db_post,
        salary=db_salary,
        titles=db_titles
    )

    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def update_employee(db: AsyncSession, employee_in: schema.EmployeeIn, employee_id: int) -> models.Employee | None:
    db_employee = await get_employee(db, employee_id)

    if not db_employee:
        return None

    db_topic = await get_topic_by_name_and_number(
        db,
        employee_in.topic.name,
        employee_in.topic.number
    ) or models.Topic(**employee_in.topic.dict())

    db_post = await get_post_by_name_and_code(
        db,
        employee_in.post.name,
        employee_in.post.code
    ) or models.Post(**employee_in.post.dict())

    db_salary = await get_salary_by_amount_and_currency(
        db,
        employee_in.salary.amount,
        employee_in.salary.currency
    ) or await create_salary(db, employee_in.salary)

    db_titles = [
        await get_title_by_name(
            db,
            i.name
        ) or models.Title(**i.dict())
        for i in employee_in.titles
    ]

    db_employee.name = employee_in.name
    db_employee.surname = employee_in.surname
    db_employee.patronymic = employee_in.patronymic
    db_employee.department_number = employee_in.department_number
    db_employee.service_number = employee_in.service_number
    db_employee.employment_date = employee_in.employment_date
    db_employee.topic = db_topic
    db_employee.post = db_post
    db_employee.salary = db_salary
    db_employee.titles = db_titles

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


async def get_employees_by_title(db: AsyncSession, title: schema.TitleIn) -> list[models.Employee]:
    stmt = select(models.Employee).join(models.Employee, models.Title.employees).where(models.Title.name == title.name)
    return list((await db.scalars(stmt)).all())


async def get_all_employees(db: AsyncSession) -> list[models.Employee]:
    stmt = select(models.Employee).order_by(asc(models.Employee.id))
    return list((await db.scalars(stmt)).all())


async def delete_employee(db: AsyncSession, employee_id: int) -> models.Employee | None:
    db_employee = await get_employee(db, employee_id)
    if not db_employee:
        return None

    await db.delete(db_employee)
    await db.commit()

    return db_employee


async def search_employees(db: AsyncSession, search_model: schema.EmployeeSearchModel) -> list[models.Employee]:
    # TODO: Refactor this spaghetti

    stmt = select(models.Employee)

    if search_model.topic:
        stmt = stmt.join(models.Topic)
        if search_model.topic.name:
            stmt = stmt.where(models.Topic.name == search_model.topic.name)
        if search_model.topic.number:
            stmt = stmt.where(models.Topic.number == search_model.topic.number)

    if search_model.post:
        stmt = stmt.join(models.Post)
        if search_model.post.name:
            stmt = stmt.where(models.Post.name == search_model.post.name)
        if search_model.post.code:
            stmt = stmt.where(models.Post.code == search_model.post.code)

    if search_model.salary:
        stmt = stmt.join(models.Salary)
        if search_model.salary.amount:
            stmt = stmt.where(models.Salary.amount == search_model.salary.amount)
        if search_model.salary.currency:
            stmt = stmt.join(models.Currency)
            if search_model.salary.currency.name:
                stmt = stmt.where(models.Currency.name == search_model.salary.currency.name)

    if search_model.titles:
        stmt = stmt.join(models.Title, models.Employee.titles)
        titles_names = [title.name for title in search_model.titles]
        stmt = stmt.where(models.Title.name.in_(titles_names))

    if search_model.name:
        stmt = stmt.where(models.Employee.name == search_model.name)

    if search_model.surname:
        stmt = stmt.where(models.Employee.surname == search_model.surname)

    if search_model.patronymic:
        stmt = stmt.where(models.Employee.patronymic == search_model.patronymic)

    if search_model.department_number:
        stmt = stmt.where(models.Employee.department_number == search_model.department_number)

    if search_model.service_number:
        stmt = stmt.where(models.Employee.service_number == search_model.service_number)

    if search_model.employment_date:
        stmt = stmt.where(models.Employee.employment_date == search_model.employment_date)

    db_employees = list((await db.scalars(stmt)).all())
    return db_employees

# Relations should be fixed later for be implemented as in database schema design

import datetime
import decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Table, Column, Numeric

from database_app.database import DBModelBase


employee_title_table = Table(
    "employee_title",
    DBModelBase.metadata,
    Column("employee_id", ForeignKey("employee.id"), primary_key=True),
    Column("title_id", ForeignKey("title.id"), primary_key=True),
)


class Employee(DBModelBase):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(length=100))
    surname: Mapped[str] = mapped_column(String(length=100))
    patronymic: Mapped[str] = mapped_column(String(length=100))
    department_number: Mapped[int]
    service_number: Mapped[int] = mapped_column(unique=True)
    employment_date: Mapped[datetime.date]

    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"))
    topic: Mapped["Topic"] = relationship(back_populates="employees", lazy="subquery")

    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    post: Mapped["Post"] = relationship(back_populates="employees", lazy="subquery")

    salary_id: Mapped[int] = mapped_column(ForeignKey("salary.id"))
    salary: Mapped["Salary"] = relationship(back_populates="employees", lazy="subquery")

    titles: Mapped[list["Title"]] = relationship(
        secondary=employee_title_table,
        back_populates="employees",
        lazy="subquery"
    )


class Topic(DBModelBase):
    __tablename__ = "topic"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(length=500), unique=True)
    number: Mapped[int] = mapped_column(unique=True)

    employees: Mapped[list[Employee]] = relationship(back_populates="topic")


class Post(DBModelBase):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[int]
    name: Mapped[str] = mapped_column(String(length=500), unique=True)

    employees: Mapped[list[Employee]] = relationship(back_populates="post")


class Title(DBModelBase):
    __tablename__ = "title"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(length=200), unique=True)

    employees: Mapped[list[Employee]] = relationship(secondary=employee_title_table, back_populates="titles")


class Salary(DBModelBase):
    __tablename__ = "salary"

    id: Mapped[int] = mapped_column(primary_key=True)

    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(scale=2))
    currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"))
    currency: Mapped["Currency"] = relationship(back_populates="salaries", lazy="subquery")

    employees: Mapped[list[Employee]] = relationship(back_populates="salary")


class Currency(DBModelBase):
    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(length=3), unique=True)

    salaries: Mapped[list[Salary]] = relationship(back_populates="currency")

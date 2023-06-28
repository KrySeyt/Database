from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from database_app.database import DBModelBase


class Employee(DBModelBase):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=100))
    surname: Mapped[str] = mapped_column(String(length=100))
    patronymic: Mapped[str] = mapped_column(String(length=100))

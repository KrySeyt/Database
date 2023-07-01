import datetime
import decimal

from pydantic import BaseModel, Field


class Base(BaseModel):
    pass


class TopicBase(Base):
    name: str
    number: int


class TopicIn(TopicBase):
    pass


class Topic(TopicBase):
    id: int

    class Config:
        orm_mode = True


class TopicOut(TopicBase):
    id: int


class PostBase(Base):
    name: str
    code: int


class PostIn(PostBase):
    pass


class Post(PostBase):
    id: int

    class Config:
        orm_mode = True


class PostOut(PostBase):
    id: int


class TitleBase(Base):
    name: str


class TitleIn(TitleBase):
    pass


class Title(TitleBase):
    id: int

    class Config:
        orm_mode = True


class TitleOut(TitleBase):
    id: int


class CurrencyBase(Base):
    name: str = Field(example="RUB")


class CurrencyIn(CurrencyBase):
    pass


class Currency(CurrencyBase):
    id: int

    class Config:
        orm_mode = True


class CurrencyOut(CurrencyBase):
    id: int


class SalaryBase(Base):
    amount: decimal.Decimal


class SalaryIn(SalaryBase):
    currency: "CurrencyIn"


class Salary(SalaryBase):
    id: int
    currency: "Currency"

    class Config:
        orm_mode = True


class SalaryOut(SalaryBase):
    id: int
    currency: CurrencyOut


class EmployeeBase(Base):
    name: str
    surname: str
    patronymic: str
    department_number: int
    service_number: int
    employment_date: datetime.date


class EmployeeIn(EmployeeBase):
    topic: TopicIn
    post: PostIn
    salary: SalaryIn
    titles: list[TitleIn]


class EmployeeInWithID(EmployeeIn):
    id: int


class Employee(EmployeeBase):
    id: int
    topic: Topic
    post: Post
    salary: Salary
    titles: list[Title]

    class Config:
        orm_mode = True


class EmployeeOut(EmployeeBase):
    id: int
    topic: TopicOut
    post: PostOut
    salary: SalaryOut
    titles: list[TitleOut]


class EmployeeSearchModel(Base):
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None

import datetime

from pydantic import BaseModel


class Base(BaseModel):
    pass


class TitleBase(Base):
    name: str


class TitleIn(TitleBase):
    pass


class Title(TitleBase):
    id: int


class TitleOut(TitleBase):
    pass


class TopicBase(Base):
    number: int
    name: str


class TopicIn(TopicBase):
    pass


class Topic(TopicBase):
    id: int


class TopicOut(TopicBase):
    pass


class PostBase(Base):
    code: int
    name: str


class PostIn(PostBase):
    pass


class Post(PostBase):
    id: int


class PostOut(PostBase):
    pass


class CurrencyBase(Base):
    name: str


class CurrencyIn(CurrencyBase):
    pass


class Currency(CurrencyBase):
    id: int


class CurrencyOut(CurrencyBase):
    pass


class SalaryBase(Base):
    amount: int


class SalaryIn(SalaryBase):
    currency: CurrencyIn


class Salary(SalaryBase):
    id: int
    currency: Currency


class SalaryOut(SalaryBase):
    currency: CurrencyOut


class EmployeeBase(Base):
    name: str
    surname: str
    patronymic: str
    service_number: int
    department_number: int
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

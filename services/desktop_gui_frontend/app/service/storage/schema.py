import datetime
import decimal

from pydantic import BaseModel, validator


class Base(BaseModel):
    pass


class TitleBase(Base):
    name: str


class TitleIn(Base):
    name: str


class Title(TitleBase):
    id: int


class TitleOut(TitleBase):
    pass


class TopicBase(Base):
    name: str


class TopicIn(Base):
    name: str
    number: str


class Topic(TopicBase):
    id: int
    number: int


class TopicOut(TopicBase):
    number: int


class PostBase(Base):
    name: str


class PostIn(Base):
    name: str
    code: str


class Post(PostBase):
    id: int
    code: int


class PostOut(PostBase):
    code: int


class CurrencyBase(Base):
    name: str


class CurrencyIn(Base):
    name: str


class Currency(CurrencyBase):
    id: int


class CurrencyOut(CurrencyBase):
    pass


class SalaryBase(Base):
    amount: decimal.Decimal


class SalaryIn(Base):
    amount: str
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


class EmployeeIn(Base):
    name: str
    surname: str
    patronymic: str
    service_number: str
    department_number: str
    employment_date: str
    topic: TopicIn
    post: PostIn
    salary: SalaryIn
    titles: list[TitleIn]

    @validator("employment_date", pre=True)
    def date_to_str(cls, employment_date: datetime.date) -> str:
        return str(employment_date)


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


class TopicSearchModel(Base):
    name: str | None = None
    number: str | None = None


class PostSearchModel(Base):
    name: str | None = None
    code: str | None = None


class CurrencySearchModel(Base):
    name: str | None = None


class SalarySearchModel(Base):
    amount: str | None = None
    currency: CurrencySearchModel | None = None


class TitleSearchModel(Base):
    name: str | None = None


class EmployeeSearchModel(Base):
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None
    service_number: str | None = None
    department_number: str | None = None
    employment_date: str | None = None
    topic: TopicSearchModel | None = None
    post: PostSearchModel | None = None
    salary: SalarySearchModel | None = None
    titles: list[TitleSearchModel] | None = None

import datetime
import decimal

from pydantic import BaseModel, Field, validator

from . import utils


class Base(BaseModel, frozen=True):
    pass


class TopicBase(Base):
    name: str = Field(min_length=5, max_length=500)
    number: int = Field(ge=0)

    @validator("name")
    def name_capitalize(cls, name: str) -> str:
        return name.capitalize()


class TopicIn(TopicBase):
    pass


class Topic(TopicBase):
    id: int

    class Config:
        orm_mode = True


class TopicOut(TopicBase):
    id: int


class PostBase(Base):
    name: str = Field(min_length=3, max_length=200)
    code: int = Field(ge=0)

    @validator("name")
    def name_capitalize(cls, name: str) -> str:
        return name.capitalize()


class PostIn(PostBase):
    pass


class Post(PostBase):
    id: int

    class Config:
        orm_mode = True


class PostOut(PostBase):
    id: int


class TitleBase(Base):
    name: str = Field(min_length=2, max_length=200)

    @validator("name")
    def name_capitalize(cls, name: str) -> str:
        return name.capitalize()


class TitleIn(TitleBase):
    pass


class Title(TitleBase):
    id: int

    class Config:
        orm_mode = True


class TitleOut(TitleBase):
    id: int


class CurrencyBase(Base):
    name: str = Field(min_length=3, max_length=3, example="RUB")

    @validator("name")
    def name_uppercase(cls, name: str) -> str:
        return name.upper()

    @validator("name")
    def name_is_alpha(cls, name: str) -> str:
        if not name.isalpha():
            raise ValueError("Name should be alphabetic")
        return name

    @validator("name")
    def currency_exist(cls, name: str) -> str:
        if name not in utils.currencies:
            raise ValueError("Unknown currency")
        return name


class CurrencyIn(CurrencyBase):
    pass


class Currency(CurrencyBase):
    id: int

    class Config:
        orm_mode = True


class CurrencyOut(CurrencyBase):
    id: int


class SalaryBase(Base):
    amount: decimal.Decimal = Field(gt=0)

    @validator("amount")
    def salary_is_normal(cls, amount: decimal.Decimal) -> decimal.Decimal:
        if not amount.is_normal():
            raise ValueError("Salary amount is not normal number")
        return amount

    @validator("amount")
    def salary_has_correct_scale(cls, amount: decimal.Decimal) -> decimal.Decimal:
        if len(str(amount % 1)) - 2 > 2:
            raise ValueError("Salary amount has too much scale. Max scale is 2")
        return amount


class SalaryIn(SalaryBase):
    currency: CurrencyIn


class Salary(SalaryBase):
    id: int
    currency: Currency

    class Config:
        orm_mode = True


class SalaryOut(SalaryBase):
    id: int
    currency: CurrencyOut


class EmployeeBase(Base):
    name: str = Field(max_length=100, min_length=1)
    surname: str = Field(max_length=100, min_length=1)
    patronymic: str = Field(max_length=100, min_length=1)
    department_number: int = Field(ge=0)
    service_number: int = Field(ge=0)
    employment_date: datetime.date

    @validator("name", pre=True)
    def name_capitalize(cls, name: str) -> str:
        return name.capitalize()

    @validator("name")
    def name_is_alpha(cls, name: str) -> str:
        if not name.isalpha():
            raise ValueError("Name should be alphabetic")
        return name

    @validator("surname", pre=True)
    def surname_capitalize(cls, surname: str) -> str:
        return surname.capitalize()

    @validator("surname")
    def surname_is_alpha(cls, surname: str) -> str:
        if not surname.isalpha():
            raise ValueError("Surname should be alphabetic")
        return surname

    @validator("patronymic", pre=True)
    def patronymic_capitalize(cls, patronymic: str) -> str:
        return patronymic.capitalize()

    @validator("surname")
    def patronymic_is_alpha(cls, patronymic: str) -> str:
        if not patronymic.isalpha():
            raise ValueError("Patronymic should be alphabetic")
        return patronymic

    @validator("employment_date")
    def employment_date_not_greater_than_today(cls, employment_date: datetime.date) -> datetime.date:
        now_utc = datetime.datetime.utcnow()
        max_timezone_shift = 14
        max_possible_time = now_utc + datetime.timedelta(hours=max_timezone_shift)
        max_possible_day = max_possible_time.date()

        if employment_date > max_possible_day:
            raise ValueError("Employment date greater than now")

        return employment_date

    @validator("employment_date")
    def employment_date_not_to_small(cls, employment_date: datetime.date) -> datetime.date:
        if employment_date < datetime.date(year=1920, day=1, month=1):
            raise ValueError("Employment date is too small. Min employment date is 1920-01-01")
        return employment_date


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

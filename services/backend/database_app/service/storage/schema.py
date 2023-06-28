from pydantic import BaseModel


class Base(BaseModel):
    pass


class EmployeeBase(Base):
    last_name: str
    first_name: str
    patronymic: str


class EmployeeIn(EmployeeBase):
    pass


class EmployeeOut(EmployeeBase):
    pass


class Employee(EmployeeBase):
    class Config:
        orm_mode = True

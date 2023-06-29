from pydantic import BaseModel


class Base(BaseModel):
    pass


class EmployeeBase(Base):
    name: str
    surname: str
    patronymic: str


class EmployeeIn(EmployeeBase):
    pass


class Employee(EmployeeBase):
    class Config:
        orm_mode = True


class EmployeeOut(EmployeeBase):
    pass

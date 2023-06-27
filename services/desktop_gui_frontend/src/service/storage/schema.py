from pydantic import BaseModel


class Base(BaseModel):
    pass


class EmployeeBase(Base):
    first_name: str
    last_name: str
    patronymic: str


class EmployeeIn(EmployeeBase):
    pass


class Employee(EmployeeBase):
    class Config:
        orm_mode = True


class EmployeeOut(EmployeeBase):
    pass

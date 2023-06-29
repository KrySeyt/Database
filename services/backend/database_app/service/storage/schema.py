from pydantic import BaseModel


class Base(BaseModel):
    pass


class EmployeeBase(Base):
    name: str
    surname: str
    patronymic: str


class EmployeeIn(EmployeeBase):
    pass


class EmployeeInWithID(EmployeeBase):
    id: int


class EmployeeOut(EmployeeBase):
    id: int


class Employee(EmployeeBase):
    id: int

    class Config:
        orm_mode = True

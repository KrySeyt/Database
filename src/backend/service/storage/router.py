from fastapi import APIRouter

from . import schema
from . import service

router = APIRouter()


@router.post(
    path="/employee",
    response_model=schema.EmployeeOut
)
async def create_employee(employee: schema.EmployeeIn) -> schema.Employee:
    return await service.create_employee(employee)

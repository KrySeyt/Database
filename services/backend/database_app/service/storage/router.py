from fastapi import APIRouter

from database_app.service.storage import schema, service

router = APIRouter()


@router.post(
    path="/employee",
    response_model=schema.EmployeeOut
)
async def create_employee(employee: schema.EmployeeIn) -> schema.Employee:
    return await service.create_employee(employee)

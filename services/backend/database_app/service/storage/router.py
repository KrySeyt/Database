from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from database_app.service.storage import schema, service
from ... import dependencies

router = APIRouter()


@router.post(
    path="/employee",
    response_model=schema.EmployeeOut
)
async def create_employee(
        employee: schema.EmployeeIn,
        db: Annotated[AsyncSession, Depends(dependencies.get_db)]
) -> schema.Employee:
    return await service.create_employee(db, employee)

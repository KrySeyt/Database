from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status

from database_app.service.storage import schema as storage_schema
from ...dependencies import get_db_stub
from . import service
from . import exceptions


router = APIRouter()


@router.get(
    path="/statistics/highest_paid_employee",
    response_model=storage_schema.EmployeeOut,
    status_code=status.HTTP_200_OK,
)
async def get_highest_paid_employee(
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> storage_schema.Employee:
    employee = await service.get_highest_paid_employee(db)
    if not employee:
        raise exceptions.NoEmployees("Not single employee exist")
    return employee

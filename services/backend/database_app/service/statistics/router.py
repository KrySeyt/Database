from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, Path, Body

from database_app.service.storage import schema as storage_schema
from ...dependencies import get_db_stub
from . import service

router = APIRouter(tags=["Statistics"], prefix="/statistics")


@router.get(
    path="/highest_paid_employees/{employees_count}",
    response_model=list[storage_schema.EmployeeOut],
    status_code=status.HTTP_200_OK,
)
async def get_highest_paid_employees(
        employees_count: Annotated[int, Path()],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> list[storage_schema.Employee]:
    employees = await service.get_highest_paid_employees(db, employees_count)
    return employees


@router.get(
    path="/work_longest_employees/{employees_count}",
    response_model=list[storage_schema.EmployeeOut],
    status_code=status.HTTP_200_OK,
)
async def get_work_longest_employees(
        employees_count: Annotated[int, Path()],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> list[storage_schema.Employee]:
    employees = await service.get_work_longest_employee(db, employees_count)
    return employees


@router.post(
    path="/title_employees_growth_history",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        2023: 5,
                        2022: 10
                    }
                }
            }
        }
    },
    status_code=status.HTTP_200_OK,
)
async def get_title_employees_growth(
        title: Annotated[storage_schema.TitleIn, Body()],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> dict[int, int]:
    employees_growth = await service.get_title_employees_growth_history(db, title)
    return employees_growth

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, Body, Path

from database_app.service.storage import schema as storage_schema
from ...dependencies import get_db_stub
from . import service
from .. import exceptions


router = APIRouter(tags=["Forecasts"], prefix="/forecasts")


@router.post(
    path="/title_employees_growth/{years_count}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        2025: 5,
                        2024: 10
                    }
                }
            }
        }
    },
    status_code=status.HTTP_200_OK,
)
async def get_certain_title_employees_growth(
        title: Annotated[storage_schema.TitleIn, Body()],
        years_count: Annotated[int, Path()],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> dict[int, int]:
    employees_growth = await service.get_title_employees_growth(db, title, years_count)
    if not employees_growth:
        raise exceptions.NoEmployeesExist("Not single employee exist")
    return employees_growth

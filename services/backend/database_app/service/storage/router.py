from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Path, HTTPException, status, Query

from database_app.service.storage import schema, service
from ...dependencies import get_db_stub
from .dependencies import employee_service_number_unique, employee_id_exist

router = APIRouter()


@router.post(
    path="/employee",
    response_model=schema.EmployeeOut,
    status_code=status.HTTP_201_CREATED
)
async def create_employee(
        employee: Annotated[schema.EmployeeIn, Depends(employee_service_number_unique)],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> schema.Employee:
    return await service.create_employee(db, employee)


@router.get(
    path="/employee/{employee_id}",
    response_model=schema.EmployeeOut
)
async def get_employee(
        employee_id: Annotated[int, Path()],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> schema.Employee:
    employee = await service.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return employee


@router.get(
    path="/employees",
    response_model=list[schema.EmployeeOut]
)
async def get_employees(
        db: Annotated[AsyncSession, Depends(get_db_stub)],
        skip: int = Query(default=0),
        limit: int = Query(default=100),
) -> list[schema.Employee]:
    return await service.get_employees(db, skip, limit)


@router.put(
    path="/employee/{employee_id}",
    response_model=schema.EmployeeOut
)
async def update_employee(
        employee_in: Annotated[schema.EmployeeIn, Depends(employee_service_number_unique)],
        employee_id: Annotated[int, Depends(employee_id_exist)],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> schema.Employee:
    return await service.update_employee(db, employee_in, employee_id)


@router.delete(
    path="/employee/{employee_id}",
    response_model=schema.EmployeeOut
)
async def delete_employee(
        employee_id: Annotated[int, Path()],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> schema.Employee:
    employee = await service.delete_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return employee


@router.post(
    path="/search/employees",
    response_model=list[schema.EmployeeOut]
)
async def search_employees(
        search_model: schema.EmployeeSearchModel,
        db: Annotated[AsyncSession, Depends(get_db_stub)]
) -> list[schema.Employee]:
    return await service.search_employees(db, search_model)

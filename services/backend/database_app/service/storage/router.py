from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query, status, Body

from database_app.service.storage import schema, service
from ...dependencies import get_db_stub
from ...schema import ErrorResponseBody
from .dependencies import employee_service_number_unique, employee_id_exists


router = APIRouter(tags=["Storage"], prefix="/storage")


@router.post(
    path="/employee",
    response_model=schema.EmployeeOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
        employee: Annotated[schema.EmployeeIn, Depends(employee_service_number_unique)],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> schema.Employee:
    return await service.create_employee(db, employee)


@router.get(
    path="/employee/{employee_id}",
    response_model=schema.EmployeeOut,
    responses={
        404: {"model": ErrorResponseBody}
    }
)
async def get_employee(
        employee_id: Annotated[int, Depends(employee_id_exists)],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> schema.Employee:
    employee = await service.get_employee(db, employee_id)
    assert employee
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
    response_model=schema.EmployeeOut,
    responses={
        404: {"model": ErrorResponseBody}
    }
)
async def update_employee(
        employee_in: Annotated[schema.EmployeeIn, Body()],
        employee_id: Annotated[int, Depends(employee_id_exists)],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> schema.Employee:
    employee = await service.update_employee(db, employee_in, employee_id)
    assert employee
    return employee


@router.delete(
    path="/employee/{employee_id}",
    response_model=schema.EmployeeOut,
    responses={
        404: {"model": ErrorResponseBody}
    }
)
async def delete_employee(
        employee_id: Annotated[int, Depends(employee_id_exists)],
        db: Annotated[AsyncSession, Depends(get_db_stub)],
) -> schema.Employee:
    employee = await service.delete_employee(db, employee_id)
    assert employee
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

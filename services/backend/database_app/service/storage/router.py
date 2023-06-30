from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Path, HTTPException, status, Query

from database_app.service.storage import schema, service
from ... import dependencies

router = APIRouter()


@router.post(
    path="/employee",
    response_model=schema.EmployeeOut,
    status_code=status.HTTP_201_CREATED
)
async def create_employee(
        employee: schema.EmployeeIn,
        db: Annotated[AsyncSession, Depends(dependencies.get_db_stub)],
) -> schema.Employee:

    return await service.create_employee(db, employee)


@router.get(
    path="/employee/{employee_id}",
    response_model=schema.EmployeeOut,

)
async def get_employee(
        employee_id: Annotated[int, Path()],
        db: Annotated[AsyncSession, Depends(dependencies.get_db_stub)],
) -> schema.Employee:

    employee = await service.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return employee


@router.get(
    path="/employees",
    response_model=list[schema.EmployeeOut],
)
async def get_employees(
        db: Annotated[AsyncSession, Depends(dependencies.get_db_stub)],
        skip: int = Query(default=0),
        limit: int = Query(default=100),
) -> list[schema.Employee]:

    return await service.get_employees(db, skip, limit)


@router.put(
    path="/employee",
    response_model=schema.EmployeeOut,
    status_code=status.HTTP_201_CREATED
)
async def update_employee(
        employee_in: schema.EmployeeInWithID,
        db: Annotated[AsyncSession, Depends(dependencies.get_db_stub)],
) -> schema.Employee:

    employee = await service.update_employee(db, employee_in)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return employee

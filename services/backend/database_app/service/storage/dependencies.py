from typing import Annotated

from fastapi import Depends, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from database_app.dependencies import get_db_stub
from . import service
from .schema import EmployeeIn
from .exceptions import EmployeeServiceNumberNotUnique, EmployeeIDDoesntExist


async def employee_service_number_not_occupied(
        db: Annotated[AsyncSession, Depends(get_db_stub)],
        employee_in: Annotated[EmployeeIn, Body()]
) -> EmployeeIn:

    if await service.is_service_number_occupied(db, employee_in.service_number):
        raise EmployeeServiceNumberNotUnique("Employee service number must be unique")
    return employee_in


async def employee_service_number_available_to_employee(
        db: Annotated[AsyncSession, Depends(get_db_stub)],
        employee_in: Annotated[EmployeeIn, Body()],
        employee_id: Annotated[int, Path()]
) -> EmployeeIn:

    if await service.is_service_number_available_to_employee(db, employee_in.service_number, employee_id):
        return employee_in
    raise EmployeeServiceNumberNotUnique("Employee service number must be unique")


async def employee_id_exists(
        db: Annotated[AsyncSession, Depends(get_db_stub)],
        employee_id: Annotated[int, Path()]
) -> int:
    if not await service.is_employee_id_exist(db, employee_id):
        raise EmployeeIDDoesntExist("ID must be occupied by employee")
    return employee_id

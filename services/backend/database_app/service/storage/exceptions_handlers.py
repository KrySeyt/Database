from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from .exceptions import EmployeeServiceNumberNotUnique, EmployeeIDDoesntExist
from ...schema import ErrorResponseBody, ErrorInfo


async def employee_service_number_not_unique_handler(request: Request, exc: EmployeeServiceNumberNotUnique) -> Response:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponseBody(
            [
                ErrorInfo(
                    loc=[
                        "body",
                        "service_number"
                    ],
                    msg=str(exc),
                    type_="value_error.not_unique"
                )
            ]
        ).dict()
    )


async def employee_id_doesnt_exist_handler(request: Request, exc: EmployeeIDDoesntExist) -> Response:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponseBody(
            [
                ErrorInfo(
                    loc=[
                        "body",
                        "id"
                    ],
                    msg=str(exc),
                    type_="value_error.doesnt_exist"
                )
            ]
        ).dict()
    )

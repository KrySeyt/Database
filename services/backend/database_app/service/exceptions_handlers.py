from fastapi import Request, Response
from fastapi.responses import JSONResponse

from database_app.schema import ErrorResponseBody, ErrorInfo
from database_app.service.exceptions import NoEmployeesExist


async def no_employees_handler(request: Request, exception: NoEmployeesExist) -> Response:
    return JSONResponse(
        status_code=404,
        content=ErrorResponseBody(
            [
                ErrorInfo(
                    loc=[
                        "database",
                        "employees"
                    ],
                    msg=str(exception),
                    type_="db_error.no_employees"
                )
            ]
        )
    )

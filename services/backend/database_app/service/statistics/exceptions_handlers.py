from fastapi import Request, Response
from fastapi.responses import JSONResponse

from ...schema import ErrorResponseBody, ErrorInfo
from .exceptions import NoEmployees


async def no_employees_handler(request: Request, exception: NoEmployees) -> Response:
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

from fastapi import FastAPI

from database_app.service.storage.router import router as storage_router
from database_app.dependencies import get_db, get_db_stub
from database_app.service.storage.exceptions import EmployeeServiceNumberNotUnique
from database_app.service.storage.exceptions_handlers import employee_service_number_not_unique_handler


app = FastAPI()
app.include_router(storage_router)

app.dependency_overrides[get_db_stub] = get_db
app.add_exception_handler(EmployeeServiceNumberNotUnique, employee_service_number_not_unique_handler)

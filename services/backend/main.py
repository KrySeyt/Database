from fastapi import FastAPI

from database_app.service.storage.router import router as storage_router
from database_app.dependencies import get_db, get_db_stub


app = FastAPI()
app.include_router(storage_router)

app.dependency_overrides[get_db_stub] = get_db

from fastapi import FastAPI

from database_app.service.storage.router import router as storage_router

app = FastAPI()
app.include_router(storage_router)

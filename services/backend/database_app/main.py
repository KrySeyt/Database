from fastapi import FastAPI

from service.storage.router import router as storage_router

app = FastAPI()
app.include_router(storage_router)

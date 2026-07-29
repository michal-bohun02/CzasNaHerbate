from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from core.config import settings
from db.config import TORTOISE_ORM
from api.v1.router import api_router

app = FastAPI(title=settings.project_name)

app.include_router(api_router, prefix="/api/v1")

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/")
def read_root():
    return {"message": "Backend działa"}
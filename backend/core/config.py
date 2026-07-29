import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgres://postgres:postgres@localhost:5433/czasnaherbate"
    )
    project_name: str = "CzasNaHerbate API"

settings = Settings()
from pydantic import BaseModel
from datetime import datetime

class ItemCreate(BaseModel):
    name: str
    description: str | None = None

class ItemOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True
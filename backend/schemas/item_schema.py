from pydantic import BaseModel
from datetime import datetime

class ItemCreate(BaseModel):
    name: str
    slug: str | None = None
    description: str | None = None

class ItemOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class SearchHit(BaseModel):
    id: int
    name: str
    slug: str
    photo_url: str | None
    category_name: str | None
    category_slug: str | None
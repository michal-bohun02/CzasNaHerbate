from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    position: int


class FilterOptionOut(BaseModel):
    id: str
    name: str
    slug: str
    position: int
    source: str


class FilterGroupOut(BaseModel):
    id: str
    name: str
    slug: str
    position: int
    options: list[FilterOptionOut]


class CategoryFiltersOut(BaseModel):
    id: int
    name: str
    slug: str
    price_min: Decimal | None = None
    price_max: Decimal | None = None
    groups: list[FilterGroupOut]


class CatalogItemOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None = None
    photo_url: str | None = None
    price: Decimal | None = None
    badges: list[FilterOptionOut]

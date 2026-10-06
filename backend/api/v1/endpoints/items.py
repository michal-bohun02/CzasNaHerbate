import re
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query
from tortoise import connections

from core.config import settings
from models.item_model import Item
from schemas.item_schema import ItemCreate, ItemOut, SearchHit

router = APIRouter()


def _fold(value: str) -> str:
    return value.lower().translate(str.maketrans("ąćęłńóśźż", "acelnoszz"))


def _photo_url(storage_key: str) -> str:
    key = quote(storage_key, safe="/")
    return f"{settings.minio_public_url.rstrip('/')}/{settings.minio_bucket}/{key}"


def slugify(value: str) -> str:
    slug = value.strip().lower().replace("_", "-")
    slug = re.sub(r"[^a-z0-9-]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "item"


async def unique_slug(base: str) -> str:
    slug = base
    number = 2
    while await Item.filter(slug=slug).exists():
        slug = f"{base}-{number}"
        number += 1
    return slug


@router.post("/", response_model=ItemOut)
async def create_item(item: ItemCreate):
    payload = item.model_dump()
    payload["slug"] = await unique_slug(slugify(payload["slug"] or payload["name"]))
    obj = await Item.create(**payload)
    return obj

@router.get("/", response_model=list[ItemOut])
async def list_items():
    return await Item.all()


@router.get("/search", response_model=list[SearchHit])
async def search_items(q: str = Query(default=""), limit: int = Query(default=8, ge=1, le=20)):
    folded = _fold(q.strip())
    if len(folded) < 2:
        return []
    pattern = f"%{folded.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')}%"
    connection = connections.get("default")
    rows = await connection.execute_query_dict(
        """
        SELECT
            i.id,
            i.name,
            i.slug,
            photo.storage_key,
            root.slug AS category_slug,
            root.name AS category_name
        FROM items i
        LEFT JOIN LATERAL (
            SELECT storage_key
            FROM item_photos
            WHERE item_id = i.id
            ORDER BY position, id
            LIMIT 1
        ) photo ON TRUE
        LEFT JOIN LATERAL (
            SELECT c.slug, c.name
            FROM item_categories ic
            JOIN categories c ON c.id = ic.category_id
            WHERE ic.item_id = i.id
              AND c.parent_id IS NULL
            ORDER BY ic.is_primary DESC, c.position, c.id
            LIMIT 1
        ) root ON TRUE
        WHERE translate(lower(i.name), 'ąćęłńóśźż', 'acelnoszz') ILIKE $1 ESCAPE '\\'
           OR translate(lower(coalesce(i.description, '')), 'ąćęłńóśźż', 'acelnoszz') ILIKE $1 ESCAPE '\\'
        ORDER BY
            CASE
                WHEN translate(lower(i.name), 'ąćęłńóśźż', 'acelnoszz') ILIKE $1 ESCAPE '\\' THEN 0
                ELSE 1
            END,
            i.name
        LIMIT $2
        """,
        [pattern, limit],
    )
    return [
        SearchHit(
            id=row["id"],
            name=row["name"],
            slug=row["slug"],
            photo_url=_photo_url(row["storage_key"]) if row["storage_key"] else None,
            category_name=row["category_name"],
            category_slug=row["category_slug"],
        )
        for row in rows
    ]


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: int):
    obj = await Item.get_or_none(id=item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj
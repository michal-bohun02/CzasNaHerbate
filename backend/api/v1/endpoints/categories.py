from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from tortoise import connections

from core.config import settings
from models.attribute_model import Attribute
from models.category_model import Category
from models.item_model import Item
from schemas.category_schema import (
    CatalogItemOut,
    CategoryFiltersOut,
    CategoryOut,
    FilterGroupOut,
    FilterOptionOut,
)

router = APIRouter()


@router.get("", response_model=list[CategoryOut])
async def list_categories():
    return await Category.filter(parent_id__isnull=True).order_by("position", "id")


@router.get("/{slug}/filters", response_model=CategoryFiltersOut)
async def category_filters(slug: str):
    category = await Category.get_or_none(slug=slug, parent_id__isnull=True)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    groups = await Category.filter(parent_id=category.id).order_by("position", "id")
    group_ids = [group.id for group in groups]
    options = (
        await Category.filter(parent_id__in=group_ids).order_by("position", "id")
        if group_ids
        else []
    )
    options_by_parent: dict[int, list[FilterOptionOut]] = {group_id: [] for group_id in group_ids}
    for option in options:
        options_by_parent[option.parent_id].append(
            FilterOptionOut(
                id=f"category:{option.id}",
                name=option.name,
                slug=option.slug,
                position=option.position,
                source="category",
            )
        )

    category_ids = [category.id, *group_ids, *[option.id for option in options]]
    price_min, price_max = await _price_bounds(category_ids)
    filter_groups = [
        FilterGroupOut(
            id=f"category:{group.id}",
            name=group.name,
            slug=group.slug,
            position=group.position,
            options=options_by_parent[group.id],
        )
        for group in groups
    ]
    properties = await Attribute.filter(category_id=category.id, type="bool").order_by("position", "id")
    if properties:
        filter_groups.append(
            FilterGroupOut(
                id="attribute:wlasciwosci",
                name="Właściwości",
                slug="wlasciwosci",
                position=100,
                options=[
                    FilterOptionOut(
                        id=f"attribute:{prop.id}",
                        name=prop.name,
                        slug=prop.slug,
                        position=prop.position,
                        source="attribute",
                    )
                    for prop in properties
                ],
            )
        )

    return CategoryFiltersOut(
        id=category.id,
        name=category.name,
        slug=category.slug,
        price_min=price_min,
        price_max=price_max,
        groups=filter_groups,
    )


@router.get("/{slug}/items", response_model=list[CatalogItemOut])
async def category_items(slug: str):
    category = await Category.get_or_none(slug=slug, parent_id__isnull=True)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    groups = await Category.filter(parent_id=category.id)
    group_ids = {group.id for group in groups}
    item_ids = await Item.filter(category_links__category_id=category.id).values_list("id", flat=True)
    if not item_ids:
        return []

    items = (
        await Item.filter(id__in=list(item_ids))
        .order_by("id")
        .prefetch_related(
            "photos",
            "variants",
            "category_links__category",
            "attribute_links__attribute",
        )
    )
    return [_catalog_item(item, category.id, group_ids) for item in items]


def _catalog_item(item, root_id: int, group_ids: set[int]) -> CatalogItemOut:
    photos = sorted(item.photos, key=lambda photo: (photo.position, photo.id))
    photo_url = _photo_url(photos[0].storage_key) if photos else None
    prices = [variant.price for variant in item.variants]
    badges = []
    for link in item.category_links:
        linked = link.category
        if linked.parent_id in group_ids and linked.id != root_id:
            badges.append(
                FilterOptionOut(
                    id=f"category:{linked.id}",
                    name=linked.name,
                    slug=linked.slug,
                    position=linked.position,
                    source="category",
                )
            )
    for link in item.attribute_links:
        prop = link.attribute
        if prop.category_id == root_id and prop.type == "bool":
            badges.append(
                FilterOptionOut(
                    id=f"attribute:{prop.id}",
                    name=prop.name,
                    slug=prop.slug,
                    position=100 + prop.position,
                    source="attribute",
                )
            )
    badges.sort(key=lambda badge: (badge.position, badge.id))
    return CatalogItemOut(
        id=item.id,
        name=item.name,
        slug=item.slug,
        description=item.description,
        photo_url=photo_url,
        price=min(prices) if prices else None,
        badges=badges,
    )


def _photo_url(storage_key: str) -> str:
    key = quote(storage_key, safe="/")
    return f"{settings.minio_public_url.rstrip('/')}/{settings.minio_bucket}/{key}"


async def _price_bounds(category_ids: list[int]):
    if not category_ids:
        return None, None
    connection = connections.get("default")
    rows = await connection.execute_query_dict(
        """
        SELECT MIN(v.price) AS price_min, MAX(v.price) AS price_max
        FROM item_variants v
        INNER JOIN item_categories ic ON ic.item_id = v.item_id
        WHERE ic.category_id = ANY($1::int[])
        """,
        [category_ids],
    )
    if not rows:
        return None, None
    return rows[0]["price_min"], rows[0]["price_max"]

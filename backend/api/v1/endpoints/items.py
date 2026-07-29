from fastapi import APIRouter, HTTPException
from models.item_model import Item
from schemas.item_schema import ItemCreate, ItemOut

router = APIRouter()

@router.post("/", response_model=ItemOut)
async def create_item(item: ItemCreate):
    obj = await Item.create(**item.model_dump())
    return obj

@router.get("/", response_model=list[ItemOut])
async def list_items():
    return await Item.all()

@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: int):
    obj = await Item.get_or_none(id=item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj
from urllib.parse import quote

from pydantic import BaseModel, computed_field, field_validator

from core.config import settings


class ItemPhotoCreate(BaseModel):
    item_id: int
    storage_key: str
    position: int = 0

    @field_validator("storage_key")
    @classmethod
    def storage_key_is_object_key(cls, value: str) -> str:
        key = value.strip().lstrip("/")
        bucket_prefix = f"{settings.minio_bucket}/"
        if not key or "\\" in key or "://" in key or key.startswith(bucket_prefix):
            raise ValueError(
                "storage_key must be a MinIO object key inside the bucket, not a URL or bucket path"
            )
        return key

class ItemPhotoOut(BaseModel):
    id: int
    item_id: int
    storage_key: str
    position: int

    @computed_field
    @property
    def url(self) -> str:
        key = quote(self.storage_key, safe="/")
        return f"{settings.minio_public_url.rstrip('/')}/{settings.minio_bucket}/{key}"

    class Config:
        from_attributes = True

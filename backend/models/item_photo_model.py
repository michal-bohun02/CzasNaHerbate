from tortoise import fields
from tortoise.models import Model


class ItemPhoto(Model):
    id = fields.IntField(pk=True)
    item: fields.ForeignKeyRelation["Item"] = fields.ForeignKeyField(
        "models.Item",
        related_name="photos",
        on_delete=fields.CASCADE,
    )
    storage_key = fields.CharField(max_length=1024, unique=True)
    position = fields.IntField(default=0)

    class Meta:
        table = "item_photos"
        indexes = (("item", "position"),)

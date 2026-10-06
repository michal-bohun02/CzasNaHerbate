from tortoise import fields
from tortoise.models import Model


class Category(Model):
    id = fields.IntField(pk=True)
    parent: fields.ForeignKeyNullableRelation["Category"] = fields.ForeignKeyField(
        "models.Category",
        related_name="children",
        null=True,
        on_delete=fields.SET_NULL,
    )
    name = fields.CharField(max_length=255)
    slug = fields.CharField(max_length=255, unique=True)
    position = fields.IntField(default=0)

    class Meta:
        table = "categories"


class ItemCategory(Model):
    item: fields.ForeignKeyRelation["Item"] = fields.ForeignKeyField(
        "models.Item",
        related_name="category_links",
        on_delete=fields.CASCADE,
    )
    category: fields.ForeignKeyRelation[Category] = fields.ForeignKeyField(
        "models.Category",
        related_name="item_links",
        on_delete=fields.CASCADE,
    )
    is_primary = fields.BooleanField(default=False)

    class Meta:
        table = "item_categories"
        unique_together = (("item", "category"),)

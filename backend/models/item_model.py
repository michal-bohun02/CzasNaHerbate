from tortoise import fields
from tortoise.models import Model


class Item(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    slug = fields.CharField(max_length=255, unique=True)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    photos: fields.ReverseRelation["ItemPhoto"]
    variants: fields.ReverseRelation["ItemVariant"]
    category_links: fields.ReverseRelation["ItemCategory"]
    attribute_links: fields.ReverseRelation["ItemAttribute"]

    class Meta:
        table = "items"

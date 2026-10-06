from tortoise import fields
from tortoise.models import Model


class Attribute(Model):
    id = fields.IntField(pk=True)
    category: fields.ForeignKeyNullableRelation["Category"] = fields.ForeignKeyField(
        "models.Category",
        related_name="attributes",
        null=True,
        on_delete=fields.SET_NULL,
    )
    name = fields.CharField(max_length=255)
    slug = fields.CharField(max_length=255, unique=True)
    type = fields.CharField(max_length=16, null=True)
    unit = fields.CharField(max_length=32, null=True)
    position = fields.IntField(default=0)

    class Meta:
        table = "attributes"


class ItemAttribute(Model):
    item: fields.ForeignKeyRelation["Item"] = fields.ForeignKeyField(
        "models.Item",
        related_name="attribute_links",
        on_delete=fields.CASCADE,
    )
    attribute: fields.ForeignKeyRelation[Attribute] = fields.ForeignKeyField(
        "models.Attribute",
        related_name="item_links",
        on_delete=fields.CASCADE,
    )
    value_text = fields.CharField(max_length=255, null=True)
    value_num = fields.DecimalField(max_digits=12, decimal_places=4, null=True)

    class Meta:
        table = "item_attributes"
        unique_together = (("item", "attribute"),)

from tortoise import fields
from tortoise.models import Model


class ItemVariant(Model):
    id = fields.IntField(pk=True)
    item: fields.ForeignKeyRelation["Item"] = fields.ForeignKeyField(
        "models.Item",
        related_name="variants",
        on_delete=fields.CASCADE,
    )
    sku = fields.CharField(max_length=64, unique=True, null=True)
    label = fields.CharField(max_length=64, null=True)
    price = fields.DecimalField(max_digits=12, decimal_places=2)
    stock = fields.IntField(default=0)

    class Meta:
        table = "item_variants"

from tortoise import migrations
from tortoise.migrations import operations as ops
from aerich.coder import decoder, encoder
from tortoise.fields.base import OnDelete
from tortoise.fields.db_defaults import Now
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='Aerich',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('version', fields.CharField(max_length=255)),
                ('app', fields.CharField(max_length=100)),
                ('content', fields.JSONField(encoder=encoder, decoder=decoder)),
            ],
            options={'table': 'aerich', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Item',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('name', fields.CharField(max_length=255)),
                ('description', fields.TextField(null=True, unique=False)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'items', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='ItemPhoto',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('item', fields.ForeignKeyField('models.Item', source_field='item_id', db_constraint=True, to_field='id', related_name='photos', on_delete=OnDelete.CASCADE)),
                ('storage_key', fields.CharField(unique=True, max_length=1024)),
                ('content_type', fields.CharField(max_length=127)),
                ('position', fields.IntField(default=0, db_default=0)),
                ('is_main', fields.BooleanField(default=False, db_default=False)),
                ('width', fields.IntField(null=True)),
                ('height', fields.IntField(null=True)),
                ('created_at', fields.DatetimeField(db_default=Now(), auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'item_photos', 'app': 'models', 'indexes': [Index(fields=['item', 'position'])], 'pk_attr': 'id'},
            bases=['Model'],
        ),
    ]

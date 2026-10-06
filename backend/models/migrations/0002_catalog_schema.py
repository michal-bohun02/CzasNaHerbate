from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0001_adding_item_pic_table')]

    initial = False

    operations = [
        ops.CreateModel(
            name='Attribute',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('name', fields.CharField(max_length=255)),
                ('slug', fields.CharField(unique=True, max_length=255)),
                ('type', fields.CharField(null=True, max_length=16)),
                ('unit', fields.CharField(null=True, max_length=32)),
            ],
            options={'table': 'attributes', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Category',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('parent', fields.ForeignKeyField('models.Category', source_field='parent_id', null=True, db_constraint=True, to_field='id', related_name='children', on_delete=OnDelete.SET_NULL)),
                ('name', fields.CharField(max_length=255)),
                ('slug', fields.CharField(unique=True, max_length=255)),
                ('position', fields.IntField(default=0)),
            ],
            options={'table': 'categories', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='ItemAttribute',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('item', fields.ForeignKeyField('models.Item', source_field='item_id', db_constraint=True, to_field='id', related_name='attribute_links', on_delete=OnDelete.CASCADE)),
                ('attribute', fields.ForeignKeyField('models.Attribute', source_field='attribute_id', db_constraint=True, to_field='id', related_name='item_links', on_delete=OnDelete.CASCADE)),
                ('value_text', fields.CharField(null=True, max_length=255)),
                ('value_num', fields.DecimalField(null=True, max_digits=12, decimal_places=4)),
            ],
            options={'table': 'item_attributes', 'app': 'models', 'unique_together': (('item', 'attribute'),), 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('item', fields.ForeignKeyField('models.Item', source_field='item_id', db_constraint=True, to_field='id', related_name='category_links', on_delete=OnDelete.CASCADE)),
                ('category', fields.ForeignKeyField('models.Category', source_field='category_id', db_constraint=True, to_field='id', related_name='item_links', on_delete=OnDelete.CASCADE)),
                ('is_primary', fields.BooleanField(default=False)),
            ],
            options={'table': 'item_categories', 'app': 'models', 'unique_together': (('item', 'category'),), 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='ItemVariant',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('item', fields.ForeignKeyField('models.Item', source_field='item_id', db_constraint=True, to_field='id', related_name='variants', on_delete=OnDelete.CASCADE)),
                ('sku', fields.CharField(null=True, unique=True, max_length=64)),
                ('label', fields.CharField(null=True, max_length=64)),
                ('price', fields.DecimalField(max_digits=12, decimal_places=2)),
                ('stock', fields.IntField(default=0)),
            ],
            options={'table': 'item_variants', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.AddField(
            model_name='Item',
            name='slug',
            field=fields.CharField(null=True, max_length=255),
        ),
        ops.RunSQL(
            """
            UPDATE items
            SET slug = trim(BOTH '-' FROM regexp_replace(lower(replace(name, '_', '-')), '[^a-z0-9-]+', '-', 'g'))
            WHERE slug IS NULL;
            UPDATE items SET slug = 'item-' || id WHERE slug IS NULL OR slug = '';
            WITH ranked AS (
                SELECT id, row_number() OVER (PARTITION BY slug ORDER BY id) AS n
                FROM items
            )
            UPDATE items AS i
            SET slug = i.slug || '-' || ranked.n
            FROM ranked
            WHERE i.id = ranked.id AND ranked.n > 1;
            """,
            reverse_sql="ALTER TABLE items DROP COLUMN IF EXISTS slug",
        ),
        ops.AlterField(
            model_name='Item',
            name='slug',
            field=fields.CharField(unique=True, max_length=255),
        ),
        ops.AlterField(
            model_name='ItemPhoto',
            name='position',
            field=fields.IntField(default=0),
        ),
        ops.RemoveField(model_name='ItemPhoto', name='content_type'),
        ops.RemoveField(model_name='ItemPhoto', name='created_at'),
        ops.RemoveField(model_name='ItemPhoto', name='height'),
        ops.RemoveField(model_name='ItemPhoto', name='is_main'),
        ops.RemoveField(model_name='ItemPhoto', name='width'),
    ]

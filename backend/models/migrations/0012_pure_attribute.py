from tortoise import migrations
from tortoise.migrations import operations as ops


async def add_pure(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        INSERT INTO attributes (name, slug, type, unit, position, category_id)
        SELECT 'Czyste', 'czyste', 'bool', NULL, 1, id
        FROM categories
        WHERE slug = 'herbata'
        ON CONFLICT (slug) DO UPDATE
        SET name = EXCLUDED.name,
            type = EXCLUDED.type,
            position = EXCLUDED.position,
            category_id = EXCLUDED.category_id
        """
    )
    await client.execute_query(
        """
        INSERT INTO item_attributes (item_id, attribute_id, value_text, value_num)
        SELECT i.id, czyste.id, NULL, NULL
        FROM items i
        JOIN item_categories ic ON ic.item_id = i.id
        JOIN categories herbata ON herbata.id = ic.category_id AND herbata.slug = 'herbata'
        JOIN attributes czyste ON czyste.slug = 'czyste'
        WHERE NOT EXISTS (
            SELECT 1
            FROM item_attributes ia
            JOIN attributes aromatyzowana ON aromatyzowana.id = ia.attribute_id
            WHERE ia.item_id = i.id
              AND aromatyzowana.slug = 'aromatyzowana'
        )
        ON CONFLICT (item_id, attribute_id) DO NOTHING
        """
    )


async def remove_pure(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        "DELETE FROM item_attributes WHERE attribute_id IN (SELECT id FROM attributes WHERE slug = 'czyste')"
    )
    await client.execute_query("DELETE FROM attributes WHERE slug = 'czyste'")


class Migration(migrations.Migration):
    dependencies = [("models", "0011_tea_kinds")]
    initial = False
    operations = [
        ops.RunPython(add_pure, remove_pure),
    ]

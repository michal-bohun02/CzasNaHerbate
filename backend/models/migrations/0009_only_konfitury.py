from tortoise import migrations
from tortoise.migrations import operations as ops

# Produkty, które przed scaleniem były w Powidłach.
POWIDLA_IDS = (191, 207, 211, 222, 250)


async def merge_into_konfitury(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        INSERT INTO item_categories (item_id, category_id, is_primary)
        SELECT ic.item_id, konfitury.id, FALSE
        FROM item_categories ic
        JOIN categories powidla ON powidla.id = ic.category_id AND powidla.slug = 'powidla'
        JOIN categories konfitury ON konfitury.slug = 'konfitury'
        ON CONFLICT (item_id, category_id) DO NOTHING
        """
    )
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE category_id = (SELECT id FROM categories WHERE slug = 'powidla')
        """
    )
    await client.execute_query("DELETE FROM categories WHERE slug = 'powidla'")
    await client.execute_query(
        """
        UPDATE categories
        SET position = position - 1
        WHERE parent_id = (SELECT id FROM categories WHERE slug = 'rodzaj-dodatkow')
          AND position > 1
        """
    )


async def restore_powidla(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        UPDATE categories
        SET position = position + 1
        WHERE parent_id = (SELECT id FROM categories WHERE slug = 'rodzaj-dodatkow')
          AND position >= 1
        """
    )
    await client.execute_query(
        """
        INSERT INTO categories (name, slug, position, parent_id)
        SELECT 'Powidła', 'powidla', 1, id
        FROM categories WHERE slug = 'rodzaj-dodatkow'
        ON CONFLICT (slug) DO NOTHING
        """
    )
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE item_id = ANY($1::int[])
          AND category_id = (SELECT id FROM categories WHERE slug = 'konfitury')
        """,
        [list(POWIDLA_IDS)],
    )
    for item_id in POWIDLA_IDS:
        await client.execute_query(
            """
            INSERT INTO item_categories (item_id, category_id, is_primary)
            SELECT $1, id, FALSE FROM categories WHERE slug = 'powidla'
            ON CONFLICT (item_id, category_id) DO NOTHING
            """,
            [item_id],
        )


class Migration(migrations.Migration):
    dependencies = [("models", "0008_konfitury")]
    initial = False
    operations = [
        ops.RunPython(merge_into_konfitury, restore_powidla),
    ]

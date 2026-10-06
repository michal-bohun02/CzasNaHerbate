from tortoise import migrations
from tortoise.migrations import operations as ops

# Earl Grey Yellow to żółta herbata z bergamotką, nie czarna.
ITEMS = (157, 166)
DESCRIPTION = "Earl Grey Yellow. Żółta herbata z dodatkiem klasycznego aromatu z bergamotki."
PREVIOUS = {
    157: "Earl Grey Yellow. Czarna herbata z bergamotką w łagodniejszym, złocistym wydaniu.",
    166: "Earl Grey Yellow. Czarna herbata z bergamotką o łagodniejszym aromacie.",
}


async def mark_as_yellow(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE item_id = ANY($1::int[])
          AND category_id = (SELECT id FROM categories WHERE slug = 'czarne')
        """,
        [list(ITEMS)],
    )
    for item_id in ITEMS:
        await client.execute_query(
            """
            INSERT INTO item_categories (item_id, category_id, is_primary)
            SELECT $1, id, FALSE FROM categories WHERE slug = 'zolte'
            ON CONFLICT (item_id, category_id) DO NOTHING
            """,
            [item_id],
        )
        await client.execute_query(
            "UPDATE items SET description = $1 WHERE id = $2",
            [DESCRIPTION, item_id],
        )


async def restore_black(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE item_id = ANY($1::int[])
          AND category_id = (SELECT id FROM categories WHERE slug = 'zolte')
        """,
        [list(ITEMS)],
    )
    for item_id in ITEMS:
        await client.execute_query(
            """
            INSERT INTO item_categories (item_id, category_id, is_primary)
            SELECT $1, id, FALSE FROM categories WHERE slug = 'czarne'
            ON CONFLICT (item_id, category_id) DO NOTHING
            """,
            [item_id],
        )
        await client.execute_query(
            "UPDATE items SET description = $1 WHERE id = $2",
            [PREVIOUS[item_id], item_id],
        )


class Migration(migrations.Migration):
    dependencies = [("models", "0009_only_konfitury")]
    initial = False
    operations = [
        ops.RunPython(mark_as_yellow, restore_black),
    ]

from tortoise import migrations
from tortoise.migrations import operations as ops


async def assign(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        INSERT INTO item_categories (item_id, category_id, is_primary)
        SELECT DISTINCT i.id, purpose.id, FALSE
        FROM items i
        JOIN categories purpose ON purpose.slug = 'do-yerba-mate'
        WHERE i.id IN (
            SELECT ic.item_id
            FROM item_categories ic
            JOIN categories c ON c.id = ic.category_id
            WHERE c.slug IN ('matero', 'bombille')
        )
        OR i.name ILIKE '%szczotecz%'
        ON CONFLICT (item_id, category_id) DO NOTHING
        """
    )


async def unassign(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE category_id = (SELECT id FROM categories WHERE slug = 'do-yerba-mate')
          AND (
            item_id IN (
                SELECT ic.item_id
                FROM item_categories ic
                JOIN categories c ON c.id = ic.category_id
                WHERE c.slug IN ('matero', 'bombille')
            )
            OR item_id IN (SELECT id FROM items WHERE name ILIKE '%szczotecz%')
          )
        """
    )


class Migration(migrations.Migration):
    dependencies = [("models", "0013_herbs_blooming_and_tea_updates")]
    initial = False
    operations = [
        ops.RunPython(assign, unassign),
    ]

from tortoise import migrations
from tortoise.migrations import operations as ops


def _leaf(name: str) -> str | None:
    if "matero" in name:
        return None
    if "syrop" in name and "w syropie" not in name and "w-syropie" not in name:
        return "syropy"
    if any(token in name for token in ("konfitura", "mus malinowy", "w syropie", "w-syropie")):
        return "powidla"
    if name.startswith("miod") or " miod" in name:
        return "miody"
    if any(
        token in name
        for token in (
            "w-mlecznej",
            "w-ciemnej",
            "w-bialej",
            "w-białej",
            "w mlecznej",
            "w ciemnej",
            "w bialej",
            "slonym-karmelu",
            "slonym karmelu",
            "ciasteczka",
        )
    ):
        return "slodycze"
    if any(
        token in name
        for token in (
            "czekolada",
            "czekoladka",
            "goraca-czekolada",
            "goraca czekolada",
            "ciemna z",
            "ciemna ze",
            "rzemieslnicza",
        )
    ):
        return "czekolady"
    return None


async def add_additives(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        INSERT INTO categories (name, slug, position, parent_id)
        VALUES ('Dodatki', 'dodatki', 5, NULL)
        ON CONFLICT (slug) DO NOTHING
        """
    )
    await client.execute_query(
        """
        INSERT INTO categories (name, slug, position, parent_id)
        SELECT 'Rodzaj', 'rodzaj-dodatkow', 0, id
        FROM categories WHERE slug = 'dodatki'
        ON CONFLICT (slug) DO NOTHING
        """
    )
    options = (
        ("Syropy", "syropy", 0),
        ("Powidła", "powidla", 1),
        ("Miody", "miody", 2),
        ("Czekolady", "czekolady", 3),
        ("Słodycze", "slodycze", 4),
    )
    for name, slug, position in options:
        await client.execute_query(
            """
            INSERT INTO categories (name, slug, position, parent_id)
            SELECT $1, $2, $3, id
            FROM categories WHERE slug = 'rodzaj-dodatkow'
            ON CONFLICT (slug) DO NOTHING
            """,
            [name, slug, position],
        )

    categories = await client.execute_query_dict("SELECT id, slug FROM categories")
    by_slug = {row["slug"]: row["id"] for row in categories}
    herbata_id = by_slug["herbata"]
    tree = await client.execute_query_dict(
        """
        SELECT id FROM categories
        WHERE id = $1
           OR parent_id = $1
           OR parent_id IN (SELECT id FROM categories WHERE parent_id = $1)
        """,
        [herbata_id],
    )
    tea_ids = [row["id"] for row in tree]
    items = await client.execute_query_dict("SELECT id, lower(name) AS name FROM items")
    for item in items:
        leaf = _leaf(item["name"])
        if leaf is None or leaf not in by_slug:
            continue
        await client.execute_query(
            "DELETE FROM item_categories WHERE item_id = $1 AND category_id = ANY($2::int[])",
            [item["id"], tea_ids],
        )
        await client.execute_query(
            """
            DELETE FROM item_attributes
            WHERE item_id = $1
              AND attribute_id IN (SELECT id FROM attributes WHERE slug = 'aromatyzowana')
            """,
            [item["id"]],
        )
        await client.execute_query(
            """
            INSERT INTO item_categories (item_id, category_id, is_primary)
            VALUES ($1, $2, TRUE)
            ON CONFLICT (item_id, category_id) DO NOTHING
            """,
            [item["id"], by_slug["dodatki"]],
        )
        await client.execute_query(
            """
            INSERT INTO item_categories (item_id, category_id, is_primary)
            VALUES ($1, $2, FALSE)
            ON CONFLICT (item_id, category_id) DO NOTHING
            """,
            [item["id"], by_slug[leaf]],
        )


async def remove_additives(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE category_id IN (
            SELECT id FROM categories
            WHERE slug = 'dodatki'
               OR parent_id = (SELECT id FROM categories WHERE slug = 'dodatki')
               OR parent_id IN (
                    SELECT id FROM categories WHERE parent_id = (SELECT id FROM categories WHERE slug = 'dodatki')
               )
        )
        """
    )
    await client.execute_query(
        """
        DELETE FROM categories
        WHERE slug IN ('syropy', 'powidla', 'miody', 'czekolady', 'slodycze', 'rodzaj-dodatkow', 'dodatki')
        """
    )


class Migration(migrations.Migration):
    dependencies = [("models", "0005_flavored_attribute")]
    initial = False
    operations = [
        ops.RunPython(add_additives, remove_additives),
    ]

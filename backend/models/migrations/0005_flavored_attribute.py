from tortoise import fields, migrations
from tortoise.fields.base import OnDelete
from tortoise.migrations import operations as ops


def _is_chocolate(name: str) -> bool:
    return any(
        token in name
        for token in (
            "w-mlecznej",
            "w-ciemnej",
            "w-bialej",
            "w-białej",
            "slonym-karmelu",
            "slonym karmelu",
            "ziarno-kawy",
            "orzech-laskowy",
            "ciasteczka-korzenne",
        )
    )


def _pure_type(name: str) -> str | None:
    if "pai-mu" in name or "pai mu" in name:
        return "biale"
    if "yellow-buds" in name or "yellow buds" in name:
        return "zolte"
    return None


def _is_flavored(name: str) -> bool:
    return any(
        token in name
        for token in (
            "earl",
            "jasmin",
            "jasmine",
            "ice tea",
            "ice-tea",
            "cinnamon",
            "wisniowo",
            "white-rose",
            "white rose",
            "milk-oolong",
            "milk oolong",
        )
    )


async def move_flavored_to_attribute(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        INSERT INTO attributes (name, slug, type, unit, position, category_id)
        SELECT 'Aromatyzowana', 'aromatyzowana', 'bool', NULL, 0, id
        FROM categories
        WHERE slug = 'herbata'
        ON CONFLICT (slug) DO UPDATE
        SET name = EXCLUDED.name,
            type = EXCLUDED.type,
            position = EXCLUDED.position,
            category_id = EXCLUDED.category_id
        """
    )
    attribute = await client.execute_query_dict(
        "SELECT id FROM attributes WHERE slug = 'aromatyzowana'"
    )
    attribute_id = attribute[0]["id"]
    categories = await client.execute_query_dict("SELECT id, slug FROM categories")
    by_slug = {row["slug"]: row["id"] for row in categories}
    herbata_id = by_slug["herbata"]
    flavored_category_id = by_slug.get("aromatyzowane")

    tree = await client.execute_query_dict(
        """
        SELECT id FROM categories
        WHERE id = $1
           OR parent_id = $1
           OR parent_id IN (SELECT id FROM categories WHERE parent_id = $1)
        """,
        [herbata_id],
    )
    tree_ids = [row["id"] for row in tree]

    if flavored_category_id is not None:
        tagged = await client.execute_query_dict(
            """
            SELECT i.id, lower(i.name) AS name
            FROM items i
            JOIN item_categories ic ON ic.item_id = i.id
            WHERE ic.category_id = $1
            """,
            [flavored_category_id],
        )
        for item in tagged:
            name = item["name"]
            if _is_chocolate(name):
                await client.execute_query(
                    "DELETE FROM item_categories WHERE item_id = $1 AND category_id = ANY($2::int[])",
                    [item["id"], tree_ids],
                )
                continue
            pure = _pure_type(name)
            if pure and pure in by_slug:
                await client.execute_query(
                    """
                    INSERT INTO item_categories (item_id, category_id, is_primary)
                    VALUES ($1, $2, FALSE)
                    ON CONFLICT (item_id, category_id) DO NOTHING
                    """,
                    [item["id"], by_slug[pure]],
                )
            else:
                await client.execute_query(
                    """
                    INSERT INTO item_attributes (item_id, attribute_id, value_text, value_num)
                    VALUES ($1, $2, NULL, NULL)
                    ON CONFLICT (item_id, attribute_id) DO NOTHING
                    """,
                    [item["id"], attribute_id],
                )
            await client.execute_query(
                "DELETE FROM item_categories WHERE item_id = $1 AND category_id = $2",
                [item["id"], flavored_category_id],
            )
        await client.execute_query("DELETE FROM categories WHERE slug = 'aromatyzowane'")

    named = await client.execute_query_dict(
        """
        SELECT i.id, lower(i.name) AS name
        FROM items i
        JOIN item_categories ic ON ic.item_id = i.id
        WHERE ic.category_id = $1
        """,
        [herbata_id],
    )
    for item in named:
        if _is_flavored(item["name"]):
            await client.execute_query(
                """
                INSERT INTO item_attributes (item_id, attribute_id, value_text, value_num)
                VALUES ($1, $2, NULL, NULL)
                ON CONFLICT (item_id, attribute_id) DO NOTHING
                """,
                [item["id"], attribute_id],
            )


async def restore_flavored_category(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        INSERT INTO categories (name, slug, position, parent_id)
        SELECT 'Aromatyzowane', 'aromatyzowane', 7, id
        FROM categories
        WHERE slug = 'rodzaj-herbaty'
        ON CONFLICT (slug) DO NOTHING
        """
    )
    await client.execute_query(
        """
        INSERT INTO item_categories (item_id, category_id, is_primary)
        SELECT ia.item_id, c.id, FALSE
        FROM item_attributes ia
        JOIN attributes a ON a.id = ia.attribute_id
        JOIN categories c ON c.slug = 'aromatyzowane'
        WHERE a.slug = 'aromatyzowana'
        ON CONFLICT (item_id, category_id) DO NOTHING
        """
    )
    await client.execute_query("DELETE FROM item_attributes WHERE attribute_id IN (SELECT id FROM attributes WHERE slug = 'aromatyzowana')")
    await client.execute_query("DELETE FROM attributes WHERE slug = 'aromatyzowana'")


class Migration(migrations.Migration):
    dependencies = [("models", "0004_assign_catalog_items")]
    initial = False
    operations = [
        ops.AddField(
            model_name="Attribute",
            name="category",
            field=fields.ForeignKeyField(
                "models.Category",
                source_field="category_id",
                null=True,
                on_delete=OnDelete.SET_NULL,
                related_name="attributes",
            ),
        ),
        ops.AddField(
            model_name="Attribute",
            name="position",
            field=fields.IntField(default=0),
        ),
        ops.RunPython(move_flavored_to_attribute, restore_flavored_category),
    ]

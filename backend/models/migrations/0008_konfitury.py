from tortoise import migrations
from tortoise.migrations import operations as ops

# Słoiki błędnie przypisane do herbaty. Konfitury i owoce w syropie
# z tej samej serii idą do filtra Konfitury, powidła z etykiety do Powideł.
KONFITURY = (
    141,  # Cytryna z imbirem
    142,  # Cytrynki z whisky
    143,  # Cytrynki z żurawiną i cynamonem
    144,  # Czarny bez z sokiem cytrynowym
    177,  # Imbir z sokiem cytrynowym
    178,  # Imbir z sokiem cytrynowym
    199,  # Limonki
    203,  # Malina z sokiem cytrynowym
    206,  # Maliny z sokiem cytrynowym
    233,  # Pigwa
    235,  # Płatki róży
    266,  # Wiśnia z kardamonem
)
POWIDLA = (250,)  # Śliwka z orzechami i cynamonem

DESCRIPTIONS: dict[int, tuple[str, str]] = {
    141: (
        "Herbata Cytryna z imbirem. Rozgrzewająca, cytrusowa kompozycja do filiżanki.",
        "Konfitura cytrynowa z imbirem. Owocowy dodatek do herbaty, pieczywa i deserów.",
    ),
    142: (
        "Herbata Cytrynki z whisky. Aromatyzowana kompozycja o cytrusowej i lekko spirytusowej nucie.",
        "Cytrynki z whisky w słodkim syropie. Owocowy dodatek do napojów i deserów.",
    ),
    143: (
        "Herbata Cytrynki z żurawiną i cynamonem. Kwaskowo-korzenna kompozycja na chłodniejszy dzień.",
        "Cytrynki z żurawiną i cynamonem. Owocowy dodatek do herbaty, pieczywa i deserów.",
    ),
    144: (
        "Herbata Czarny bez z sokiem cytrynowym. Kwiatowo-cytrusowa kompozycja do filiżanki.",
        "Czarny bez z sokiem cytrynowym. Owocowy dodatek do herbaty, pieczywa i deserów.",
    ),
    177: (
        "Herbata Imbir z sokiem cytrynowym. Rozgrzewająca kompozycja na chłodniejszy dzień.",
        "Imbir z sokiem cytrynowym. Pasteryzowany dodatek do napojów i deserów.",
    ),
    178: (
        "Herbata Imbir z sokiem cytrynowym. Rozgrzewająca kompozycja do filiżanki.",
        "Imbir z sokiem cytrynowym. Pasteryzowany dodatek do napojów i deserów.",
    ),
    199: (
        "Herbata Limonki. Cytrusowa, orzeźwiająca kompozycja do filiżanki.",
        "Limonki w słodkim syropie. Owocowy dodatek do napojów i deserów.",
    ),
    203: (
        "Herbata Malina z sokiem cytrynowym. Owocowa, kwaskowa kompozycja do filiżanki.",
        "Maliny z sokiem cytrynowym. Owocowy dodatek do napojów i deserów.",
    ),
    206: (
        "Herbata Maliny z sokiem cytrynowym. Owocowo-cytrusowa kompozycja do filiżanki.",
        "Maliny z sokiem cytrynowym. Owocowy dodatek do napojów i deserów.",
    ),
    233: (
        "Herbata Pigwa. Owocowa kompozycja o aromacie pigwy.",
        "Pigwa w słodkim syropie. Owocowy dodatek do napojów i deserów.",
    ),
    235: (
        "Herbata Płatki Róży. Kwiatowa kompozycja do dzbanka albo filiżanki.",
        "Płatki róży w syropie. Owocowy dodatek do napojów i deserów.",
    ),
    250: (
        "Herbata Śliwka z orzechami i cynamonem. Owocowo-korzenna kompozycja na chłodniejszy dzień.",
        "Powidła śliwkowe z orzechami i cynamonem. Owocowy dodatek do herbaty, pieczywa i deserów.",
    ),
    266: (
        "Herbata Wiśnia z kardamonem. Owocowo-korzenna kompozycja do filiżanki.",
        "Konfitura wiśniowa z kardamonem. Owocowy dodatek do herbaty, pieczywa i deserów.",
    ),
}


async def _tea_ids(client) -> list[int]:
    rows = await client.execute_query_dict(
        """
        SELECT id FROM categories
        WHERE slug = 'herbata'
           OR parent_id = (SELECT id FROM categories WHERE slug = 'herbata')
           OR parent_id IN (
                SELECT id FROM categories WHERE parent_id = (SELECT id FROM categories WHERE slug = 'herbata')
           )
        """
    )
    return [row["id"] for row in rows]


async def _assign(client, item_ids: tuple[int, ...], leaf_slug: str, by_slug: dict[str, int]) -> None:
    if not item_ids:
        return
    await client.execute_query(
        "DELETE FROM item_categories WHERE item_id = ANY($1::int[]) AND category_id = ANY($2::int[])",
        [list(item_ids), await _tea_ids(client)],
    )
    await client.execute_query(
        """
        DELETE FROM item_attributes
        WHERE item_id = ANY($1::int[])
          AND attribute_id IN (SELECT id FROM attributes WHERE slug = 'aromatyzowana')
        """,
        [list(item_ids)],
    )
    for item_id in item_ids:
        await client.execute_query(
            """
            INSERT INTO item_categories (item_id, category_id, is_primary)
            VALUES ($1, $2, TRUE)
            ON CONFLICT (item_id, category_id) DO UPDATE SET is_primary = TRUE
            """,
            [item_id, by_slug["dodatki"]],
        )
        await client.execute_query(
            """
            INSERT INTO item_categories (item_id, category_id, is_primary)
            VALUES ($1, $2, FALSE)
            ON CONFLICT (item_id, category_id) DO NOTHING
            """,
            [item_id, by_slug[leaf_slug]],
        )


async def move_preserves(apps, schema_editor) -> None:
    client = schema_editor.client
    existing = await client.execute_query_dict("SELECT id FROM categories WHERE slug = 'konfitury'")
    if not existing:
        await client.execute_query(
            """
            UPDATE categories
            SET position = position + 1
            WHERE parent_id = (SELECT id FROM categories WHERE slug = 'rodzaj-dodatkow')
              AND position >= 2
            """
        )
        await client.execute_query(
            """
            INSERT INTO categories (name, slug, position, parent_id)
            SELECT 'Konfitury', 'konfitury', 2, id
            FROM categories WHERE slug = 'rodzaj-dodatkow'
            """
        )

    categories = await client.execute_query_dict("SELECT id, slug FROM categories")
    by_slug = {row["slug"]: row["id"] for row in categories}
    await _assign(client, KONFITURY, "konfitury", by_slug)
    await _assign(client, POWIDLA, "powidla", by_slug)

    for item_id, (_old, new) in DESCRIPTIONS.items():
        await client.execute_query(
            "UPDATE items SET description = $1 WHERE id = $2",
            [new, item_id],
        )


async def restore_preserves(apps, schema_editor) -> None:
    client = schema_editor.client
    item_ids = list(KONFITURY + POWIDLA)
    herbata = await client.execute_query_dict("SELECT id FROM categories WHERE slug = 'herbata'")
    if herbata:
        herbata_id = herbata[0]["id"]
        for item_id in item_ids:
            await client.execute_query(
                """
                INSERT INTO item_categories (item_id, category_id, is_primary)
                VALUES ($1, $2, TRUE)
                ON CONFLICT (item_id, category_id) DO UPDATE SET is_primary = TRUE
                """,
                [item_id, herbata_id],
            )
            await client.execute_query(
                """
                INSERT INTO item_attributes (item_id, attribute_id)
                SELECT $1, id FROM attributes WHERE slug = 'aromatyzowana'
                ON CONFLICT (item_id, attribute_id) DO NOTHING
                """,
                [item_id],
            )
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE item_id = ANY($1::int[])
          AND category_id IN (
                SELECT id FROM categories WHERE slug IN ('dodatki', 'konfitury', 'powidla')
          )
        """,
        [item_ids],
    )
    for item_id, (old, _new) in DESCRIPTIONS.items():
        await client.execute_query(
            "UPDATE items SET description = $1 WHERE id = $2",
            [old, item_id],
        )
    await client.execute_query("DELETE FROM categories WHERE slug = 'konfitury'")
    await client.execute_query(
        """
        UPDATE categories
        SET position = position - 1
        WHERE parent_id = (SELECT id FROM categories WHERE slug = 'rodzaj-dodatkow')
          AND position >= 3
        """
    )


class Migration(migrations.Migration):
    dependencies = [("models", "0007_customer_item_names")]
    initial = False
    operations = [
        ops.RunPython(move_preserves, restore_preserves),
    ]

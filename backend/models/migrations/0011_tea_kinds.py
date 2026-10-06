from tortoise import migrations
from tortoise.migrations import operations as ops

# Poprawione rodzaje. Nowe filtry: rooibos i owocowe.
MOVES = (
    (159, "czarne", "zielone"),  # Earl Grey Fantasy
    (192, "czarne", "zielone"),  # Korea Jeju
    (25, None, "rooibos"),  # After Winter
    (28, None, "owocowe"),  # Energia południa
    (120, None, "czarne"),  # African Queen
    (121, None, "pu-erh"),  # Aksamitny pocałunek
)
DESCRIPTIONS = {
    159: (
        "Earl Grey Fantasy. Aromatyzowana czarna herbata z bergamotką, w słodszej odsłonie.",
        "Earl Grey Fantasy. Zielona herbata z bergamotką, w słodszej odsłonie.",
    ),
    192: (
        "Czarna herbata Korea Jeju OP z wyspy Czedżu. Łagodny napar o własnym charakterze.",
        "Zielona herbata Korea Jeju z wyspy Czedżu. Łagodny napar o własnym charakterze.",
    ),
    25: (
        "Herbata After Winter. Rozgrzewająca kompozycja na chłodniejsze dni, do dzbanka albo filiżanki.",
        "Rooibos After Winter. Rozgrzewająca kompozycja na chłodniejsze dni, do dzbanka albo filiżanki.",
    ),
    28: (
        "Herbata Energia Południa. Kompozycja na popołudniową przerwę, do dzbanka albo filiżanki.",
        "Owocowa herbata Energia południa. Kompozycja na popołudniową przerwę, do dzbanka albo filiżanki.",
    ),
    120: (
        "Herbata African Queen. Aromatyzowana kompozycja do dzbanka albo filiżanki.",
        "African Queen. Aromatyzowana czarna herbata do dzbanka albo filiżanki.",
    ),
    121: (
        "Herbata Aksamitny Pocałunek. Łagodna, aromatyzowana kompozycja na spokojną filiżankę.",
        "Aksamitny pocałunek. Aromatyzowana herbata pu-erh na spokojną filiżankę.",
    ),
}


async def _set_kind(client, item_id: int, slug: str) -> None:
    await client.execute_query(
        """
        INSERT INTO item_categories (item_id, category_id, is_primary)
        SELECT $1, id, FALSE FROM categories WHERE slug = $2
        ON CONFLICT (item_id, category_id) DO NOTHING
        """,
        [item_id, slug],
    )


async def _clear_kind(client, item_id: int, slug: str) -> None:
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE item_id = $1
          AND category_id = (SELECT id FROM categories WHERE slug = $2)
        """,
        [item_id, slug],
    )


async def recategorize(apps, schema_editor) -> None:
    client = schema_editor.client
    existing = await client.execute_query_dict(
        "SELECT slug FROM categories WHERE slug IN ('rooibos', 'owocowe')"
    )
    have = {row["slug"] for row in existing}
    options = (("Rooibos", "rooibos", 7), ("Owocowe", "owocowe", 8))
    for name, slug, position in options:
        if slug in have:
            continue
        await client.execute_query(
            """
            INSERT INTO categories (name, slug, position, parent_id)
            SELECT $1, $2, $3, id
            FROM categories WHERE slug = 'rodzaj-herbaty'
            """,
            [name, slug, position],
        )
    for item_id, old_slug, new_slug in MOVES:
        if old_slug:
            await _clear_kind(client, item_id, old_slug)
        await _set_kind(client, item_id, new_slug)
        await client.execute_query(
            "UPDATE items SET description = $1 WHERE id = $2",
            [DESCRIPTIONS[item_id][1], item_id],
        )


async def restore(apps, schema_editor) -> None:
    client = schema_editor.client
    for item_id, old_slug, new_slug in MOVES:
        await _clear_kind(client, item_id, new_slug)
        if old_slug:
            await _set_kind(client, item_id, old_slug)
        await client.execute_query(
            "UPDATE items SET description = $1 WHERE id = $2",
            [DESCRIPTIONS[item_id][0], item_id],
        )
    await client.execute_query("DELETE FROM categories WHERE slug IN ('rooibos', 'owocowe')")


class Migration(migrations.Migration):
    dependencies = [("models", "0010_earl_grey_yellow")]
    initial = False
    operations = [
        ops.RunPython(recategorize, restore),
    ]

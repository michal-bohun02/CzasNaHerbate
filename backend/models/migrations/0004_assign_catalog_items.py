from tortoise import migrations
from tortoise.migrations import operations as ops


def _kind(name: str) -> str | None:
    if any(token in name for token in ("pu erh", "pu-erh", "puerh", "puehr")):
        return "pu-erh"
    if "oolong" in name or "da hong" in name:
        return "oolong"
    if any(
        token in name
        for token in (
            "earl",
            "assam",
            "ceylon",
            "darjeeling",
            "english breakfast",
            "lapsang",
            "kenya",
            "turecka",
            "yunnan black",
            "golden yunnan",
            "china golden",
            "nepal",
            "korea jeju",
            "chiyabari",
            "super black",
            "sencha black",
            "yun ming czarny",
        )
    ):
        return "czarne"
    if "yellow tea" in name or "yellow buds" in name or "sunon yellow" in name:
        return "zolte"
    if any(token in name for token in ("white", "silver needle", "pai mu", "biale", "białe")):
        return "biale"
    if any(
        token in name
        for token in (
            "sencha",
            "bancha",
            "gyokuro",
            "gunpowder",
            "bi luo",
            "gen mai",
            "tamaryokucha",
            "arashiyama",
            "jasmin",
            "green yunnan",
            "yun ming zielony",
        )
    ):
        return "zielone"
    return "aromatyzowane"


def _classify(name: str) -> tuple[str | None, list[str]]:
    if "zestaw" in name:
        return "zestawy-prezentowe", []

    if any(token in name for token in ("kubek", "filizank", "carmani")):
        leaves = ["filizanki-espresso"] if "espresso" in name or "filizank" in name else ["kubki"]
        if "650" in name:
            leaves.append("powyzej-400-ml")
        return "porcelana", leaves

    if any(
        token in name
        for token in (
            "matero",
            "bombilla",
            "frenchpress",
            "french press",
            "szczotecz",
            "skrzynka",
            "yerbomos",
            "diament",
        )
    ) or name.strip() == "liza":
        leaves: list[str] = []
        if "matero" in name or "diament" in name:
            leaves.append("matero")
        if "bombilla" in name or name.strip() == "liza":
            leaves.append("bombille")
        if "french" in name:
            leaves.append("french-press")
        if "skrzynka" in name:
            leaves.append("skrzynki-na-herbate")
        return "akcesoria", leaves

    if any(
        token in name
        for token in (
            "kombucha",
            "syrop",
            "matecznik",
            "konfitura",
            "mus malinowy",
            "maliny w syropie",
        )
    ) or name.startswith("miod"):
        return None, []

    if any(
        token in name
        for token in (
            "czekolada",
            "czekoladka",
            "w mlecznej",
            "w ciemnej",
            "w bialej",
            "w białej",
            "rzemieslnicza",
            "slonym karmelu",
            "goraca-czekolada",
            "goraca czekolada",
        )
    ) or name.startswith("ciemna z"):
        return None, []

    if "kawa" in name:
        return "kawa", []

    if any(
        token in name
        for token in (
            "yerba",
            "mate ",
            " mate",
            "wild-power",
            "wild power",
            "chillout",
            "opakow",
            "despalada",
            "deguarana",
            "very-berry",
            "very berry",
        )
    ) or name.strip() in {"iq", "mint", "argentina", "lemon", "fitness", "yoga", "canabis", "cannabis"}:
        return None, []

    return "herbata", [_kind(name)]


async def assign_catalog_items(apps, schema_editor) -> None:
    client = schema_editor.client
    items = await client.execute_query_dict("SELECT id, name FROM items ORDER BY id")
    categories = await client.execute_query_dict("SELECT id, slug FROM categories")
    by_slug = {row["slug"]: row["id"] for row in categories}

    for item in items:
        root, leaves = _classify(item["name"].lower())
        if root is None or root not in by_slug:
            continue
        await client.execute_query(
            """
            INSERT INTO item_categories (item_id, category_id, is_primary)
            VALUES ($1, $2, TRUE)
            ON CONFLICT (item_id, category_id) DO NOTHING
            """,
            [item["id"], by_slug[root]],
        )
        for leaf in leaves:
            if leaf not in by_slug:
                continue
            await client.execute_query(
                """
                INSERT INTO item_categories (item_id, category_id, is_primary)
                VALUES ($1, $2, FALSE)
                ON CONFLICT (item_id, category_id) DO NOTHING
                """,
                [item["id"], by_slug[leaf]],
            )


async def clear_catalog_items(apps, schema_editor) -> None:
    await schema_editor.client.execute_query("DELETE FROM item_categories")


class Migration(migrations.Migration):
    dependencies = [("models", "0003_category_filters")]
    initial = False
    operations = [
        ops.RunPython(assign_catalog_items, clear_catalog_items),
    ]

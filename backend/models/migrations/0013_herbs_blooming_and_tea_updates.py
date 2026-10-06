from tortoise import migrations
from tortoise.migrations import operations as ops

# Czarna, aromatyzowana.
BLACK = (
    122,  # Aleja gwiazd
    130,  # Casablanca
    138,  # Chwila przy kominku
    150,  # Czekoladowa laguna
    173,  # Hiszpańska mandarynka
    174,  # Ice tea brzoskwiniowa rumba
    175,  # Ice tea cytrynowa
    176,  # Ice tea Mango Twist
    179,  # Imię róży
    193,  # Książę Persji
    195,  # Kwiat granatu
    197,  # Lazy Day
    202,  # Madagaskar
    204,  # Malinowa
    205,  # Malinowa chmurka
    224,  # Ocean wspomnień
    228,  # Orange Dream
    229,  # Orientalna przygoda
    232,  # Pieczone jabłuszko
    234,  # Pikantna dynia
    236,  # Poezja smaku
    243,  # Pychotka
    251,  # Słodka pokusa
    252,  # Śniadanie u Tiffany'ego
    253,  # Spacer kochanków
    255,  # Sunrise
    258,  # Tropikalna pokusa
    259,  # Truskawki ze śmietaną
    265,  # Wiosenny spacer
    267,  # Wiśnie w rumie
    273,  # Złota gruszka
    274,  # Złote wspomnienie
    275,  # Zmysłowe mango
)
GREEN = (198,)  # Lemoniada rabarbarowa
WHITE = (208, 231, 257, 264)  # Mamma Mia, Pełnia szczęścia, Tajemnica Inków, Winogronowe Moscato
FRUIT = (230,)  # Owocowy zmierzch
BLOOMING = (194,)  # Kwiat miłości — jedyna kwitnąca kulka w katalogu
PURE_OOLONG = (212,)  # Milk Oolong
HERB = (128,)  # Blue Butterfly
CHOCOLATE = (244,)  # Ruby z żurawiną

KINDS = (
    (BLACK, "czarne", "Czarna herbata "),
    (GREEN, "zielone", "Zielona herbata "),
    (WHITE, "biale", "Biała herbata "),
    (FRUIT, "owocowe", "Owocowa herbata "),
)


async def _set_kind(client, item_ids: tuple[int, ...], slug: str) -> None:
    await client.execute_query(
        """
        INSERT INTO item_categories (item_id, category_id, is_primary)
        SELECT i.id, c.id, FALSE
        FROM items i
        JOIN categories c ON c.slug = $2
        WHERE i.id = ANY($1::int[])
        ON CONFLICT (item_id, category_id) DO NOTHING
        """,
        [list(item_ids), slug],
    )


async def _drop_attr(client, item_ids: tuple[int, ...], slug: str) -> None:
    await client.execute_query(
        """
        DELETE FROM item_attributes
        WHERE item_id = ANY($1::int[])
          AND attribute_id = (SELECT id FROM attributes WHERE slug = $2)
        """,
        [list(item_ids), slug],
    )


async def _add_attr(client, item_ids: tuple[int, ...], slug: str) -> None:
    await client.execute_query(
        """
        INSERT INTO item_attributes (item_id, attribute_id, value_text, value_num)
        SELECT i.id, a.id, NULL, NULL
        FROM items i
        JOIN attributes a ON a.slug = $2
        WHERE i.id = ANY($1::int[])
        ON CONFLICT (item_id, attribute_id) DO NOTHING
        """,
        [list(item_ids), slug],
    )


async def _leave_tea(client, item_ids: tuple[int, ...]) -> None:
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE item_id = ANY($1::int[])
          AND category_id IN (
              SELECT id FROM categories
              WHERE slug = 'herbata'
                 OR parent_id = (SELECT id FROM categories WHERE slug = 'rodzaj-herbaty')
                 OR parent_id IN (
                     SELECT id FROM categories WHERE parent_id = (SELECT id FROM categories WHERE slug = 'herbata')
                 )
          )
        """,
        [list(item_ids)],
    )
    await _drop_attr(client, item_ids, "aromatyzowana")
    await _drop_attr(client, item_ids, "czyste")
    await _drop_attr(client, item_ids, "kwitnace")


async def apply(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        INSERT INTO categories (name, slug, position, parent_id)
        VALUES ('Zioła', 'ziola', 6, NULL)
        ON CONFLICT (slug) DO NOTHING
        """
    )
    await client.execute_query(
        """
        INSERT INTO categories (name, slug, position, parent_id)
        SELECT 'Rodzaj', 'rodzaj-ziol', 0, id
        FROM categories WHERE slug = 'ziola'
        ON CONFLICT (slug) DO NOTHING
        """
    )
    options = (
        ("Zioła", "ziolowe", 0),
        ("Zioła korzenne", "ziola-korzenne", 1),
        ("Yerba", "yerba", 2),
    )
    for name, slug, position in options:
        await client.execute_query(
            """
            INSERT INTO categories (name, slug, position, parent_id)
            SELECT $1, $2, $3, id
            FROM categories WHERE slug = 'rodzaj-ziol'
            ON CONFLICT (slug) DO NOTHING
            """,
            [name, slug, position],
        )
    await client.execute_query(
        """
        INSERT INTO attributes (name, slug, type, unit, position, category_id)
        SELECT 'Kwitnące', 'kwitnace', 'bool', NULL, 2, id
        FROM categories WHERE slug = 'herbata'
        ON CONFLICT (slug) DO UPDATE
        SET name = EXCLUDED.name,
            type = EXCLUDED.type,
            position = EXCLUDED.position,
            category_id = EXCLUDED.category_id
        """
    )

    for item_ids, slug, prefix in KINDS:
        await _set_kind(client, item_ids, slug)
        await client.execute_query(
            """
            UPDATE items
            SET description = regexp_replace(description, '^Herbata ', $2)
            WHERE id = ANY($1::int[])
              AND description LIKE 'Herbata %'
            """,
            [list(item_ids), prefix],
        )

    await _set_kind(client, BLOOMING, "zielone")
    await _drop_attr(client, BLOOMING, "aromatyzowana")
    await _drop_attr(client, BLOOMING, "czyste")
    await _add_attr(client, BLOOMING, "kwitnace")
    await client.execute_query(
        "UPDATE items SET description = $1 WHERE id = 194",
        ["Kwiat miłości. Zielona herbata kwitnąca, wiązana w kulkę."],
    )

    await _drop_attr(client, PURE_OOLONG, "aromatyzowana")
    await _add_attr(client, PURE_OOLONG, "czyste")
    await client.execute_query(
        "UPDATE items SET description = $1 WHERE id = 212",
        ["Milk Oolong. Czysty oolong o kremowej, mlecznej nucie."],
    )

    await _leave_tea(client, HERB)
    await _set_kind(client, HERB, "ziola")
    await client.execute_query(
        """
        UPDATE item_categories SET is_primary = TRUE
        WHERE item_id = ANY($1::int[])
          AND category_id = (SELECT id FROM categories WHERE slug = 'ziola')
        """,
        [list(HERB)],
    )
    await _set_kind(client, HERB, "ziolowe")
    await client.execute_query(
        "UPDATE items SET description = $1 WHERE id = 128",
        ["Blue Butterfly. Zioła z kwiatów klitorii na niebieski napar."],
    )

    await _leave_tea(client, CHOCOLATE)
    await _set_kind(client, CHOCOLATE, "dodatki")
    await client.execute_query(
        """
        UPDATE item_categories SET is_primary = TRUE
        WHERE item_id = ANY($1::int[])
          AND category_id = (SELECT id FROM categories WHERE slug = 'dodatki')
        """,
        [list(CHOCOLATE)],
    )
    await _set_kind(client, CHOCOLATE, "czekolady")
    await client.execute_query(
        "UPDATE items SET description = $1 WHERE id = 244",
        ["Czekolada Ruby z żurawiną."],
    )

    await client.execute_query(
        """
        INSERT INTO item_categories (item_id, category_id, is_primary)
        SELECT i.id, c.id, c.slug = 'ziola'
        FROM items i
        JOIN categories c ON c.slug IN ('ziola', 'yerba')
        WHERE i.name ILIKE 'yerba%'
        ON CONFLICT (item_id, category_id) DO NOTHING
        """
    )


async def revert(apps, schema_editor) -> None:
    client = schema_editor.client
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE item_id IN (SELECT id FROM items WHERE name ILIKE 'yerba%')
          AND category_id IN (SELECT id FROM categories WHERE slug IN ('ziola', 'yerba'))
        """
    )
    await client.execute_query(
        """
        DELETE FROM item_categories
        WHERE item_id = ANY($1::int[])
          AND category_id IN (SELECT id FROM categories WHERE slug IN ('ziola', 'ziolowe', 'dodatki', 'czekolady'))
        """,
        [list(HERB + CHOCOLATE)],
    )
    await client.execute_query(
        """
        INSERT INTO item_categories (item_id, category_id, is_primary)
        SELECT i.id, c.id, TRUE
        FROM items i
        JOIN categories c ON c.slug = 'herbata'
        WHERE i.id = ANY($1::int[])
        ON CONFLICT (item_id, category_id) DO NOTHING
        """,
        [list(HERB + CHOCOLATE + BLOOMING)],
    )
    await _add_attr(client, HERB + CHOCOLATE + BLOOMING + PURE_OOLONG, "aromatyzowana")
    await _drop_attr(client, PURE_OOLONG, "czyste")
    await _drop_attr(client, BLOOMING, "kwitnace")
    for item_ids, slug, _prefix in KINDS:
        await client.execute_query(
            """
            DELETE FROM item_categories
            WHERE item_id = ANY($1::int[])
              AND category_id = (SELECT id FROM categories WHERE slug = $2)
            """,
            [list(item_ids), slug],
        )
        await client.execute_query(
            """
            UPDATE items
            SET description = regexp_replace(description, $2, 'Herbata ')
            WHERE id = ANY($1::int[])
            """,
            [list(item_ids), "^" + _prefix.replace(" ", " ")],
        )
    await client.execute_query(
        "DELETE FROM item_categories WHERE item_id = 194 AND category_id = (SELECT id FROM categories WHERE slug = 'zielone')"
    )
    await client.execute_query(
        "UPDATE items SET description = $1 WHERE id = 194",
        ["Herbata Kwiat Miłości. Kwiatowa, aromatyzowana kompozycja na spokojną filiżankę."],
    )
    await client.execute_query(
        "UPDATE items SET description = $1 WHERE id = 212",
        ["Oolong mleczny Milk Oolong. Kremowy, gładki napar o mlecznej nucie."],
    )
    await client.execute_query(
        "UPDATE items SET description = $1 WHERE id = 128",
        ["Herbata Blue Butterfly. Aromatyzowana kompozycja do dzbanka albo filiżanki."],
    )
    await client.execute_query(
        "UPDATE items SET description = $1 WHERE id = 244",
        ["Herbata Ruby z żurawiną. Owocowa kompozycja o kwaskowatej nucie."],
    )
    await client.execute_query("DELETE FROM attributes WHERE slug = 'kwitnace'")
    await client.execute_query(
        "DELETE FROM categories WHERE slug IN ('ziolowe', 'ziola-korzenne', 'yerba', 'rodzaj-ziol', 'ziola')"
    )


class Migration(migrations.Migration):
    dependencies = [("models", "0012_pure_attribute")]
    initial = False
    operations = [
        ops.RunPython(apply, revert),
    ]

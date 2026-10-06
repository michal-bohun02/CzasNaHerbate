from tortoise import migrations
from tortoise.migrations import operations as ops


def _q(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _statements() -> tuple[list[str], list[str]]:
    roots = [
        ("Herbata", "herbata", 0, [
            ("Rodzaj herbaty", "rodzaj-herbaty", [
                ("Zielone", "zielone"),
                ("Czarne", "czarne"),
                ("Oolong", "oolong"),
                ("Białe", "biale"),
                ("Matcha", "matcha"),
                ("Pu-erh", "pu-erh"),
                ("Żółte", "zolte"),
                ("Aromatyzowane", "aromatyzowane"),
            ]),
            ("Zawartość kofeiny", "zawartosc-kofeiny", [
                ("Bez kofeiny", "bez-kofeiny"),
                ("Niska", "kofeina-niska"),
                ("Średnia", "kofeina-srednia"),
                ("Wysoka", "kofeina-wysoka"),
            ]),
            ("Pochodzenie", "pochodzenie-herbaty", [
                ("Chiny", "chiny"),
                ("Japonia", "japonia"),
                ("Indie", "indie"),
                ("Cejlon", "cejlon"),
                ("Afryka", "afryka"),
            ]),
        ]),
        ("Kawa", "kawa", 1, [
            ("Rodzaj kawy", "rodzaj-kawy", [
                ("Ziarnista", "ziarnista"),
                ("Mielona", "mielona"),
                ("Bezkofeinowa", "bezkofeinowa"),
            ]),
            ("Stopień palenia", "stopien-palenia", [
                ("Jasne", "palenie-jasne"),
                ("Średnie", "palenie-srednie"),
                ("Ciemne", "palenie-ciemne"),
            ]),
            ("Pochodzenie", "pochodzenie-kawy", [
                ("Afryka", "kawa-afryka"),
                ("Ameryka Południowa", "kawa-ameryka-poludniowa"),
                ("Ameryka Środkowa", "kawa-ameryka-srodkowa"),
                ("Azja", "kawa-azja"),
            ]),
        ]),
        ("Porcelana", "porcelana", 2, [
            ("Rodzaj", "rodzaj-porcelany", [
                ("Kubki", "kubki"),
                ("Filiżanki espresso", "filizanki-espresso"),
                ("Zestawy", "zestawy-porcelany"),
                ("Dzbanki", "dzbanki"),
            ]),
            ("Pojemność", "pojemnosc", [
                ("Do 200 ml", "do-200-ml"),
                ("200–400 ml", "200-400-ml"),
                ("Powyżej 400 ml", "powyzej-400-ml"),
            ]),
        ]),
        ("Akcesoria", "akcesoria", 3, [
            ("Rodzaj", "rodzaj-akcesoriow", [
                ("Matero", "matero"),
                ("Bombille", "bombille"),
                ("French press", "french-press"),
                ("Zaparzacze", "zaparzacze"),
                ("Skrzynki na herbatę", "skrzynki-na-herbate"),
            ]),
            ("Przeznaczenie", "przeznaczenie", [
                ("Herbata", "do-herbaty"),
                ("Kawa", "do-kawy"),
                ("Yerba mate", "do-yerba-mate"),
            ]),
        ]),
        ("Zestawy prezentowe", "zestawy-prezentowe", 4, [
            ("Zawartość", "zawartosc-zestawu", [
                ("Herbata", "zestaw-herbata"),
                ("Kawa", "zestaw-kawa"),
                ("Yerba mate", "zestaw-yerba"),
                ("Porcelana", "zestaw-porcelana"),
            ]),
            ("Okazja", "okazja", [
                ("Na start", "na-start"),
                ("Na prezent", "na-prezent"),
                ("Świąteczny", "swiateczny"),
            ]),
        ]),
    ]

    forward: list[str] = []
    leaves: list[str] = []
    groups: list[str] = []
    root_slugs: list[str] = []

    for name, slug, position, children in roots:
        root_slugs.append(slug)
        forward.append(
            "INSERT INTO categories (name, slug, position, parent_id) "
            f"VALUES ({_q(name)}, {_q(slug)}, {position}, NULL) "
            "ON CONFLICT (slug) DO NOTHING"
        )
        for group_position, (group_name, group_slug, options) in enumerate(children):
            groups.append(group_slug)
            forward.append(
                "INSERT INTO categories (name, slug, position, parent_id) "
                f"SELECT {_q(group_name)}, {_q(group_slug)}, {group_position}, id "
                f"FROM categories WHERE slug = {_q(slug)} "
                "ON CONFLICT (slug) DO NOTHING"
            )
            for option_position, (option_name, option_slug) in enumerate(options):
                leaves.append(option_slug)
                forward.append(
                    "INSERT INTO categories (name, slug, position, parent_id) "
                    f"SELECT {_q(option_name)}, {_q(option_slug)}, {option_position}, id "
                    f"FROM categories WHERE slug = {_q(group_slug)} "
                    "ON CONFLICT (slug) DO NOTHING"
                )

    def delete(slugs: list[str]) -> str:
        joined = ", ".join(_q(slug) for slug in slugs)
        return f"DELETE FROM categories WHERE slug IN ({joined})"

    reverse = [delete(leaves), delete(groups), delete(root_slugs)]
    return forward, reverse


_FORWARD, _REVERSE = _statements()


class Migration(migrations.Migration):
    dependencies = [("models", "0002_catalog_schema")]
    initial = False
    operations = [
        ops.RunSQL(_FORWARD, _REVERSE),
    ]

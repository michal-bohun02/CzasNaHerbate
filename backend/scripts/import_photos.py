#!/usr/bin/env python3
"""
Hurtowy import referencji zdjęć z MinIO do tabeli item_photos.

Klucze obiektów są najpierw normalizowane: polskie znaki schodzą do ASCII
(ą -> a, ę -> e, ...), a spacje zamieniają się na _. Jeśli klucz się zmienia,
obiekt w MinIO jest kopiowany na nową nazwę, a stary usuwany. Wiersze już
zapisane w bazie dostają zaktualizowany storage_key.

Instalacja (w venv backendu):
    pip install boto3

Użycie (z katalogu backend):
    python scripts/import_photos.py --dry-run
    python scripts/import_photos.py
    python scripts/import_photos.py --mapping mapping.csv
ID rzeczy jest liczbą na początku nazwy pliku, na przykład 1040-matero-stal-czarne.jpg albo 1191.jpg.
Plik CSV, gdy nazwa nie zaczyna się od ID (kolejność wierszy = kolejność w galerii):
    storage_key,item_id
    3f8a1c2e.jpg,5

Skrypt można puszczać wielokrotnie: zdjęcia już obecne w tabeli są pomijane,
a nowe dostają kolejne numery position. Pierwsze zdjęcie rzeczy bez is_main
dostaje is_main = true.
"""
import argparse
import asyncio
import csv
import os
import re
from collections import defaultdict
from pathlib import Path

import asyncpg
import boto3
from botocore.config import Config

ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"

POLISH = str.maketrans(
    {
        "ą": "a",
        "ć": "c",
        "ę": "e",
        "ł": "l",
        "ń": "n",
        "ó": "o",
        "ś": "s",
        "ź": "z",
        "ż": "z",
        "Ą": "A",
        "Ć": "C",
        "Ę": "E",
        "Ł": "L",
        "Ń": "N",
        "Ó": "O",
        "Ś": "S",
        "Ź": "Z",
        "Ż": "Z",
    }
)

IMAGE_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".avif": "image/avif",
}

DEFAULT_PREFIX = ""
ITEM_ID_PATTERN = re.compile(r"(?:^|/)(\d+)(?=[-_.])")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def s3_endpoint() -> str:
    public = env("S3_ENDPOINT", "MINIO_PUBLIC_URL")
    if public:
        return public if "://" in public else f"http://{public}"
    host = env("MINIO_ENDPOINT", default="localhost:9000")
    return host if "://" in host else f"http://{host}"


def normalize_key(key: str) -> str:
    parts = []
    for segment in key.split("/"):
        segment = segment.translate(POLISH)
        segment = re.sub(r"\s+", "_", segment)
        segment = re.sub(r"_+", "_", segment).strip("_")
        parts.append(segment)
    return "/".join(parts)


def content_type_for(key: str) -> str | None:
    return IMAGE_EXT.get(Path(key).suffix.lower())


def list_keys(s3, bucket: str, prefix: str):
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/") or content_type_for(key) is None:
                continue
            yield key


def load_mapping(path: str) -> list[tuple[str, int]]:
    with open(path, newline="", encoding="utf-8") as handle:
        return [
            (normalize_key(row["storage_key"].strip()), int(row["item_id"]))
            for row in csv.DictReader(handle)
        ]


def allocate_name(candidate: str, taken: set[str]) -> str:
    if candidate not in taken:
        return candidate
    folder, _, name = candidate.rpartition("/")
    stem, dot, ext = name.rpartition(".")
    if not dot:
        stem, ext = name, ""
    number = 2
    while True:
        filename = f"{stem}_{number}.{ext}" if ext else f"{stem}_{number}"
        renamed = f"{folder}/{filename}" if folder else filename
        if renamed not in taken:
            return renamed
        number += 1


def leading_id(key: str) -> int | None:
    name = key.rsplit("/", 1)[-1]
    match = re.match(r"(\d+)(?=[-_.])", name)
    return int(match.group(1)) if match else None


def prefix_new_id(key: str, new_id: int) -> str:
    folder, _, name = key.rpartition("/")
    renamed = f"{new_id}-{name}"
    return f"{folder}/{renamed}" if folder else renamed


def with_new_id(key: str, new_id: int) -> str:
    folder, _, name = key.rpartition("/")
    renamed = re.sub(r"^\d+(?=[-_.])", str(new_id), name, count=1)
    return f"{folder}/{renamed}" if folder else renamed


def item_name(keys: list[str]) -> str:
    stems = []
    for key in keys:
        stem = Path(key).stem
        stem = re.sub(r"^\d+[-_]", "", stem)
        stem = re.sub(
            r"[-_](?:detal|opakowanie|szczegol|maly|\d+)$",
            "",
            stem,
            flags=re.IGNORECASE,
        )
        stem = stem.replace("_", " ").strip()
        if stem:
            stems.append(stem)
    if not stems:
        return "item"
    return max(set(stems), key=stems.count)[:255]


def plan_renames(keys: list[str]) -> tuple[list[tuple[str, str]], dict[str, str], dict[int, int]]:
    """Normalizuje nazwy i nadaje kolejne item_id od 1.

    Zdjęcia z tym samym starym numerem dostają ten sam nowy numer.
    """
    taken = set(keys)
    normalized: dict[str, str] = {}
    for key in keys:
        renamed = allocate_name(normalize_key(key), taken - {key})
        taken.discard(key)
        taken.add(renamed)
        normalized[key] = renamed

    variant = re.compile(r"(?:[-_](?:detal|opakowanie|szczegol|maly|\d+))$", re.IGNORECASE)
    unnumbered: dict[str, list[str]] = defaultdict(list)
    for original, norm in normalized.items():
        if leading_id(norm) is None:
            stem = variant.sub("", Path(norm).stem).lower()
            unnumbered[stem].append(original)
    next_id = max((leading_id(key) for key in normalized.values() if leading_id(key) is not None), default=0) + 1
    for stem in sorted(unnumbered):
        for original in unnumbered[stem]:
            normalized[original] = prefix_new_id(normalized[original], next_id)
        next_id += 1

    old_ids = sorted({item_id for item_id in (leading_id(key) for key in normalized.values()) if item_id is not None})
    id_map = {old: new for new, old in enumerate(old_ids, start=1)}

    taken = set(normalized.values())
    final: dict[str, str] = {}
    renames = []
    for key, norm in normalized.items():
        old = leading_id(norm)
        target = with_new_id(norm, id_map[old]) if old is not None else norm
        target = allocate_name(target, taken - {norm})
        taken.discard(norm)
        taken.add(target)
        final[key] = target
        if target != key:
            renames.append((key, target))
    return renames, final, id_map


def apply_renames(s3, bucket: str, renames: list[tuple[str, str]]) -> None:
    for old, new in renames:
        s3.copy_object(Bucket=bucket, Key=new, CopySource={"Bucket": bucket, "Key": old})
        s3.delete_object(Bucket=bucket, Key=old)


async def main() -> None:
    load_env_file(ROOT_ENV)

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="nic nie zapisuj, tylko pokaż podsumowanie")
    parser.add_argument("--mapping", help="CSV z kolumnami storage_key,item_id")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    parser.add_argument(
        "--pattern",
        default=ITEM_ID_PATTERN.pattern,
        help="regex z jedną grupą = item_id, dopasowywany do klucza",
    )
    args = parser.parse_args()
    pattern = re.compile(args.pattern)

    bucket = env("S3_BUCKET", "MINIO_BUCKET", default="zdjecia-czas-na-herbate")
    s3 = boto3.client(
        "s3",
        endpoint_url=s3_endpoint(),
        aws_access_key_id=env("S3_ACCESS_KEY", "MINIO_ACCESS_KEY", default="minioadmin"),
        aws_secret_access_key=env("S3_SECRET_KEY", "MINIO_SECRET_KEY"),
        region_name=env("S3_REGION", default="us-east-1"),
        config=Config(s3={"addressing_style": "path"}),
    )

    s3_keys = sorted(list_keys(s3, bucket, args.prefix))
    print(f"Zdjęć w MinIO pod '{args.prefix or '/'}': {len(s3_keys)}")

    renames, final_by_original, id_map = plan_renames(s3_keys)
    print(f"Starych numerów: {len(id_map)} -> nowe ID 1..{len(id_map)}")
    if renames:
        print(f"Do zmiany nazwy w MinIO: {len(renames)}")
        for old, new in renames[:10]:
            print(f"  {old} -> {new}")

    grouped: dict[int, list[str]] = defaultdict(list)
    problems: dict[str, list[str]] = defaultdict(list)

    if args.mapping:
        in_s3 = set(final_by_original.values())
        for key, item_id in load_mapping(args.mapping):
            if key in in_s3:
                grouped[item_id].append(key)
            else:
                problems["w CSV, ale brak pliku w MinIO"].append(key)
    else:
        for key in final_by_original.values():
            match = pattern.search(key)
            if match:
                grouped[int(match.group(1))].append(key)
            else:
                problems["nie da się odczytać item_id z klucza"].append(key)

    database_url = env("DATABASE_URL")
    if not database_url:
        raise SystemExit("Brak DATABASE_URL w środowisku albo w .env")
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url.removeprefix("postgres://")

    conn = await asyncpg.connect(database_url)
    try:
        item_ids = {row["id"] for row in await conn.fetch("SELECT id FROM items")}
        already = {row["storage_key"] for row in await conn.fetch("SELECT storage_key FROM item_photos")}
        max_pos = {
            row["item_id"]: row["max_position"]
            for row in await conn.fetch(
                "SELECT item_id, MAX(position) AS max_position FROM item_photos GROUP BY item_id"
            )
        }

        key_updates = []
        for old, new in renames:
            if old not in already:
                continue
            if new in already:
                problems["nowy klucz jest już w item_photos"].append(f"{old} -> {new}")
                continue
            key_updates.append((new, old))
            already.remove(old)
            already.add(new)

        new_items = []
        for item_id, keys in sorted(grouped.items()):
            if item_id in item_ids:
                continue
            new_items.append((item_id, item_name(keys)))

        rows = []
        skipped_existing = 0
        for item_id, keys in grouped.items():
            if item_id not in item_ids and item_id not in {row[0] for row in new_items}:
                problems[f"brak rzeczy o id={item_id} w tabeli items"].extend(keys)
                continue
            position = max_pos.get(item_id, -1) + 1
            for key in keys:
                if key in already:
                    skipped_existing += 1
                    continue
                if content_type_for(key) is None:
                    problems["nieobsługiwane rozszerzenie"].append(key)
                    continue
                rows.append((item_id, key, position))
                position += 1

        print(
            f"Nowe rzeczy: {len(new_items)} | do dodania zdjęć: {len(rows)} | "
            f"już w bazie: {skipped_existing} | aktualizacje kluczy: {len(key_updates)}"
        )
        for reason, keys in problems.items():
            print(f"Pominięte ({reason}): {len(keys)}, np. {keys[:3]}")

        if args.dry_run:
            print("\n[DRY RUN] Przykładowe wiersze:")
            for row in rows[:10]:
                print(
                    "  item_id=%s  position=%s  %s" % (row[0], row[2], row[1])
                )
            return

        if renames:
            apply_renames(s3, bucket, renames)

        async with conn.transaction():
            if new_items:
                await conn.executemany(
                    "INSERT INTO items (id, name, slug, created_at) VALUES ($1, $2, $2, NOW())",
                    new_items,
                )
                await conn.execute(
                    "SELECT setval('items_id_seq', (SELECT MAX(id) FROM items))"
                )
            if key_updates:
                await conn.executemany(
                    "UPDATE item_photos SET storage_key = $1 WHERE storage_key = $2",
                    key_updates,
                )
            if rows:
                await conn.executemany(
                    """
                    INSERT INTO item_photos (item_id, storage_key, position)
                    VALUES ($1, $2, $3)
                    """,
                    rows,
                )
        print(
            f"Gotowe, dodano {len(new_items)} rzeczy i {len(rows)} zdjęć, "
            f"zaktualizowano {len(key_updates)} kluczy."
        )
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())

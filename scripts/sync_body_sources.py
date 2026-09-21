"""Синхронизирует раздел «## Источники» в тексте карточек с полем sources.

Запуск из корня проекта:
    python scripts/sync_body_sources.py [--dry-run]

Источником истины является YAML-поле sources. Раздел «## Источники» в
Markdown-теле перезаписывается нумерованным списком из этого поля; если
раздела нет, он добавляется в конец карточки. Валидатор выдаёт
предупреждение BODY_SOURCES_MISMATCH, если раздел расходится с полем.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.card_writer import read_card, sync_body_sources, write_card  # noqa: E402
from src.schema import load_schema  # noqa: E402

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kb", default=str(ROOT / "kb"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    kb = Path(args.kb)
    schema = load_schema(kb / "_schema" / "schema.yaml")
    changed = 0
    for path in sorted(kb.rglob("*.md")):
        rel = path.relative_to(kb)
        if path.name in {"index.md", "README.md"} or rel.parts[0] in {"templates", "_schema", "rules"}:
            continue
        doc = read_card(path)
        if not doc.meta.get("id"):
            continue
        new_body = sync_body_sources(doc.body, list(doc.meta.get("sources") or []))
        if new_body != doc.body:
            changed += 1
            if not args.dry_run:
                doc.body = new_body
                write_card(doc, schema)
    print(f"Обновлено разделов «Источники»: {changed}{' (сухой прогон)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

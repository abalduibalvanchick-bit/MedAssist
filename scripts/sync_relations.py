"""Добавляет в relations связи, подразумеваемые машиночитаемым слоем.

Запуск из корня проекта:
    python scripts/sync_relations.py [--dry-run]

Для каждой ссылки машиночитаемого слоя, у поля которой в схеме указан атрибут
implies, проверяется, есть ли в графе связь между карточками (любого типа, в
любом направлении). Если связи нет и подразумеваемый тип допустим для
категорий карточек, связь добавляется с пометкой об источнике.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.card_writer import read_card, write_card  # noqa: E402
from src.machine_refs import iter_machine_refs  # noqa: E402
from src.repository import KnowledgeRepository  # noqa: E402
from src.schema import load_schema  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kb", default=str(ROOT / "kb"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    kb = Path(args.kb)
    schema = load_schema(kb / "_schema" / "schema.yaml")
    repo = KnowledgeRepository(kb).load()
    categories = {c.id: c.category for c in repo.cards}
    linked = {frozenset((c.id, str(r.get("target", "")).strip())) for c in repo.cards for r in c.relations}
    added = 0
    for card in repo.cards:
        if card.schema_version < 2:
            continue
        new = []
        for ref in iter_machine_refs(card.metadata, schema, card.category):
            pair = frozenset((card.id, ref.target))
            if not ref.implies or ref.target not in categories or ref.target == card.id or pair in linked:
                continue
            info = schema.relation_types.get(ref.implies)
            tgt_cat = categories[ref.target]
            if info is None or (info.from_categories and card.category not in info.from_categories) \
                    or (info.to_categories and tgt_cat not in info.to_categories):
                print(f"! {card.id}: {ref.path} -> {ref.target}: тип {ref.implies} недопустим для {card.category}->{tgt_cat}")
                continue
            new.append({"target": ref.target, "type": ref.implies,
                        "description": f"выведено из машиночитаемого слоя ({ref.path.split('[')[0].split('.')[0]})"})
            linked.add(pair)
        if new:
            added += len(new)
            print(f"~ {card.id}: +{len(new)} связей")
            if not args.dry_run:
                doc = read_card(card.file_path)
                doc.meta["relations"] = list(doc.meta.get("relations") or []) + new
                write_card(doc, schema)
    print(f"Добавлено связей: {added}{' (сухой прогон)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

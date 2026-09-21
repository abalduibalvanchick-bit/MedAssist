"""Применяет патчи наполнения к карточкам базы знаний.

Запуск из корня проекта:
    python scripts/apply_patch.py patch.yaml [patch2.yaml ...] [--dry-run] [--date YYYY-MM-DD]

Формат патча — YAML-словарь «ID карточки -> операции»:

    DIAG-SYMPTOM-002:
      set:                      # установить/заменить поля YAML
        synonyms: [загрудинная боль]
        features:
          - {code: chest_pain.pressing, label: давящая}
      unset: [old_field]        # удалить поля
      add_relations:            # добавить связи (дубликаты target+type пропускаются)
        - {target: DIAG-DISEASE-002, type: symptom_of, description: ...}
      remove_relations:         # удалить связи по target (и type, если указан)
        - {target: DIAG-EXAM-004}
      add_sources: [...]        # добавить источники (без дубликатов)
      remove_sources: [...]     # удалить источники по точному совпадению
      body: |                   # заменить Markdown-тело целиком
        # ...
      status: approved

    GLB-PROFILE-001:            # создание новой карточки
      create:
        file: glb_profile_elderly.md
      set: {...все поля метаданных...}
      body: |
        # ...

Патч — рабочий инструмент наполнения: после применения источником истины
остаются сами карточки, патч в репозитории не хранится.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.card_writer import CardDocument, read_card, write_card  # noqa: E402
from src.schema import load_schema  # noqa: E402

KB = ROOT / "kb"


def index_cards(kb: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in kb.rglob("*.md"):
        rel = path.relative_to(kb)
        if path.name in {"index.md", "README.md"} or rel.parts[0] in {"templates", "_schema", "rules"}:
            continue
        doc = read_card(path)
        if doc.meta.get("id"):
            result[str(doc.meta["id"])] = path
    return result


def bump_minor(version: Any) -> str:
    try:
        major, minor = (str(version).split(".") + ["0"])[:2]
        return f"{int(major)}.{int(minor) + 1}"
    except ValueError:
        return "2.1"


def apply(patch: dict[str, Any], kb: Path, date: str, dry_run: bool) -> list[str]:
    schema = load_schema(kb / "_schema" / "schema.yaml")
    paths = index_cards(kb)
    log: list[str] = []
    for card_id, ops in patch.items():
        if card_id.startswith("_"):
            continue  # служебные ключи (якоря YAML с общими значениями)
        ops = ops or {}
        if "create" in ops and card_id in paths:
            ops = {k: v for k, v in ops.items() if k != "create"}  # повторное применение = обновление
        if "create" in ops:
            meta = dict(ops.get("set") or {})
            meta["id"] = card_id
            category = meta.get("category")
            domain = meta.get("domain")
            if category not in schema.categories or domain not in schema.domains:
                raise SystemExit(f"{card_id}: для создания нужны корректные domain и category")
            folder = kb / schema.domains[domain]["folder"] / schema.categories[category].folder
            path = folder / ops["create"]["file"]
            body = ops.get("body", "")
            doc = CardDocument(path=path, meta=meta, body="\n" + body.lstrip("\n"))
            log.append(f"+ {card_id}: создана {path.relative_to(kb)}")
            if not dry_run:
                write_card(doc, schema)
            continue

        if card_id not in paths:
            raise SystemExit(f"{card_id}: карточка не найдена")
        doc = read_card(paths[card_id])
        meta = doc.meta
        changed: list[str] = []
        content_changed = False
        for key, value in (ops.get("set") or {}).items():
            if meta.get(key) != value:
                meta[key] = value
                changed.append(f"set {key}")
                content_changed = True
        for key in ops.get("unset") or []:
            if key in meta:
                meta.pop(key)
                changed.append(f"unset {key}")
                content_changed = True
        relations = list(meta.get("relations") or [])
        for spec in ops.get("remove_relations") or []:
            before = len(relations)
            relations = [r for r in relations if not (r.get("target") == spec["target"] and (not spec.get("type") or r.get("type") == spec["type"]))]
            if len(relations) != before:
                changed.append(f"-rel {spec['target']}")
                content_changed = True
        existing = {(r.get("target"), r.get("type")) for r in relations}
        for rel in ops.get("add_relations") or []:
            key = (rel["target"], rel["type"])
            if key not in existing:
                relations.append({k: rel[k] for k in ("target", "type", "description") if k in rel})
                existing.add(key)
                changed.append(f"+rel {rel['type']}->{rel['target']}")
                content_changed = True
        meta["relations"] = relations
        sources = list(meta.get("sources") or [])
        for src in ops.get("remove_sources") or []:
            if src in sources:
                sources.remove(src)
                changed.append("-source")
                content_changed = True
        for src in ops.get("add_sources") or []:
            if src not in sources:
                sources.append(src)
                changed.append("+source")
                content_changed = True
        meta["sources"] = sources
        if "body" in ops:
            new_body = "\n" + ops["body"].lstrip("\n")
            if new_body != doc.body:
                doc.body = new_body
                changed.append("body")
                content_changed = True
        if "status" in ops and meta.get("status") != ops["status"]:
            meta["status"] = ops["status"]
            changed.append(f"status={ops['status']}")
        if content_changed:
            meta["version"] = bump_minor(meta.get("version"))
        if changed:
            meta["date_updated"] = date
            log.append(f"~ {card_id}: " + ", ".join(changed))
            if not dry_run:
                write_card(doc, schema)
    return log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Применение патчей наполнения к карточкам")
    parser.add_argument("patches", nargs="+")
    parser.add_argument("--kb", default=str(KB))
    parser.add_argument("--date", default="2026-09-16")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    total = 0
    for patch_path in args.patches:
        patch = yaml.safe_load(Path(patch_path).read_text(encoding="utf-8")) or {}
        for line in apply(patch, Path(args.kb), args.date, args.dry_run):
            print(line)
            total += 1
    print(f"Изменено/создано карточек: {total}{' (сухой прогон)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

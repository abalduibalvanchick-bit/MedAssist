"""Чтение и запись карточек базы знаний с сохранением Markdown-тела.

Используется инструментами сопровождения (мигратор, наполнение машиночитаемого
слоя, генераторы). Гарантирует единый стиль YAML: канонический порядок ключей,
Unicode без экранирования, многострочные строки в блочном стиле, комментарий
о незаполненном машиночитаемом слое.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .markdown_parser import split_front_matter
from .schema import Schema

KEY_ORDER = [
    "id", "schema_version", "title", "domain", "category",
    "icd_10", "icd_11", "atc_code", "inn",
    "body_system", "tags", "urgency", "access_level", "target_specialist", "age_group",
    "evidence_level", "recommendation_class", "synonyms",
    "relations",
]
TAIL_ORDER = [
    "sources", "clinical_guidelines", "last_medical_review", "medical_reviewer",
    "author", "version", "date_created", "date_updated", "status", "disclaimer", "notes",
]
EMPTY = (None, [], {}, "")


@dataclass
class CardDocument:
    path: Path
    meta: dict[str, Any]
    body: str


class _Dumper(yaml.SafeDumper):
    """Дампер без алиасов и с блочным стилем для многострочных строк."""

    def ignore_aliases(self, data: Any) -> bool:  # noqa: D401 - сигнатура PyYAML
        return True


def _str_presenter(dumper: yaml.SafeDumper, data: str):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_Dumper.add_representer(str, _str_presenter)


def dump_yaml(meta: dict[str, Any]) -> str:
    return yaml.dump(meta, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=1000, default_flow_style=False)


def read_card(path: Path) -> CardDocument:
    raw = path.read_text(encoding="utf-8")
    yaml_text, body = split_front_matter(raw, path)
    meta = yaml.safe_load(yaml_text) or {}
    return CardDocument(path=path, meta=meta, body=body)


def ordered_meta(meta: dict[str, Any], schema: Schema, category: str) -> dict[str, Any]:
    order = KEY_ORDER + list(schema.machine_fields(category)) + TAIL_ORDER
    result = {k: meta[k] for k in order if k in meta}
    for key, value in meta.items():
        if key not in result:
            result[key] = value
    return result


def machine_layer_missing(meta: dict[str, Any], schema: Schema, category: str) -> list[str]:
    return [f for f in schema.machine_required_for_approved(category) if meta.get(f) in EMPTY]


def machine_comment(meta: dict[str, Any], schema: Schema, category: str) -> str:
    missing = machine_layer_missing(meta, schema, category)
    if not missing:
        return ""
    return (f"# Машиночитаемый слой (schema v2) не заполнен. Для status: approved требуются поля: "
            f"{', '.join(missing)}. См. docs/schema.md, раздел «{category}».\n")


def render_card(meta: dict[str, Any], body: str, schema: Schema) -> str:
    category = str(meta.get("category", ""))
    return "---\n" + dump_yaml(ordered_meta(meta, schema, category)) + machine_comment(meta, schema, category) + "---\n" + body


def write_card(doc: CardDocument, schema: Schema, path: Path | None = None) -> Path:
    target = path or doc.path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_card(doc.meta, doc.body, schema), encoding="utf-8")
    return target

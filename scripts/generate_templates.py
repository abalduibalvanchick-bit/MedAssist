"""Генерирует шаблоны карточек kb/templates/template_<category>.md из схемы.

Запуск из корня проекта:
    python scripts/generate_templates.py

Для каждой из категорий схемы создаётся шаблон, содержащий:
* YAML-блок со всеми обязательными полями, подсказками о допустимых значениях
  перечислений и примером связи допустимого для категории типа;
* скелет машиночитаемого слоя, построенный по типам полей схемы, с пометкой
  полей, обязательных для status: approved;
* рекомендуемые разделы Markdown-тела (schema.yaml, раздел sections).

Шаблоны не редактируются вручную: при изменении схемы их нужно перегенерировать.
Устаревшие шаблоны (категорий, которых нет в схеме) удаляются.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.schema import Schema, load_schema  # noqa: E402

OUT = ROOT / "kb" / "templates"
HEADER = "# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную."
EXAMPLE_CONDITION = {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}


def example_id(schema: Schema, categories: list[str]) -> str:
    cat = categories[0] if categories else "disease"
    info = schema.categories.get(cat)
    if info is None:
        return "DIAG-DISEASE-001"
    return f"{schema.domains[info.domain]['id_prefix']}-{cat.upper()}-001"


def id_categories(ftype: str) -> list[str]:
    if "(" not in ftype:
        return []
    return [c.strip() for c in ftype[ftype.index("(") + 1:ftype.rindex(")")].split(",") if c.strip()]


def example_value(schema: Schema, spec: dict[str, Any]) -> Any:
    ftype = str(spec.get("type", "string"))
    if ftype.startswith("list["):
        inner = ftype[5:-1]
        if inner == "object":
            return [example_object(schema, spec.get("item") or {})]
        return [example_value(schema, {"type": inner})]
    if ftype == "object":
        return example_object(schema, spec.get("item") or {})
    if ftype.startswith("id"):
        return example_id(schema, id_categories(ftype))
    if ftype.startswith("enum("):
        values = schema.enum(ftype[5:-1])
        return values[0] if values else "<значение>"
    if ftype == "condition":
        return EXAMPLE_CONDITION
    if ftype == "number":
        return 0
    if ftype == "boolean":
        return True
    if ftype == "parameter":
        return "sbp"
    return "<текст>"


def example_object(schema: Schema, item: dict[str, Any]) -> dict[str, Any]:
    return {key: example_value(schema, sub or {}) for key, sub in item.items()}


def flow(value: Any) -> str:
    """Компактная запись значения в YAML flow-стиле (JSON — подмножество YAML)."""
    return json.dumps(value, ensure_ascii=False)


def relation_example(schema: Schema, category: str) -> tuple[str, str]:
    for name, info in schema.relation_types.items():
        if info.from_categories and category in info.from_categories and info.to_categories:
            return name, example_id(schema, list(info.to_categories))
    return "associated_with", "DIAG-DISEASE-001"


def enum_hint(schema: Schema, name: str) -> str:
    return " | ".join(map(str, schema.enum(name)))


def render_template(schema: Schema, category: str) -> str:
    info = schema.categories[category]
    domain = info.domain
    dom = schema.domains[domain]
    card_id = f"{dom['id_prefix']}-{category.upper()}-NNN"
    rel_type, rel_target = relation_example(schema, category)
    required = set(schema.machine_required_for_approved(category))
    lines = [
        "---",
        HEADER,
        f"# Категория: {category} — {info.title}. Файл: kb/{dom['folder']}/{info.folder}/{domain}_{category}_<краткое_имя>.md",
        f"id: {card_id}",
        "schema_version: 2",
        "title: <Название>",
        f"domain: {domain}",
        f"category: {category}",
        f"body_system: [{schema.enum('body_system')[0]}]  # {enum_hint(schema, 'body_system')}",
        "tags: [<тег>]",
        f"urgency: routine  # {enum_hint(schema, 'urgency')}",
        f"access_level: professional  # {enum_hint(schema, 'access_level')}",
        f"target_specialist: [therapist]  # см. docs/metadata_schema.md, перечисление target_specialist",
        f"age_group: [adult]  # {enum_hint(schema, 'age_group')}",
        f"# evidence_level: Ia  # необязательно: {enum_hint(schema, 'evidence_level')}",
        f"# recommendation_class: I  # необязательно: {enum_hint(schema, 'recommendation_class')}",
        "relations:",
        f"  - target: {rel_target}",
        f"    type: {rel_type}  # типы и допустимые категории: docs/link_types.md",
        "    description: <смысл связи>",
    ]
    fields = schema.machine_fields(category)
    if fields:
        lines.append(f"# Машиночитаемый слой (docs/schema.md, раздел «{category}»):")
        for name, spec in fields.items():
            spec = spec or {}
            mark = "обязательно для approved" if name in required else ("необязательно" if spec.get("optional") else "рекомендуется")
            doc = f"; {spec['doc']}" if spec.get("doc") else ""
            lines.append(f"{name}: {flow(example_value(schema, spec))}  # {spec.get('type', '')}; {mark}{doc}")
    lines += [
        "sources:",
        "  - <Автор(ы). Название. Издание/журнал. Год;том:страницы.>",
        "  - <Вторая конкретная библиографическая ссылка>",
        "clinical_guidelines: [<Краткое название КР, год>]",
        "last_medical_review: YYYY-MM-DD",
        f"medical_reviewer: {schema.model_review_marker}",
        "author: <Инженер знаний №N>",
        "version: '2.0'",
        "date_created: YYYY-MM-DD",
        "date_updated: YYYY-MM-DD",
        f"status: draft  # {enum_hint(schema, 'status')}; approved — только при заполненном машиночитаемом слое",
        "disclaimer: true",
        "---",
        "",
        f"# <Название>",
        "",
        "> ⚕️ **Дисклеймер**: Информация носит справочный характер и не заменяет консультацию специалиста.",
        "",
    ]
    for section in (schema.raw.get("sections") or {}).get(category, []):
        lines.append(f"## {section}")
        if section == "Источники":
            lines.append("<генерируется из поля sources: python scripts/sync_body_sources.py>")
        else:
            lines.append("<заполнить>")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    schema = load_schema(ROOT / "kb" / "_schema" / "schema.yaml")
    OUT.mkdir(parents=True, exist_ok=True)
    expected = set()
    for category in schema.categories:
        path = OUT / f"template_{category}.md"
        path.write_text(render_template(schema, category), encoding="utf-8")
        expected.add(path.name)
    for stale in OUT.glob("template_*.md"):
        if stale.name not in expected:
            stale.unlink()
    print(f"Сгенерировано шаблонов: {len(expected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

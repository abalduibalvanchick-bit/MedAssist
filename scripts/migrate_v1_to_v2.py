"""Мигратор базы знаний MedAssist со схемы v1 на схему v2.

Запуск из корня проекта:
    python scripts/migrate_v1_to_v2.py --dry-run     # только отчёт, файлы не меняются
    python scripts/migrate_v1_to_v2.py               # выполнить миграцию

Свойства:
* детерминированность — одинаковый вход даёт одинаковый результат;
* идемпотентность — карточки со schema_version >= 2 не изменяются, повторный
  запуск ничего не делает;
* все решения протоколируются в docs/migration_v1_to_v2.md.

Что делает мигратор:
1. Переносит папки доменов: kb/diagnostics -> kb/diag, kb/therapy -> kb/pharm,
   kb/protocols -> kb/prot, kb/global -> kb/glb.
2. Переименовывает файлы, чьё имя не начинается с <domain>_<category>_.
3. Нормализует метаданные: domain, category, schema_version, version, даты,
   medical_reviewer, status, evidence_level; удаляет пустые необязательные поля.
4. Преобразует связи: тип v1 -> тип v2 с проверкой допустимых категорий по схеме;
   переносит цели из related в relations; удаляет related; устраняет дубликаты.
5. Записывает YAML в едином стиле и добавляет комментарий о незаполненном
   машиночитаемом слое.
Тело карточки (Markdown) не изменяется.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.markdown_parser import split_front_matter  # noqa: E402
from src.schema import Schema, load_schema  # noqa: E402

KB = ROOT / "kb"
REPORT_PATH = ROOT / "docs" / "migration_v1_to_v2.md"
MIGRATION_DATE = "2026-09-16"
EXCLUDED_DIRS = {"templates", "_schema", "rules"}
EXCLUDED_FILES = {"index.md", "README.md"}
EMPTY_REVIEWER = {"", "—", "-", "ФИО", "ФИО, специальность", "ФИО рецензента, специальность", "ФИО врача", "ФИО, степень"}

# Канонический порядок ключей в YAML-блоке v2.
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
OPTIONAL_DROP_IF_EMPTY = {"icd_10", "icd_11", "atc_code", "inn", "evidence_level", "recommendation_class", "notes"}

# Тип связи по паре категорий, когда исходный тип v1 не несёт направления или
# недопустим для этой пары по схеме v2. Это знание о миграции, а не о медицине.
PAIR_DEFAULT: dict[tuple[str, str], str] = {}


def _pairs(sources: list[str], targets: list[str], rtype: str) -> None:
    for s in sources:
        for t in targets:
            PAIR_DEFAULT[(s, t)] = rtype


# диагностика
_pairs(["disease"], ["symptom"], "has_symptom")
_pairs(["disease", "emergency", "symptom", "redflag"], ["exam"], "diagnosed_by")
_pairs(["disease", "emergency", "symptom"], ["redflag"], "has_red_flag")
_pairs(["disease"], ["emergency"], "complicated_by")
_pairs(["disease", "emergency"], ["difdiag"], "considered_in")
_pairs(["symptom"], ["disease", "emergency"], "symptom_of")
_pairs(["symptom"], ["difdiag"], "has_differential")
_pairs(["exam"], ["disease", "emergency", "symptom", "redflag"], "diagnoses")
_pairs(["exam"], ["difdiag", "screening", "protocol", "checklist", "follow_up", "routing", "emergency_p"], "exam_used_in")
_pairs(["difdiag"], ["disease", "emergency", "redflag"], "considers")
_pairs(["difdiag"], ["symptom"], "differential_for")
_pairs(["difdiag", "protocol", "checklist", "follow_up", "screening", "routing", "emergency_p"], ["exam"], "uses_exam")
_pairs(["redflag"], ["disease", "emergency", "symptom", "difdiag", "routing"], "red_flag_for")
_pairs(["emergency"], ["symptom"], "has_symptom")
_pairs(["emergency"], ["disease"], "complicates")
# протоколы
_pairs(["protocol"], ["disease", "emergency"], "protocol_for")
_pairs(["protocol"], ["checklist"], "has_checklist")
_pairs(["protocol"], ["follow_up"], "has_follow_up")
_pairs(["protocol"], ["patient_info"], "has_patient_info")
_pairs(["protocol", "patient_info", "checklist"], ["routing"], "has_routing")
_pairs(["protocol", "emergency_p", "follow_up", "checklist", "routing", "screening"], ["scale"], "assessed_by")
_pairs(["protocol"], ["screening"], "has_screening")
_pairs(["protocol", "routing", "follow_up"], ["emergency_p"], "has_emergency_protocol")
_pairs(["protocol", "emergency_p", "follow_up", "routing", "scale"], ["regimen", "drug", "drugclass", "nonpharm"], "recommends")
_pairs(["emergency_p"], ["disease", "emergency", "redflag", "protocol"], "emergency_protocol_for")
_pairs(["emergency_p", "screening", "follow_up"], ["routing"], "next_step")
_pairs(["routing"], ["disease", "emergency", "symptom", "protocol"], "routing_for")
_pairs(["routing"], ["redflag"], "has_red_flag")
_pairs(["routing"], ["follow_up"], "next_step")
_pairs(["scale"], ["disease", "emergency", "protocol", "routing", "symptom"], "assesses")
_pairs(["screening"], ["disease", "protocol"], "screening_for")
_pairs(["follow_up"], ["disease", "protocol"], "follow_up_for")
_pairs(["patient_info"], ["disease", "protocol", "drug", "emergency", "nonpharm"], "patient_info_for")
_pairs(["checklist"], ["disease", "protocol"], "checklist_for")
# фармакология
_pairs(["drug", "drugclass", "regimen", "nonpharm"], ["disease", "emergency", "symptom"], "treats")
_pairs(["drug"], ["drugclass", "regimen"], "included_in")
_pairs(["drugclass", "nonpharm"], ["regimen"], "included_in")
_pairs(["drugclass", "regimen"], ["drug"], "includes")
_pairs(["regimen"], ["drugclass", "nonpharm"], "includes")
_pairs(["drug", "drugclass"], ["interaction"], "has_interaction")
_pairs(["drug", "drugclass"], ["adr"], "causes_adr")
_pairs(["drug", "drugclass", "regimen"], ["dosing"], "dose_adjusted_by")
_pairs(["regimen", "drug", "drugclass", "nonpharm"], ["protocol", "emergency_p", "follow_up", "routing"], "recommended_by")
_pairs(["nonpharm"], ["patient_info"], "has_patient_info")
_pairs(["dosing"], ["drug", "drugclass", "regimen"], "dose_adjustment_for")
_pairs(["adr"], ["drug", "drugclass"], "adr_caused_by")
_pairs(["interaction"], ["drug", "drugclass"], "interaction_for")

GENERIC_TYPES = {"associated_with"}


# ---------------------------------------------------------------------------
@dataclass
class CardFile:
    path: Path
    meta: dict[str, Any]
    body: str
    raw: str


@dataclass
class MigrationLog:
    folder_moves: list[tuple[str, str]] = field(default_factory=list)
    file_renames: list[tuple[str, str]] = field(default_factory=list)
    relation_changes: Counter = field(default_factory=Counter)
    relation_examples: dict[tuple[str, str, str, str], str] = field(default_factory=dict)
    related_moved: int = 0
    duplicates_removed: int = 0
    reviewer_replaced: Counter = field(default_factory=Counter)
    status_changes: Counter = field(default_factory=Counter)
    evidence_fixes: list[str] = field(default_factory=list)
    few_sources: list[str] = field(default_factory=list)
    migrated: int = 0
    skipped_v2: int = 0
    unresolved: list[str] = field(default_factory=list)


def is_card(path: Path, kb: Path) -> bool:
    rel = path.relative_to(kb)
    if path.name in EXCLUDED_FILES:
        return False
    return not any(part in EXCLUDED_DIRS for part in rel.parts)


def read_card(path: Path) -> CardFile:
    raw = path.read_text(encoding="utf-8")
    yaml_text, body = split_front_matter(raw, path)
    meta = yaml.safe_load(yaml_text) or {}
    return CardFile(path=path, meta=meta, body=body, raw=raw)


def relation_valid(schema: Schema, rtype: str, src: str, tgt: str) -> bool:
    info = schema.relation_types.get(rtype)
    if info is None:
        return False
    if info.from_categories and src not in info.from_categories:
        return False
    if info.to_categories and tgt not in info.to_categories:
        return False
    return True


def resolve_relation(schema: Schema, old_type: str, src: str, tgt: str) -> tuple[str, str]:
    """Возвращает (тип v2, способ выбора)."""
    mapped = schema.normalize_relation_type(old_type) if old_type else "associated_with"
    if mapped not in schema.relation_types:
        mapped = "associated_with"
    if mapped not in GENERIC_TYPES and relation_valid(schema, mapped, src, tgt):
        return mapped, "прямое соответствие" if mapped == old_type else "алиас v1"
    # Тип по паре категорий приоритетнее обращения: он задаёт единый тип для всех
    # связей данной пары, тогда как обращение зависит от случайного исходного типа.
    default = PAIR_DEFAULT.get((src, tgt))
    if default and relation_valid(schema, default, src, tgt):
        inverse = schema.inverse_relation(mapped) if mapped not in GENERIC_TYPES else None
        return default, "обращение направления" if default == inverse else "по паре категорий"
    inverse = schema.inverse_relation(mapped)
    if mapped not in GENERIC_TYPES and inverse and relation_valid(schema, inverse, src, tgt):
        return inverse, "обращение направления"
    return "associated_with", "общая ассоциация"


def bump_version(value: Any) -> str:
    try:
        major = int(str(value).split(".")[0])
    except (TypeError, ValueError):
        major = 1
    return f"{major + 1}.0"


def ordered(meta: dict[str, Any], schema: Schema, category: str) -> dict[str, Any]:
    machine = list(schema.machine_fields(category))
    order = KEY_ORDER + machine + TAIL_ORDER
    result = {k: meta[k] for k in order if k in meta}
    for k in meta:
        if k not in result:
            result[k] = meta[k]
    return result


class _Dumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_Dumper.add_representer(str, _str_presenter)


def dump_yaml(meta: dict[str, Any]) -> str:
    return yaml.dump(meta, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=1000, default_flow_style=False)


def machine_comment(schema: Schema, category: str, meta: dict[str, Any]) -> str:
    required = schema.machine_required_for_approved(category)
    missing = [f for f in required if meta.get(f) in (None, [], {}, "")]
    if not missing:
        return ""
    return (f"# Машиночитаемый слой (schema v2) не заполнен. Для status: approved требуются поля: "
            f"{', '.join(missing)}. См. docs/schema.md, раздел «{category}».\n")


# ---------------------------------------------------------------------------
def plan_folder_moves(kb: Path, schema: Schema) -> list[tuple[Path, Path]]:
    moves = []
    for legacy, domain in schema.legacy_domain_aliases.items():
        src = kb / legacy
        dst = kb / schema.domains[domain]["folder"]
        if src.exists() and src != dst:
            moves.append((src, dst))
    return sorted(set(moves))


def migrate(kb: Path, schema: Schema, dry_run: bool) -> MigrationLog:
    log = MigrationLog()

    # 1. Папки доменов.
    for src, dst in plan_folder_moves(kb, schema):
        log.folder_moves.append((str(src.relative_to(kb)), str(dst.relative_to(kb))))
        if dry_run:
            continue
        if dst.exists():
            for item in src.iterdir():
                shutil.move(str(item), str(dst / item.name))
            src.rmdir()
        else:
            shutil.move(str(src), str(dst))

    # В сухом прогоне работаем со старыми путями, но вычисляем новые.
    def future_path(path: Path) -> Path:
        rel = path.relative_to(kb)
        first = rel.parts[0]
        if first in schema.legacy_domain_aliases:
            first = schema.domains[schema.legacy_domain_aliases[first]]["folder"]
        return kb.joinpath(first, *rel.parts[1:])

    card_files = [read_card(p) for p in sorted(kb.rglob("*.md")) if is_card(p, kb)]
    by_id: dict[str, CardFile] = {c.meta.get("id"): c for c in card_files if c.meta.get("id")}
    categories = {cid: schema.normalize_category(str(c.meta.get("category", ""))) for cid, c in by_id.items()}

    for card in card_files:
        meta = dict(card.meta)
        try:
            version = int(meta.get("schema_version", 1))
        except (TypeError, ValueError):
            version = 1
        if version >= 2:
            log.skipped_v2 += 1
            continue
        cid = str(meta.get("id", ""))
        domain = schema.normalize_domain(str(meta.get("domain", "")))
        category = schema.normalize_category(str(meta.get("category", "")))
        meta["domain"] = domain
        meta["category"] = category
        meta["schema_version"] = 2

        # --- связи ---
        new_relations: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for rel in meta.get("relations") or []:
            if not isinstance(rel, dict):
                continue
            target = str(rel.get("target", "")).strip()
            old_type = str(rel.get("type", "")).strip()
            if not target:
                continue
            tgt_cat = categories.get(target)
            if tgt_cat is None:
                log.unresolved.append(f"{cid}: связь на несуществующую карточку {target}")
                new_type, how = schema.normalize_relation_type(old_type) or "associated_with", "цель не найдена"
            else:
                new_type, how = resolve_relation(schema, old_type, category, tgt_cat)
            if (target, new_type) in seen:
                log.duplicates_removed += 1
                continue
            seen.add((target, new_type))
            entry = {"target": target, "type": new_type}
            if rel.get("description"):
                entry["description"] = str(rel["description"]).strip()
            new_relations.append(entry)
            if old_type != new_type:
                key = (old_type or "—", new_type, category, tgt_cat or "?")
                log.relation_changes[(old_type or "—", new_type, how)] += 1
                log.relation_examples.setdefault(key, f"{cid} -> {target}")
        targets_in_relations = {r["target"] for r in new_relations}
        for target in meta.get("related") or []:
            target = str(target).strip()
            if not target or target in targets_in_relations:
                continue
            tgt_cat = categories.get(target)
            if tgt_cat is None:
                log.unresolved.append(f"{cid}: related на несуществующую карточку {target}")
                continue
            new_type, how = resolve_relation(schema, "", category, tgt_cat)
            if (target, new_type) in seen:
                continue
            seen.add((target, new_type))
            new_relations.append({"target": target, "type": new_type, "description": "перенесено из поля related (схема v1)"})
            targets_in_relations.add(target)
            log.related_moved += 1
            log.relation_changes[("related", new_type, how)] += 1
        meta["relations"] = new_relations
        meta.pop("related", None)

        # --- служебные поля ---
        reviewer = str(meta.get("medical_reviewer", "") or "").strip()
        if reviewer != schema.model_review_marker:
            log.reviewer_replaced[reviewer or "(пусто)"] += 1
            meta["medical_reviewer"] = schema.model_review_marker
        status = str(meta.get("status", "")).strip()
        if status == "approved":
            required = schema.machine_required_for_approved(category)
            if any(meta.get(f) in (None, [], {}, "") for f in required):
                meta["status"] = "medical_review"
                log.status_changes["approved -> medical_review (нет машиночитаемого слоя)"] += 1
        elif status not in schema.enum("status"):
            meta["status"] = "draft"
            log.status_changes[f"{status or '(пусто)'} -> draft"] += 1
        ev = meta.get("evidence_level")
        if ev not in (None, "") and str(ev) not in schema.enum("evidence_level"):
            if str(ev) in schema.enum("recommendation_class") and not meta.get("recommendation_class"):
                meta["recommendation_class"] = str(ev)
            log.evidence_fixes.append(f"{cid}: evidence_level={ev!r} удалён (значение класса рекомендаций)")
            meta.pop("evidence_level", None)
        for key in list(meta):
            if key in OPTIONAL_DROP_IF_EMPTY and meta[key] in (None, ""):
                meta.pop(key)
        meta["version"] = bump_version(meta.get("version"))
        meta["date_updated"] = MIGRATION_DATE
        if len(meta.get("sources") or []) < schema.min_sources:
            log.few_sources.append(cid)

        # --- путь ---
        cat_info = schema.categories[category]
        new_dir = kb / schema.domains[domain]["folder"] / cat_info.folder
        expected_prefix = f"{domain}_{category}_"
        name = card.path.name
        if not name.startswith(expected_prefix):
            m = name.split("_", 2)
            stem = m[2] if len(m) == 3 else name
            # prot_emergency_x.md -> prot_emergency_p_x.md
            for prefix in (f"{domain}_{category.split('_')[0]}_", f"{name.split('_')[0]}_{category.split('_')[0]}_"):
                if name.startswith(prefix):
                    stem = name[len(prefix):]
                    break
            name = expected_prefix + stem
        name = name.lower()  # имена файлов только в нижнем регистре (pharm_drugclass_gLP1_... -> glp1)
        new_path = new_dir / name
        old_future = future_path(card.path)
        if old_future != new_path:
            log.file_renames.append((str(old_future.relative_to(kb)), str(new_path.relative_to(kb))))

        text = "---\n" + dump_yaml(ordered(meta, schema, category)) + machine_comment(schema, category, meta) + "---\n" + card.body
        log.migrated += 1
        if dry_run:
            continue
        current = old_future if old_future.exists() else card.path
        new_path.parent.mkdir(parents=True, exist_ok=True)
        new_path.write_text(text, encoding="utf-8")
        if current.resolve() != new_path.resolve() and current.exists():
            current.unlink()
    return log


# ---------------------------------------------------------------------------
def render_report(log: MigrationLog, dry_run: bool) -> str:
    lines = [
        "# Отчёт о миграции базы знаний v1 → v2",
        "",
        f"Режим: **{'сухой прогон' if dry_run else 'выполнено'}**. Дата миграции: {MIGRATION_DATE}.",
        "Сформировано скриптом `scripts/migrate_v1_to_v2.py`.",
        "",
        "## Итоги",
        "",
        f"- мигрировано карточек: **{log.migrated}**",
        f"- пропущено (уже v2): {log.skipped_v2}",
        f"- перенесено папок доменов: {len(log.folder_moves)}",
        f"- переименовано файлов: {len(log.file_renames)}",
        f"- изменено типов связей: {sum(c for (o, n, h), c in log.relation_changes.items() if o != 'related')}",
        f"- целей перенесено из related в relations: {log.related_moved}",
        f"- удалено дублирующих связей: {log.duplicates_removed}",
        f"- заменено значений medical_reviewer: {sum(log.reviewer_replaced.values())}",
        f"- изменено статусов: {sum(log.status_changes.values())}",
        f"- карточек с числом источников меньше минимума: {len(log.few_sources)}",
        f"- неразрешённых ссылок: {len(log.unresolved)}",
        "",
    ]
    if log.folder_moves:
        lines += ["## Папки доменов", "", "| Было | Стало |", "|---|---|"]
        lines += [f"| `kb/{a}` | `kb/{b}` |" for a, b in log.folder_moves]
        lines.append("")
    if log.file_renames:
        lines += ["## Переименованные файлы", "", "| Было | Стало |", "|---|---|"]
        lines += [f"| `{a}` | `{b}` |" for a, b in log.file_renames if a.split("/")[-1] != b.split("/")[-1]]
        lines.append("")
    if log.relation_changes:
        lines += ["## Преобразование типов связей", "", "| Тип v1 | Тип v2 | Способ | Количество |", "|---|---|---|---|"]
        for (old, new, how), count in sorted(log.relation_changes.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"| `{old}` | `{new}` | {how} | {count} |")
        lines += ["", "Способы выбора типа: *алиас v1* — по таблице `legacy_relation_aliases` схемы; "
                      "*обращение направления* — исходный тип указывал в обратную сторону, использован обратный тип; "
                      "*по паре категорий* — тип выбран по категориям источника и цели; *общая ассоциация* — "
                      "специфичный тип для пары категорий не определён.", ""]
    if log.reviewer_replaced:
        lines += ["## Поле medical_reviewer", "",
                  "Внешняя медицинская верификация в учебном проекте не проводилась. Все значения, включая "
                  "условные ФИО из примеров ТЗ, заменены на единообразную маркировку.", "",
                  "| Было | Количество |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in log.reviewer_replaced.most_common()]
        lines.append("")
    if log.status_changes:
        lines += ["## Статусы", "", "| Изменение | Количество |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in log.status_changes.items()]
        lines.append("")
    if log.evidence_fixes:
        lines += ["## Исправления evidence_level", ""] + [f"- {x}" for x in log.evidence_fixes] + [""]
    if log.few_sources:
        lines += ["## Карточки с недостаточным числом источников", "",
                  "Требуется дополнить до двух источников: " + ", ".join(f"`{x}`" for x in sorted(log.few_sources)), ""]
    if log.unresolved:
        lines += ["## Неразрешённые ссылки", ""] + [f"- {x}" for x in log.unresolved] + [""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Миграция базы знаний MedAssist v1 -> v2")
    parser.add_argument("--kb", default=str(KB))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", default=str(REPORT_PATH))
    args = parser.parse_args(argv)
    schema = load_schema(ROOT / "kb" / "_schema" / "schema.yaml")
    log = migrate(Path(args.kb), schema, args.dry_run)
    report = render_report(log, args.dry_run)
    if args.dry_run:
        print(report)
    else:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(report, encoding="utf-8")
        print(f"Миграция выполнена: {log.migrated} карточек. Отчёт: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

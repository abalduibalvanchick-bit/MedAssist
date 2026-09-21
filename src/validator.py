"""Валидатор базы знаний MedAssist (схема v2).

Три уровня проверки:

* ERROR   — нарушение структуры, при котором база считается сломанной;
* WARNING — допустимо, но требует внимания (устаревшие формы, неполнота);
* INFO    — качественные признаки, не влияющие на итог (например, доля
            карточек в статусе approved).

Карточки схемы v1 (без поля schema_version) проверяются в режиме
совместимости прежними правилами. Карточки схемы v2 проверяются строго
по kb/_schema/schema.yaml: инвариант домена, перечисления, связи и их
категории, машиночитаемый слой, условия мини-языка, правила kb/rules.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .conditions import validate_condition
from .config import (
    ALLOWED_RELATION_TYPES,
    ALLOWED_STATUS,
    ALLOWED_URGENCY,
    FOLDER_CATEGORY_RULES,
    REQUIRED_FIELDS_V1,
    RULES_ROOT,
    SCHEMA,
)
from .models import KnowledgeCard
from .repository import KnowledgeRepository
from .schema import Schema

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STUB_MARKERS = ("служебная интеграционная карточка", "интеграционная карточка", "заглушка")
STUB_MIN_CONTENT_CHARS = 600
EMPTY_REVIEWER_VALUES = {"", "—", "-", "ФИО", "ФИО, специальность", "ФИО рецензента, специальность", "ФИО врача", "ФИО, степень"}


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    file_path: str
    card_id: str
    message: str


@dataclass
class ValidationReport:
    total_cards: int
    total_rules: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)
    parse_errors: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def _by_severity(self, severity: str) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == severity]

    @property
    def errors(self) -> list[ValidationIssue]:
        return self._by_severity("ERROR")

    @property
    def warnings(self) -> list[ValidationIssue]:
        return self._by_severity("WARNING")

    @property
    def infos(self) -> list[ValidationIssue]:
        return self._by_severity("INFO")

    @property
    def is_valid(self) -> bool:
        return not self.parse_errors and not self.errors

    def to_markdown(self) -> str:
        lines = [
            "# Отчёт проверки базы знаний MedAssist",
            "",
            f"Проверено карточек: **{self.total_cards}**.",
            f"Проверено правил: **{self.total_rules}**.",
            f"Ошибок парсинга: **{len(self.parse_errors)}**.",
            f"Структурных ошибок: **{len(self.errors)}**.",
            f"Предупреждений: **{len(self.warnings)}**.",
            f"Итог: **{'проверка пройдена' if self.is_valid else 'требуются исправления'}**.",
            "",
        ]
        if self.stats:
            lines.extend(["## Показатели качества", ""])
            lines.extend(f"- {key}: {value}" for key, value in self.stats.items())
            lines.append("")
        if self.parse_errors:
            lines.extend(["## Ошибки парсинга", ""])
            lines.extend(f"- {error}" for error in self.parse_errors)
            lines.append("")
        visible = [i for i in self.issues if i.severity != "INFO"]
        if visible:
            lines.extend([
                "## Найденные замечания",
                "",
                "| Уровень | Код | ID | Файл | Сообщение |",
                "|---|---|---|---|---|",
            ])
            for issue in visible:
                msg = issue.message.replace("|", "\\|")
                lines.append(f"| {issue.severity} | {issue.code} | {issue.card_id} | {issue.file_path} | {msg} |")
        return "\n".join(lines)


class KnowledgeBaseValidator:
    """Проверяет структурную целостность и качество базы знаний."""

    def __init__(self, repository: KnowledgeRepository, schema: Schema = SCHEMA, rules_root: Path | None = None) -> None:
        self.repository = repository
        self.schema = schema
        self.rules_root = rules_root if rules_root is not None else RULES_ROOT
        self._known_ids: set[str] = set()
        self._known_features: set[str] = set()
        self._exam_values: dict[str, set[str]] = {}
        self._scale_categories: dict[str, set[str]] = {}
        self._cards_by_id: dict[str, KnowledgeCard] = {}

    # ------------------------------------------------------------------ вход
    def validate(self) -> ValidationReport:
        report = ValidationReport(
            total_cards=len(self.repository.cards),
            parse_errors=list(self.repository.parse_errors),
        )
        self._collect_registries()
        self._validate_unique_ids(report)

        for card in self.repository.cards:
            if card.schema_version >= 2:
                self._validate_v2(card, report)
            else:
                self._validate_v1(card, report)

        self._validate_relation_symmetry(report)
        report.total_rules = self._validate_rules(report)
        self._collect_stats(report)
        return report

    def save_report(self, output_path: Path) -> ValidationReport:
        report = self.validate()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report.to_markdown(), encoding="utf-8")
        return report

    # ------------------------------------------------------------- реестры
    def _collect_registries(self) -> None:
        self._known_ids = {card.id for card in self.repository.cards if card.id}
        self._cards_by_id = {card.id: card for card in self.repository.cards if card.id}
        self._known_features = set()
        self._exam_values = {}
        self._scale_categories = {}
        for card in self.repository.cards:
            if card.category == "symptom":
                for item in card.machine_field("features", []) or []:
                    if isinstance(item, dict) and item.get("code"):
                        self._known_features.add(str(item["code"]))
            elif card.category == "exam":
                values = {str(r.get("value")) for r in (card.machine_field("results", []) or []) if isinstance(r, dict)}
                if values:
                    self._exam_values[card.id] = values
            elif card.category == "scale":
                cats = {str(r.get("category")) for r in (card.machine_field("interpretation", []) or []) if isinstance(r, dict)}
                if cats:
                    self._scale_categories[card.id] = cats

    # ------------------------------------------------------------- утилиты
    def _add(self, report: ValidationReport, card: KnowledgeCard | None, severity: str, code: str, message: str,
             file_path: str | None = None, card_id: str | None = None) -> None:
        report.issues.append(ValidationIssue(
            severity=severity,
            code=code,
            file_path=file_path if file_path is not None else (str(card.file_path) if card else ""),
            card_id=card_id if card_id is not None else ((card.id or "<no id>") if card else "<rule>"),
            message=message,
        ))

    def _rel_path(self, card: KnowledgeCard) -> Path:
        try:
            return card.file_path.relative_to(self.repository.kb_root)
        except ValueError:
            return card.file_path

    def _condition_issues(self, node: Any, path: str):
        return validate_condition(
            node, self.schema,
            known_ids=self._known_ids, known_features=self._known_features,
            known_exam_values=self._exam_values, known_scale_categories=self._scale_categories,
            path=path,
        )

    # ---------------------------------------------------------- общие проверки
    def _validate_unique_ids(self, report: ValidationReport) -> None:
        for card_id, cards in self.repository.index.duplicates.items():
            for card in cards:
                self._add(report, card, "ERROR", "DUPLICATE_ID", f"Идентификатор {card_id} повторяется в нескольких карточках.")

    def _validate_dates(self, card: KnowledgeCard, report: ValidationReport) -> None:
        for field_name in ("date_created", "date_updated", "last_medical_review"):
            value = str(card.metadata.get(field_name, "")).strip()
            if value and not DATE_PATTERN.match(value):
                self._add(report, card, "WARNING", "BAD_DATE_FORMAT", f"Поле {field_name} должно иметь формат YYYY-MM-DD.")

    def _validate_sources_and_disclaimer(self, card: KnowledgeCard, report: ValidationReport, min_sources: int) -> None:
        sources = card.metadata.get("sources", [])
        if not isinstance(sources, list) or not sources:
            self._add(report, card, "ERROR", "EMPTY_SOURCES", "Поле sources должно быть непустым списком.")
        elif len(sources) < min_sources:
            self._add(report, card, "WARNING", "FEW_SOURCES", f"Источников {len(sources)}, требуется не менее {min_sources}.")
        if card.metadata.get("disclaimer") is not True:
            self._add(report, card, "ERROR", "NO_DISCLAIMER", "Поле disclaimer должно иметь значение true.")

    def _validate_links(self, card: KnowledgeCard, report: ValidationReport, strict_types: bool) -> None:
        for target_id in card.related:
            if target_id not in self._known_ids:
                self._add(report, card, "ERROR", "BROKEN_RELATED", f"Ссылка related ведёт на несуществующий документ: {target_id}.")
        for relation in card.relations:
            target_id = str(relation.get("target", "")).strip()
            relation_type = str(relation.get("type", "")).strip()
            if not target_id:
                self._add(report, card, "ERROR", "EMPTY_RELATION_TARGET", "В relations отсутствует target.")
            elif target_id not in self._known_ids:
                self._add(report, card, "ERROR", "BROKEN_RELATION", f"Связь relations ведёт на несуществующий документ: {target_id}.")
            elif target_id == card.id:
                self._add(report, card, "WARNING", "SELF_RELATION", "Карточка ссылается сама на себя.")
            if not relation_type:
                self._add(report, card, "WARNING", "EMPTY_RELATION_TYPE", "В relations отсутствует type.")
                continue
            if strict_types:
                if relation_type not in self.schema.relation_types:
                    alias = self.schema.legacy_relation_aliases.get(relation_type)
                    hint = f" (устаревший тип; в v2 используйте {alias['type']})" if alias else ""
                    self._add(report, card, "ERROR", "UNKNOWN_RELATION_TYPE", f"Неизвестный тип связи: {relation_type}{hint}.")
                elif target_id in self._cards_by_id:
                    self._validate_relation_categories(card, target_id, relation_type, report)
            elif relation_type not in ALLOWED_RELATION_TYPES:
                self._add(report, card, "WARNING", "UNKNOWN_RELATION_TYPE", f"Неизвестный тип связи: {relation_type}.")

    def _validate_relation_categories(self, card: KnowledgeCard, target_id: str, relation_type: str, report: ValidationReport) -> None:
        info = self.schema.relation_types[relation_type]
        target = self._cards_by_id[target_id]
        if info.from_categories and card.category not in info.from_categories:
            self._add(report, card, "ERROR", "RELATION_SOURCE_CATEGORY",
                      f"Связь {relation_type} недопустима для карточки категории {card.category}; ожидается одна из {list(info.from_categories)}.")
        if info.to_categories and target.category not in info.to_categories:
            self._add(report, card, "ERROR", "RELATION_TARGET_CATEGORY",
                      f"Связь {relation_type} -> {target_id}: цель имеет категорию {target.category}, ожидается одна из {list(info.to_categories)}.")

    # ------------------------------------------------------------- режим v1
    def _validate_v1(self, card: KnowledgeCard, report: ValidationReport) -> None:
        self._add(report, card, "INFO", "SCHEMA_V1", "Карточка ещё не мигрирована на схему v2.")
        for field_name in REQUIRED_FIELDS_V1:
            if field_name not in card.metadata:
                self._add(report, card, "ERROR", "MISSING_FIELD", f"Отсутствует обязательное поле YAML: {field_name}.")
        domain = self.schema.normalize_domain(card.domain)
        if card.domain and domain not in self.schema.domain_codes:
            self._add(report, card, "WARNING", "UNKNOWN_DOMAIN", f"Неизвестный домен: {card.domain}.")
        category = self.schema.normalize_category(card.category)
        if domain in self.schema.domain_codes and category not in self.schema.categories_of_domain(domain):
            self._add(report, card, "ERROR", "UNKNOWN_CATEGORY", f"Недопустимая категория для домена {domain}: {card.category}.")
        if card.urgency and card.urgency not in ALLOWED_URGENCY:
            self._add(report, card, "ERROR", "UNKNOWN_URGENCY", f"Недопустимый уровень срочности: {card.urgency}.")
        if card.status and card.status not in ALLOWED_STATUS:
            self._add(report, card, "WARNING", "UNKNOWN_STATUS", f"Неизвестный статус карточки: {card.status}.")
        if category in {"emergency", "emergency_p"} and card.urgency != "emergency":
            self._add(report, card, "ERROR", "EMERGENCY_URGENCY", "Карточка emergency/emergency_p должна иметь urgency: emergency.")
        self._validate_sources_and_disclaimer(card, report, min_sources=1)
        self._validate_links(card, report, strict_types=False)
        self._validate_folder_category(card, report, category)
        self._validate_dates(card, report)
        self._validate_quality(card, report)

    # ------------------------------------------------------------- режим v2
    def _validate_v2(self, card: KnowledgeCard, report: ValidationReport) -> None:
        for field_name in self.schema.common_required:
            if field_name not in card.metadata:
                self._add(report, card, "ERROR", "MISSING_FIELD", f"Отсутствует обязательное поле YAML: {field_name}.")
        for field_name in self.schema.removed_in_v2:
            if field_name in card.metadata:
                self._add(report, card, "ERROR", "REMOVED_FIELD", f"Поле {field_name} удалено в схеме v2 и должно быть убрано из карточки.")

        self._validate_identity(card, report)

        for name in ("urgency", "status", "access_level"):
            self._check_enum(card, report, name, scalar=True)
        for name in ("body_system", "age_group", "target_specialist"):
            self._check_enum(card, report, name, scalar=False)
        for name in ("evidence_level", "recommendation_class"):
            if card.metadata.get(name) not in (None, ""):
                self._check_enum(card, report, name, scalar=True)

        if card.category in {"emergency", "emergency_p"} and card.urgency != "emergency":
            self._add(report, card, "ERROR", "EMERGENCY_URGENCY", "Карточка emergency/emergency_p должна иметь urgency: emergency.")
        if card.category == "patient_info" and card.metadata.get("access_level") != "patient":
            self._add(report, card, "WARNING", "PATIENT_INFO_ACCESS", "Памятка для пациента должна иметь access_level: patient.")

        reviewer = str(card.metadata.get("medical_reviewer", "")).strip()
        if reviewer in EMPTY_REVIEWER_VALUES:
            self._add(report, card, "ERROR", "EMPTY_REVIEWER",
                      f"medical_reviewer пуст; для учебного проекта используйте значение «{self.schema.model_review_marker}».")

        self._validate_sources_and_disclaimer(card, report, min_sources=self.schema.min_sources)
        self._validate_links(card, report, strict_types=True)
        self._validate_folder_category(card, report, card.category)
        self._validate_dates(card, report)
        self._validate_machine_layer(card, report)
        self._validate_quality(card, report)

    def _validate_identity(self, card: KnowledgeCard, report: ValidationReport) -> None:
        if not self.schema.id_pattern.match(card.id or ""):
            self._add(report, card, "ERROR", "BAD_ID_FORMAT", f"ID {card.id!r} не соответствует шаблону DOMAIN-CATEGORY-NNN.")
            return
        prefix, cat_code, _ = card.id.split("-", 2)
        expected_domain = self.schema.domain_for_id_prefix(prefix)
        if card.domain != expected_domain:
            self._add(report, card, "ERROR", "DOMAIN_ID_MISMATCH", f"domain={card.domain}, но префикс ID {prefix} соответствует домену {expected_domain}.")
        if card.category != cat_code.lower():
            self._add(report, card, "ERROR", "CATEGORY_ID_MISMATCH", f"category={card.category}, но ID содержит категорию {cat_code.lower()}.")
        cat_info = self.schema.categories.get(card.category)
        if cat_info is None:
            self._add(report, card, "ERROR", "UNKNOWN_CATEGORY", f"Неизвестная категория {card.category}.")
            return
        if cat_info.domain != card.domain:
            self._add(report, card, "ERROR", "CATEGORY_DOMAIN_MISMATCH", f"Категория {card.category} принадлежит домену {cat_info.domain}, а не {card.domain}.")
        if card.domain not in self.schema.domains:
            return
        rel = self._rel_path(card)
        parts = rel.parts
        domain_folder = self.schema.domains[card.domain]["folder"]
        if len(parts) < 3 or parts[0] != domain_folder or parts[-2] != cat_info.folder:
            self._add(report, card, "ERROR", "BAD_LOCATION", f"Файл должен лежать в kb/{domain_folder}/{cat_info.folder}/, фактически: {rel}.")
        name = card.file_path.name
        expected_prefix = f"{card.domain}_{card.category}_"
        if not self.schema.file_pattern.match(name):
            self._add(report, card, "ERROR", "BAD_FILE_NAME", f"Имя файла {name} не соответствует шаблону <domain>_<category>_<name>.md.")
        elif not name.startswith(expected_prefix) or not re.fullmatch(r"[a-z0-9_]+\.md", name[len(expected_prefix):]):
            self._add(report, card, "ERROR", "FILE_NAME_MISMATCH", f"Имя файла {name} должно начинаться с {expected_prefix} и содержать только [a-z0-9_].")

    def _check_enum(self, card: KnowledgeCard, report: ValidationReport, field_name: str, *, scalar: bool) -> None:
        if field_name not in card.metadata:
            return
        allowed = set(map(str, self.schema.enum(field_name)))
        value = card.metadata[field_name]
        if scalar:
            values = [value]
        elif isinstance(value, list):
            values = value
            if not value:
                self._add(report, card, "ERROR", "EMPTY_LIST", f"Поле {field_name} не должно быть пустым.")
        else:
            self._add(report, card, "ERROR", "FIELD_NOT_LIST", f"Поле {field_name} должно быть списком.")
            values = [value]
        for item in values:
            if str(item) not in allowed:
                self._add(report, card, "ERROR", f"BAD_ENUM_{field_name.upper()}", f"Недопустимое значение {field_name}: {item!r}.")

    def _validate_folder_category(self, card: KnowledgeCard, report: ValidationReport, category: str) -> None:
        rel = self._rel_path(card)
        if len(rel.parts) < 2:
            return
        folder = rel.parts[-2]
        expected = FOLDER_CATEGORY_RULES.get(folder)
        if expected and category != expected:
            self._add(report, card, "ERROR", "FOLDER_CATEGORY_MISMATCH", f"Файл находится в папке {folder}, но category={card.category}; ожидается {expected}.")

    # ----------------------------------------------------- машиночитаемый слой
    def _validate_machine_layer(self, card: KnowledgeCard, report: ValidationReport) -> None:
        spec = self.schema.machine_layer(card.category)
        fields = spec.get("fields", {}) or {}
        for field_name, field_spec in fields.items():
            if field_name in card.metadata:
                self._validate_machine_value(card, report, field_name, card.metadata[field_name], field_spec)
        if card.status == "approved" and self.schema.approved_requires_machine_layer:
            missing = [f for f in spec.get("required_for_approved", []) if card.metadata.get(f) in (None, [], {}, "")]
            if missing:
                self._add(report, card, "ERROR", "APPROVED_WITHOUT_MACHINE_LAYER",
                          f"status: approved требует заполненных полей машиночитаемого слоя: {missing}.")

    def _validate_machine_value(self, card: KnowledgeCard, report: ValidationReport, path: str, value: Any, spec: dict[str, Any]) -> None:
        ftype = str(spec.get("type", "")).strip()
        if value is None:
            if not spec.get("nullable"):
                self._add(report, card, "ERROR", "MACHINE_NULL", f"{path}: значение не может быть null.")
            return
        if ftype == "condition":
            for issue in self._condition_issues(value, path):
                self._add(report, card, "ERROR", "BAD_CONDITION", f"{issue.path}: {issue.message}")
        elif ftype.startswith("list["):
            if not isinstance(value, list):
                self._add(report, card, "ERROR", "MACHINE_TYPE", f"{path}: ожидается список.")
                return
            inner = ftype[5:-1]
            for i, item in enumerate(value):
                if inner == "object":
                    self._validate_machine_object(card, report, f"{path}[{i}]", item, spec.get("item", {}) or {})
                else:
                    self._validate_machine_value(card, report, f"{path}[{i}]", item, {"type": inner})
        elif ftype == "object":
            self._validate_machine_object(card, report, path, value, spec.get("item", {}) or {})
        elif ftype.startswith("id"):
            self._check_id_value(card, report, path, value, ftype)
        elif ftype.startswith("enum("):
            allowed = set(map(str, self.schema.enum(ftype[5:-1])))
            if str(value) not in allowed:
                self._add(report, card, "ERROR", "MACHINE_ENUM", f"{path}: значение {value!r} не входит в {sorted(allowed)}.")
        elif ftype == "feature_code":
            if str(value) not in self._known_features:
                self._add(report, card, "ERROR", "UNKNOWN_FEATURE", f"{path}: признак {value} не объявлен ни в одной карточке симптома.")
        elif ftype == "parameter":
            if str(value) not in self.schema.parameters:
                self._add(report, card, "ERROR", "UNKNOWN_PARAMETER", f"{path}: неизвестный параметр {value}.")
        elif ftype == "operator":
            if str(value) not in self.schema.condition_operators:
                self._add(report, card, "ERROR", "BAD_OPERATOR", f"{path}: недопустимый оператор {value}.")
        elif ftype == "string":
            if not isinstance(value, str) or not value.strip():
                self._add(report, card, "ERROR", "MACHINE_TYPE", f"{path}: ожидается непустая строка.")
            elif spec.get("pattern") and not re.match(spec["pattern"], value):
                self._add(report, card, "ERROR", "MACHINE_PATTERN", f"{path}: значение {value!r} не соответствует шаблону {spec['pattern']}.")
            elif spec.get("enum") and value not in spec["enum"]:
                self._add(report, card, "ERROR", "MACHINE_ENUM", f"{path}: значение {value!r} не входит в {spec['enum']}.")
        elif ftype == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                self._add(report, card, "ERROR", "MACHINE_TYPE", f"{path}: ожидается число.")
        elif ftype == "boolean":
            if not isinstance(value, bool):
                self._add(report, card, "ERROR", "MACHINE_TYPE", f"{path}: ожидается true/false.")
        else:
            self._add(report, card, "WARNING", "SCHEMA_UNKNOWN_TYPE", f"{path}: тип {ftype!r} не поддерживается валидатором.")

    def _validate_machine_object(self, card: KnowledgeCard, report: ValidationReport, path: str, value: Any, item_spec: dict[str, Any]) -> None:
        if not isinstance(value, dict):
            self._add(report, card, "ERROR", "MACHINE_TYPE", f"{path}: ожидается объект.")
            return
        for key, sub_spec in item_spec.items():
            if key not in value:
                if not sub_spec.get("optional"):
                    self._add(report, card, "ERROR", "MACHINE_MISSING", f"{path}.{key}: обязательное поле отсутствует.")
                continue
            self._validate_machine_value(card, report, f"{path}.{key}", value[key], sub_spec)
        extra = set(value) - set(item_spec)
        if extra:
            self._add(report, card, "WARNING", "MACHINE_EXTRA", f"{path}: неизвестные поля {sorted(extra)}.")

    def _check_id_value(self, card: KnowledgeCard, report: ValidationReport, path: str, value: Any, ftype: str) -> None:
        if not isinstance(value, str) or not self.schema.id_pattern.match(value):
            self._add(report, card, "ERROR", "MACHINE_BAD_ID", f"{path}: некорректный идентификатор {value!r}.")
            return
        if value not in self._known_ids:
            self._add(report, card, "ERROR", "MACHINE_BROKEN_ID", f"{path}: ссылка на несуществующую карточку {value}.")
            return
        if "(" in ftype:
            allowed = {c.strip() for c in ftype[ftype.index("(") + 1:-1].split(",") if c.strip()}
            target = self._cards_by_id[value]
            if allowed and target.category not in allowed:
                self._add(report, card, "ERROR", "MACHINE_ID_CATEGORY", f"{path}: {value} имеет категорию {target.category}, ожидается одна из {sorted(allowed)}.")

    # ---------------------------------------------------------- симметрия
    def _validate_relation_symmetry(self, report: ValidationReport) -> None:
        """Ищет противоречивые пары явных связей.

        Между двумя карточками допустимо несколько связей разных типов (например,
        маршрут ссылается на алгоритм неотложной помощи, а алгоритм — на маршрут как
        на следующий шаг). Противоречием считается ситуация, когда обе карточки
        утверждают одно и то же направленное отношение друг о друге: A has_symptom B
        и B has_symptom A. Для симметричных типов это не противоречие.
        """
        explicit: dict[tuple[str, str], set[str]] = defaultdict(set)
        for card in self.repository.cards:
            if card.schema_version < 2:
                continue
            for relation in card.relations:
                target = str(relation.get("target", "")).strip()
                rtype = str(relation.get("type", "")).strip()
                if target and rtype:
                    explicit[(card.id, target)].add(rtype)
        rel_types = self.schema.relation_types
        for (source, target), types in explicit.items():
            if source > target:
                continue  # каждую пару проверяем один раз
            back = explicit.get((target, source), set())
            for rtype in types & back:
                info = rel_types.get(rtype)
                if info is not None and not info.symmetric:
                    card = self._cards_by_id.get(source)
                    if card is not None:
                        self._add(report, card, "ERROR", "CONTRADICTORY_RELATION",
                                  f"{source} и {target} оба утверждают связь {rtype} друг о друге; одна из сторон должна использовать {info.inverse_name()}.")

    # ------------------------------------------------------------ качество
    def _validate_quality(self, card: KnowledgeCard, report: ValidationReport) -> None:
        text = card.content.lower()
        if any(marker in text for marker in STUB_MARKERS) or len(card.content) < STUB_MIN_CONTENT_CHARS:
            self._add(report, card, "WARNING", "STUB_CARD", f"Карточка выглядит заглушкой (длина {len(card.content)} символов).")
        if card.id and not self.repository.index.inbound.get(card.id) and card.category not in {"disclaimer", "cross"}:
            self._add(report, card, "INFO", "ORPHAN", "На карточку не ссылается ни один документ.")

    # -------------------------------------------------------------- правила
    def _validate_rules(self, report: ValidationReport) -> int:
        if not self.rules_root.exists():
            return 0
        count = 0
        seen_ids: set[str] = set()
        for path in sorted(self.rules_root.rglob("*.yaml")):
            try:
                loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                report.parse_errors.append(f"Ошибка YAML в правиле {path}: {exc}")
                continue
            rules = loaded if isinstance(loaded, list) else [loaded]
            for rule in rules:
                count += 1
                self._validate_rule(rule, path, seen_ids, report)
        return count

    def _validate_rule(self, rule: Any, path: Path, seen_ids: set[str], report: ValidationReport) -> None:
        fp = str(path)
        if not isinstance(rule, dict):
            self._add(report, None, "ERROR", "RULE_NOT_OBJECT", "Правило должно быть словарём.", file_path=fp)
            return
        rid = str(rule.get("id", "<no id>"))

        def err(code: str, msg: str, severity: str = "ERROR") -> None:
            self._add(report, None, severity, code, msg, file_path=fp, card_id=rid)

        for req in self.schema.rule_required:
            if req not in rule:
                err("RULE_MISSING_FIELD", f"Отсутствует поле {req}.")
        if not self.schema.rule_id_pattern.match(rid):
            err("RULE_BAD_ID", f"ID правила {rid} не соответствует шаблону RULE-DOMAIN-NNN.")
        if rid in seen_ids:
            err("RULE_DUPLICATE_ID", f"ID правила {rid} повторяется.")
        seen_ids.add(rid)
        if rule.get("domain") not in self.schema.domain_codes:
            err("RULE_BAD_DOMAIN", f"Неизвестный домен {rule.get('domain')}.")
        extra = set(rule) - set(self.schema.rule_required) - set(self.schema.rule_optional)
        if extra:
            err("RULE_EXTRA_FIELD", f"Неизвестные поля {sorted(extra)}.", "WARNING")
        if "if" in rule:
            for issue in self._condition_issues(rule["if"], "if"):
                err("RULE_BAD_CONDITION", f"{issue.path}: {issue.message}")
        self._validate_rule_actions(rule, err)
        sources = rule.get("source_cards") or []
        if not sources:
            err("RULE_NO_SOURCES", "Правило должно ссылаться хотя бы на одну карточку-источник.")
        for src in sources:
            if src not in self._known_ids:
                err("RULE_BROKEN_SOURCE", f"source_cards ссылается на несуществующую карточку {src}.")

    def _validate_rule_actions(self, rule: dict[str, Any], err) -> None:
        actions = rule.get("then")
        if not isinstance(actions, list) or not actions:
            err("RULE_NO_ACTIONS", "then должно быть непустым списком действий.")
            return
        specs = self.schema.rule_actions
        for i, action in enumerate(actions):
            if not isinstance(action, dict) or len(action) != 1:
                err("RULE_BAD_ACTION", f"then[{i}]: действие должно быть словарём с одним ключом.")
                continue
            name, body = next(iter(action.items()))
            if name not in specs:
                err("RULE_UNKNOWN_ACTION", f"then[{i}]: неизвестное действие {name}; допустимо {sorted(specs)}.")
                continue
            spec = specs[name]
            if not isinstance(body, dict):
                body = {"target": body} if "target" in spec else {"value": body}
            if "target" in spec:
                target = body.get("target")
                allowed = {c.strip() for c in spec["target"][spec["target"].index("(") + 1:-1].split(",")}
                if target not in self._known_ids:
                    err("RULE_BROKEN_TARGET", f"then[{i}].{name}: цель {target} не существует.")
                elif self._cards_by_id[target].category not in allowed:
                    err("RULE_TARGET_CATEGORY", f"then[{i}].{name}: {target} имеет категорию {self._cards_by_id[target].category}, ожидается {sorted(allowed)}.")
            if "value" in spec:
                value = body.get("value")
                vspec = spec["value"]
                if vspec.startswith("enum(") and str(value) not in set(map(str, self.schema.enum(vspec[5:-1]))):
                    err("RULE_BAD_VALUE", f"then[{i}].{name}: значение {value!r} не входит в {vspec}.")
                elif vspec == "string" and not (isinstance(value, str) and value.strip()):
                    err("RULE_BAD_VALUE", f"then[{i}].{name}: ожидается непустая строка.")
            for key, extra_spec in (spec.get("extra") or {}).items():
                if key in body and str(extra_spec).startswith("enum(") and str(body[key]) not in set(map(str, self.schema.enum(extra_spec[5:-1]))):
                    err("RULE_BAD_VALUE", f"then[{i}].{name}.{key}: значение {body[key]!r} не входит в {extra_spec}.")

    # ----------------------------------------------------------- показатели
    def _collect_stats(self, report: ValidationReport) -> None:
        cards = self.repository.cards
        total = len(cards) or 1
        v2 = sum(1 for c in cards if c.schema_version >= 2)
        approved = sum(1 for c in cards if c.status == "approved")
        reviewed = sum(1 for c in cards if str(c.metadata.get("medical_reviewer", "")).strip() not in EMPTY_REVIEWER_VALUES)
        stubs = len({i.card_id for i in report.issues if i.code == "STUB_CARD"})
        orphans = len({i.card_id for i in report.issues if i.code == "ORPHAN"})
        machine_ready = 0
        for c in cards:
            required = self.schema.machine_required_for_approved(c.category)
            if required and all(c.metadata.get(f) not in (None, [], {}, "") for f in required):
                machine_ready += 1
        report.stats = {
            "карточек схемы v2": f"{v2} из {len(cards)}",
            "с заполненным машиночитаемым слоем": f"{machine_ready} из {len(cards)}",
            "в статусе approved": f"{approved} ({approved * 100 // total}%)",
            "с указанным рецензентом": f"{reviewed} ({reviewed * 100 // total}%)",
            "заглушек": stubs,
            "сирот (без входящих связей)": orphans,
            "правил": report.total_rules,
        }

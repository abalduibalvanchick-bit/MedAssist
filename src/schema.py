"""Загрузчик схемы базы знаний (kb/_schema/schema.yaml).

Схема — единственный источник правды о структуре базы знаний. Этот модуль
читает её один раз и предоставляет типизированный доступ остальным
компонентам. Никакие константы предметной структуры (домены, категории,
перечисления, типы связей) не должны дублироваться в коде.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

SCHEMA_RELATIVE_PATH = Path("kb") / "_schema" / "schema.yaml"


class SchemaError(Exception):
    """Ошибка структуры самой схемы."""


@dataclass(frozen=True)
class RelationType:
    name: str
    inverse: str | None
    symmetric: bool
    from_categories: tuple[str, ...]
    to_categories: tuple[str, ...]

    def inverse_name(self) -> str | None:
        if self.symmetric:
            return self.name
        return self.inverse


@dataclass(frozen=True)
class CategoryInfo:
    name: str
    domain: str
    folder: str
    title: str


@dataclass
class Schema:
    """Объектное представление schema.yaml."""

    raw: dict[str, Any]
    path: Path

    # --- базовые сведения ---------------------------------------------------
    @property
    def version(self) -> int:
        return int(self.raw.get("schema_version", 1))

    @property
    def domains(self) -> dict[str, dict[str, Any]]:
        return self.raw["domains"]

    @property
    def domain_codes(self) -> set[str]:
        return set(self.domains)

    @property
    def legacy_domain_aliases(self) -> dict[str, str]:
        return dict(self.raw.get("legacy_domain_aliases", {}))

    def normalize_domain(self, value: str) -> str:
        """Приводит устаревший код домена к каноническому."""
        value = (value or "").strip()
        if value in self.domains:
            return value
        return self.legacy_domain_aliases.get(value, value)

    def domain_for_id_prefix(self, prefix: str) -> str | None:
        for code, info in self.domains.items():
            if info.get("id_prefix") == prefix:
                return code
        return None

    # --- категории ----------------------------------------------------------
    @property
    def categories(self) -> dict[str, CategoryInfo]:
        return {
            name: CategoryInfo(name=name, domain=info["domain"], folder=info["folder"], title=info.get("title", name))
            for name, info in self.raw["categories"].items()
        }

    @property
    def legacy_category_aliases(self) -> dict[str, str]:
        return dict(self.raw.get("legacy_category_aliases", {}))

    def normalize_category(self, value: str) -> str:
        value = (value or "").strip()
        if value in self.raw["categories"]:
            return value
        return self.legacy_category_aliases.get(value, value)

    def categories_of_domain(self, domain: str) -> set[str]:
        return {name for name, info in self.categories.items() if info.domain == domain}

    def folder_category_rules(self) -> dict[str, str]:
        """Соответствие подпапки категории (для проверки расположения файла)."""
        return {info.folder: name for name, info in self.categories.items()}

    # --- идентификаторы -----------------------------------------------------
    @property
    def id_pattern(self) -> re.Pattern[str]:
        return re.compile(self.raw["identifiers"]["id_pattern"])

    @property
    def file_pattern(self) -> re.Pattern[str]:
        return re.compile(self.raw["identifiers"]["file_pattern"])

    @property
    def rule_id_pattern(self) -> re.Pattern[str]:
        return re.compile(self.raw["identifiers"]["rule_id_pattern"])

    # --- перечисления -------------------------------------------------------
    def enum(self, name: str) -> list[Any]:
        try:
            return list(self.raw["enums"][name])
        except KeyError as exc:
            raise SchemaError(f"В схеме нет перечисления {name}") from exc

    def enum_names(self) -> set[str]:
        return set(self.raw["enums"])

    @property
    def model_review_marker(self) -> str:
        return str(self.raw.get("model_review_marker", ""))

    # --- поля ---------------------------------------------------------------
    @property
    def common_required(self) -> list[str]:
        return list(self.raw["fields"]["common_required"])

    @property
    def common_optional(self) -> list[str]:
        return list(self.raw["fields"].get("common_optional", []))

    @property
    def removed_in_v2(self) -> list[str]:
        return list(self.raw["fields"].get("removed_in_v2", []))

    @property
    def min_sources(self) -> int:
        return int(self.raw["fields"].get("min_sources", 1))

    @property
    def date_pattern(self) -> re.Pattern[str]:
        return re.compile(self.raw["fields"]["date_pattern"])

    @property
    def approved_requires_machine_layer(self) -> bool:
        return bool(self.raw["fields"].get("approved_requires_machine_layer", False))

    # --- связи --------------------------------------------------------------
    @property
    def relation_types(self) -> dict[str, RelationType]:
        result: dict[str, RelationType] = {}
        for name, info in self.raw["relation_types"].items():
            info = info or {}
            result[name] = RelationType(
                name=name,
                inverse=info.get("inverse"),
                symmetric=bool(info.get("symmetric", False)),
                from_categories=tuple(info.get("from", []) or []),
                to_categories=tuple(info.get("to", []) or []),
            )
        return result

    @property
    def legacy_relation_aliases(self) -> dict[str, dict[str, Any]]:
        return dict(self.raw.get("legacy_relation_aliases", {}))

    def normalize_relation_type(self, value: str) -> str:
        value = (value or "").strip()
        if value in self.raw["relation_types"]:
            return value
        alias = self.legacy_relation_aliases.get(value)
        return alias["type"] if alias else value

    def inverse_relation(self, relation_type: str) -> str | None:
        info = self.relation_types.get(relation_type)
        return info.inverse_name() if info else None

    # --- параметры, факты, язык условий -------------------------------------
    @property
    def parameters(self) -> dict[str, dict[str, Any]]:
        return dict(self.raw.get("parameters", {}))

    @property
    def facts(self) -> dict[str, dict[str, Any]]:
        return dict(self.raw.get("facts", {}))

    @property
    def condition_atoms(self) -> list[str]:
        return list(self.raw["condition_language"]["atoms"])

    @property
    def condition_combinators(self) -> list[str]:
        return list(self.raw["condition_language"]["combinators"])

    @property
    def condition_operators(self) -> list[str]:
        return list(self.raw["condition_language"]["operators"])

    # --- машиночитаемый слой ------------------------------------------------
    def machine_layer(self, category: str) -> dict[str, Any]:
        return dict(self.raw.get("machine_layer", {}).get(category, {}) or {})

    def machine_fields(self, category: str) -> dict[str, Any]:
        return dict(self.machine_layer(category).get("fields", {}) or {})

    def machine_required_for_approved(self, category: str) -> list[str]:
        return list(self.machine_layer(category).get("required_for_approved", []) or [])

    # --- правила ------------------------------------------------------------
    @property
    def rule_required(self) -> list[str]:
        return list(self.raw["rules"]["required"])

    @property
    def rule_optional(self) -> list[str]:
        return list(self.raw["rules"].get("optional", []))

    @property
    def rule_actions(self) -> dict[str, dict[str, Any]]:
        return dict(self.raw["rules"]["actions"])

    @property
    def rule_default_priority(self) -> int:
        return int(self.raw["rules"].get("default_priority", 50))

    # --- самопроверка -------------------------------------------------------
    def self_check(self) -> list[str]:
        """Проверяет внутреннюю согласованность схемы. Возвращает список проблем."""
        problems: list[str] = []
        cats = self.categories
        for name, info in cats.items():
            if info.domain not in self.domains:
                problems.append(f"Категория {name} ссылается на неизвестный домен {info.domain}")
        folders: dict[tuple[str, str], str] = {}
        for name, info in cats.items():
            key = (info.domain, info.folder)
            if key in folders:
                problems.append(f"Папка {info.folder} в домене {info.domain} назначена двум категориям: {folders[key]}, {name}")
            folders[key] = name
        rel = self.relation_types
        for name, info in rel.items():
            if info.symmetric:
                continue
            if not info.inverse:
                problems.append(f"Тип связи {name} не имеет обратного типа")
            elif info.inverse not in rel:
                problems.append(f"Обратный тип {info.inverse} для {name} не объявлен")
            elif rel[info.inverse].inverse != name and not rel[info.inverse].symmetric:
                problems.append(f"Обратные типы не согласованы: {name} -> {info.inverse} -> {rel[info.inverse].inverse}")
            for cat in info.from_categories + info.to_categories:
                if cat not in cats:
                    problems.append(f"Тип связи {name} ссылается на неизвестную категорию {cat}")
        for alias, target in self.legacy_relation_aliases.items():
            if target.get("type") not in rel:
                problems.append(f"legacy-связь {alias} указывает на неизвестный тип {target.get('type')}")
        for cat in self.raw.get("machine_layer", {}):
            if cat not in cats:
                problems.append(f"machine_layer описан для неизвестной категории {cat}")
        for name in self.enum_names():
            values = self.enum(name)
            if len(values) != len(set(map(str, values))):
                problems.append(f"Перечисление {name} содержит дубликаты")
        return problems


def find_project_root(start: Path | None = None) -> Path:
    """Ищет корень проекта (папку, содержащую kb/_schema/schema.yaml)."""
    current = (start or Path(__file__).resolve().parent).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / SCHEMA_RELATIVE_PATH).exists():
            return candidate
    raise SchemaError(f"Не найден файл схемы {SCHEMA_RELATIVE_PATH} относительно {current}")


@lru_cache(maxsize=4)
def load_schema(path: Path | str | None = None) -> Schema:
    """Загружает схему. Результат кэшируется по пути."""
    schema_path = Path(path) if path else find_project_root() / SCHEMA_RELATIVE_PATH
    try:
        raw = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SchemaError(f"Файл схемы не найден: {schema_path}") from exc
    except yaml.YAMLError as exc:
        raise SchemaError(f"Ошибка YAML в схеме {schema_path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise SchemaError("Схема должна быть словарём верхнего уровня")
    schema = Schema(raw=raw, path=schema_path)
    problems = schema.self_check()
    if problems:
        raise SchemaError("Схема внутренне несогласована:\n  - " + "\n  - ".join(problems))
    return schema

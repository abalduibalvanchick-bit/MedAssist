"""Модели данных MVP MedAssist."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def normalize_text(value: str) -> str:
    """Нормализует строку для простого поиска.

    Учитывается русская буква ё, регистр и лишние пробелы.
    Это не полнотекстовый поисковый движок, а простой механизм для MVP.
    """

    return " ".join(value.lower().replace("ё", "е").split())


@dataclass(frozen=True)
class KnowledgeCard:
    """Одна единица знаний из Markdown-файла.

    Карточка содержит служебные YAML-метаданные, основной Markdown-текст
    и путь к исходному файлу. Остальные свойства являются удобными
    обёртками над metadata.
    """

    metadata: dict[str, Any]
    content: str
    file_path: Path

    @property
    def id(self) -> str:
        return str(self.metadata.get("id", "")).strip()

    @property
    def title(self) -> str:
        return str(self.metadata.get("title", "")).strip()

    @property
    def domain(self) -> str:
        return str(self.metadata.get("domain", "")).strip()

    @property
    def category(self) -> str:
        return str(self.metadata.get("category", "")).strip()

    @property
    def urgency(self) -> str:
        return str(self.metadata.get("urgency", "")).strip()

    @property
    def tags(self) -> list[str]:
        tags = self.metadata.get("tags", [])
        if isinstance(tags, list):
            return [str(tag).strip() for tag in tags]
        return []

    @property
    def schema_version(self) -> int:
        """Версия схемы карточки. Карточки без поля считаются схемой v1."""
        try:
            return int(self.metadata.get("schema_version", 1))
        except (TypeError, ValueError):
            return 1

    @property
    def related(self) -> list[str]:
        """Список ID связанных документов.

        В схеме v1 это отдельное поле related. В схеме v2 поле удалено и список
        вычисляется из relations, поэтому старый код навигации продолжает работать.
        """
        related = self.metadata.get("related")
        if isinstance(related, list):
            return [str(item).strip() for item in related if str(item).strip()]
        seen: list[str] = []
        for relation in self.relations:
            target = str(relation.get("target", "")).strip()
            if target and target not in seen:
                seen.append(target)
        return seen

    @property
    def status(self) -> str:
        return str(self.metadata.get("status", "")).strip()

    def machine_field(self, name: str, default: Any = None) -> Any:
        """Доступ к полю машиночитаемого слоя (схема v2)."""
        return self.metadata.get(name, default)

    @property
    def relations(self) -> list[dict[str, Any]]:
        relations = self.metadata.get("relations", [])
        if isinstance(relations, list):
            return [item for item in relations if isinstance(item, dict)]
        return []

    @property
    def short_description(self) -> str:
        return f"{self.id} — {self.title} [{self.category}, {self.urgency}]"

    def full_text_for_search(self) -> str:
        """Возвращает текст, по которому выполняется простой поиск."""

        parts = [
            self.id,
            self.title,
            self.domain,
            self.category,
            self.urgency,
            " ".join(self.tags),
            self.content,
        ]
        return normalize_text(" ".join(parts))


@dataclass(frozen=True)
class SearchResult:
    """Результат поиска с числовой оценкой релевантности."""

    card: KnowledgeCard
    score: int
    matched_by: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RelatedCard:
    """Результат разрешения связи между карточками."""

    source_id: str
    target_id: str
    relation_type: str
    description: str
    card: KnowledgeCard | None

    @property
    def is_missing(self) -> bool:
        return self.card is None

"""Репозиторий базы знаний: загрузка карточек из файловой системы."""

from __future__ import annotations

from pathlib import Path

from .config import EXCLUDED_DIR_NAMES, EXCLUDED_FILE_NAMES, KB_ROOT
from .indexer import KnowledgeIndex, build_index
from .markdown_parser import MarkdownParseError, parse_markdown_file
from .models import KnowledgeCard


class KnowledgeRepository:
    """Загружает карточки базы знаний и предоставляет доступ к индексам."""

    def __init__(self, kb_root: Path | str = KB_ROOT) -> None:
        self.kb_root = Path(kb_root)
        self.cards: list[KnowledgeCard] = []
        self.parse_errors: list[str] = []
        self.index: KnowledgeIndex = KnowledgeIndex()

    def load(self) -> "KnowledgeRepository":
        """Загружает все Markdown-карточки из kb_root."""

        self.cards = []
        self.parse_errors = []

        if not self.kb_root.exists():
            raise FileNotFoundError(f"Каталог базы знаний не найден: {self.kb_root}")

        for file_path in sorted(self.kb_root.rglob("*.md")):
            if self._should_skip(file_path):
                continue

            try:
                card = parse_markdown_file(file_path)
            except MarkdownParseError as exc:
                self.parse_errors.append(str(exc))
                continue

            self.cards.append(card)

        self.index = build_index(self.cards)
        return self

    def _should_skip(self, file_path: Path) -> bool:
        """Определяет, является ли Markdown-файл служебным."""

        if file_path.name in EXCLUDED_FILE_NAMES:
            return True
        relative_parts = file_path.relative_to(self.kb_root).parts if file_path.is_relative_to(self.kb_root) else file_path.parts
        return any(part in EXCLUDED_DIR_NAMES for part in relative_parts)

    def get_by_id(self, card_id: str) -> KnowledgeCard | None:
        return self.index.by_id.get(card_id)

    def all_cards(self) -> list[KnowledgeCard]:
        return list(self.cards)

    def summary_by_domain(self) -> dict[str, int]:
        return {domain: len(cards) for domain, cards in sorted(self.index.by_domain.items())}

    def summary_by_category(self) -> dict[str, int]:
        return {category: len(cards) for category, cards in sorted(self.index.by_category.items())}

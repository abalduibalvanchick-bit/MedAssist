"""Парсер Markdown-файлов с YAML-метаданными."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import KnowledgeCard


class MarkdownParseError(Exception):
    """Ошибка разбора Markdown-карточки базы знаний."""


def split_front_matter(raw_text: str, file_path: Path) -> tuple[str, str]:
    """Отделяет YAML-блок от основного Markdown-текста.

    Ожидаемый формат файла:
    ---
    id: "..."
    title: "..."
    ---

    # Заголовок карточки
    ...
    """

    normalized = raw_text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise MarkdownParseError(f"В файле нет начального YAML-блока: {file_path}")

    parts = normalized.split("\n---\n", 1)
    if len(parts) != 2:
        raise MarkdownParseError(f"В файле не найден закрывающий разделитель YAML: {file_path}")

    yaml_text = parts[0].removeprefix("---\n")
    markdown_body = parts[1]
    return yaml_text, markdown_body


def parse_markdown_file(file_path: Path) -> KnowledgeCard:
    """Читает Markdown-файл и возвращает объект KnowledgeCard."""

    try:
        raw_text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise MarkdownParseError(f"Файл должен быть в UTF-8: {file_path}") from exc

    yaml_text, markdown_body = split_front_matter(raw_text, file_path)

    try:
        metadata = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError as exc:
        raise MarkdownParseError(f"Ошибка YAML в файле {file_path}: {exc}") from exc

    if not isinstance(metadata, dict):
        raise MarkdownParseError(f"YAML-блок должен быть словарём: {file_path}")

    return KnowledgeCard(metadata=metadata, content=markdown_body.strip(), file_path=file_path)

"""Полная пересборка производных артефактов базы знаний одной командой.

Запуск из корня проекта после любых правок карточек, правил или схемы:
    python scripts/rebuild_all.py

Порядок:
1. sync_relations      — связи, подразумеваемые машиночитаемым слоем;
2. sync_body_sources   — раздел «Источники» в тексте карточек из поля sources;
3. generate_templates  — шаблоны карточек из схемы;
4. generate_docs       — документация docs/ из схемы;
5. generate_indices    — индексы, каталоги, статистика, дерево проекта;
6. валидация с записью отчёта indices/validation_report.md.

Код возврата ненулевой, если валидатор нашёл ошибки.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import generate_docs  # noqa: E402
import generate_indices  # noqa: E402
import generate_templates  # noqa: E402
import sync_body_sources  # noqa: E402
import sync_relations  # noqa: E402
from src.repository import KnowledgeRepository  # noqa: E402
from src.validator import KnowledgeBaseValidator  # noqa: E402


def main() -> int:
    print("1/6 связи из машиночитаемого слоя");   sync_relations.main([])
    print("2/6 разделы «Источники»");               sync_body_sources.main([])
    print("3/6 шаблоны карточек");                  generate_templates.main()
    print("4/6 документация");                      generate_docs.main()
    print("5/6 индексы и статистика");              generate_indices.generate()
    print("6/6 валидация")
    repo = KnowledgeRepository(ROOT / "kb").load()
    report = KnowledgeBaseValidator(repo).validate()
    (ROOT / "indices" / "validation_report.md").write_text(report.to_markdown(), encoding="utf-8")
    warnings = sum(1 for i in report.issues if i.severity == "WARNING")
    print(f"Карточек: {report.total_cards}, правил: {report.total_rules}, ошибок: {len(report.errors)}, предупреждений: {warnings}")
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())

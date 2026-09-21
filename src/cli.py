"""Консольный интерфейс MVP MedAssist."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import KB_ROOT, PROJECT_ROOT
from .linker import Linker
from .repository import KnowledgeRepository
from .scenarios import ScenarioRunner
from .search_engine import SearchEngine
from .validator import KnowledgeBaseValidator


def build_repository(kb_root: Path | str = KB_ROOT) -> KnowledgeRepository:
    repository = KnowledgeRepository(kb_root)
    repository.load()
    return repository


def print_card(card) -> None:
    print(f"\n{card.id} — {card.title}")
    print(f"Категория: {card.category}")
    print(f"Домен: {card.domain}")
    print(f"Срочность: {card.urgency}")
    print(f"Теги: {', '.join(card.tags)}")
    print(f"Файл: {card.file_path}")


def print_statistics(repository: KnowledgeRepository) -> None:
    print("\nСтатистика базы знаний")
    print(f"Всего карточек: {len(repository.cards)}")
    print("\nПо доменам:")
    for domain, count in repository.summary_by_domain().items():
        print(f"  {domain}: {count}")
    print("\nПо категориям:")
    for category, count in repository.summary_by_category().items():
        print(f"  {category}: {count}")
    if repository.parse_errors:
        print("\nОшибки парсинга:")
        for error in repository.parse_errors:
            print(f"  - {error}")


def run_interactive(repository: KnowledgeRepository) -> None:
    search_engine = SearchEngine(repository)
    linker = Linker(repository)
    validator = KnowledgeBaseValidator(repository)
    scenarios = ScenarioRunner(repository)

    while True:
        print("\nMedAssist Knowledge Base MVP")
        print("1. Показать статистику базы знаний")
        print("2. Найти карточку")
        print("3. Показать карточку по ID")
        print("4. Показать связанные документы")
        print("5. Фильтр по категории")
        print("6. Фильтр по срочности")
        print("7. Проверить целостность базы знаний")
        print("8. Запустить демонстрационный сценарий")
        print("0. Выход")

        choice = input("Выберите пункт: ").strip()

        if choice == "0":
            print("Выход из MVP MedAssist.")
            return
        if choice == "1":
            print_statistics(repository)
        elif choice == "2":
            query = input("Введите запрос: ").strip()
            results = search_engine.search(query)
            if not results:
                print("Ничего не найдено.")
            for result in results:
                print(f"{result.card.short_description}; score={result.score}; найдено по: {', '.join(result.matched_by)}")
        elif choice == "3":
            card_id = input("Введите ID карточки: ").strip()
            card = repository.get_by_id(card_id)
            if card is None:
                print("Карточка не найдена.")
            else:
                print_card(card)
        elif choice == "4":
            card_id = input("Введите ID исходной карточки: ").strip()
            related = linker.get_all_links(card_id)
            if not related:
                print("Связанные документы не найдены или карточка отсутствует.")
            for item in related:
                if item.card is None:
                    print(f"{item.target_id} — отсутствует; тип связи: {item.relation_type}")
                else:
                    mark = " [обратная]" if item.description.startswith("Обратная связь") else ""
                    print(f"{item.card.short_description}; тип связи: {item.relation_type}{mark}")
        elif choice == "5":
            category = input("Введите категорию: ").strip()
            for card in search_engine.filter_by_category(category):
                print(card.short_description)
        elif choice == "6":
            urgency = input("Введите срочность: ").strip()
            for card in search_engine.filter_by_urgency(urgency):
                print(card.short_description)
        elif choice == "7":
            report = validator.validate()
            print(report.to_markdown())
        elif choice == "8":
            print("Доступные сценарии: chest_pain, headache, dyspnea, hypertension_protocol, hypertension_therapy, pharm_drug, drug_interaction, validation, all")
            name = input("Введите имя сценария: ").strip() or "all"
            print(scenarios.run(name))
        else:
            print("Неизвестный пункт меню.")


def run_cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="MedAssist Knowledge Base MVP")
    parser.add_argument("--kb-root", default=str(KB_ROOT), help="Путь к каталогу kb")
    parser.add_argument("--stats", action="store_true", help="Показать статистику и выйти")
    parser.add_argument("--validate", action="store_true", help="Проверить базу знаний и выйти")
    parser.add_argument("--write-validation-report", action="store_true", help="Записать отчёт в indices/validation_report.md")
    parser.add_argument("--search", help="Найти карточки по запросу")
    parser.add_argument("--show", help="Показать карточку по ID")
    parser.add_argument("--related", help="Показать связанные документы по ID")
    parser.add_argument("--scenario", choices=["chest_pain", "headache", "dyspnea", "hypertension_protocol", "hypertension_therapy", "pharm_drug", "drug_interaction", "validation", "all"], help="Запустить сценарий")

    args = parser.parse_args(argv)
    repository = build_repository(Path(args.kb_root))
    search_engine = SearchEngine(repository)
    linker = Linker(repository)
    validator = KnowledgeBaseValidator(repository)
    scenarios = ScenarioRunner(repository)

    if args.stats:
        print_statistics(repository)
        return

    if args.validate:
        print(validator.validate().to_markdown())
        return

    if args.write_validation_report:
        output_path = PROJECT_ROOT / "indices" / "validation_report.md"
        report = validator.save_report(output_path)
        print(report.to_markdown())
        print(f"\nОтчёт записан: {output_path}")
        return

    if args.search:
        for result in search_engine.search(args.search):
            print(f"{result.card.short_description}; score={result.score}; найдено по: {', '.join(result.matched_by)}")
        return

    if args.show:
        card = repository.get_by_id(args.show)
        if card is None:
            print("Карточка не найдена.")
        else:
            print_card(card)
        return

    if args.related:
        related = linker.get_all_links(args.related)
        for item in related:
            if item.card is None:
                print(f"{item.target_id} — отсутствует; тип связи: {item.relation_type}")
            else:
                mark = " [обратная]" if item.description.startswith("Обратная связь") else ""
                print(f"{item.card.short_description}; тип связи: {item.relation_type}{mark}")
        return

    if args.scenario:
        print(scenarios.run(args.scenario))
        return

    run_interactive(repository)

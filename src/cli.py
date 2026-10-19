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


def run_solver(args) -> None:
    import json

    import yaml

    from .solver import load_default_kb, solve
    from .solver.report import format_solution

    try:
        request = yaml.safe_load(Path(args.solve).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"Не удалось прочитать файл задачи: {exc}")
        return
    kb = load_default_kb(str(Path(args.kb_root)))
    if args.dialog:
        run_dialog_console(request, args, kb)
        return
    solution = solve(request, role=args.role, kb=kb, include_trace=not args.no_trace)
    if args.json:
        print(json.dumps(solution, ensure_ascii=False, indent=2))
    else:
        print(format_solution(solution, show_trace=not args.no_trace))


def _ask_console(item: dict) -> str | None:
    """Задаёт один вопрос в консоли. Пустой ввод — значение неизвестно."""
    hint = {"boolean": "да/нет", "number": "число"}.get(item["type"], "")
    if item["type"] == "number" and item.get("unit"):
        hint = f"число, {item['unit']}"
    if item["type"] == "choice":
        for i, option in enumerate(item["options"], start=1):
            print(f"      {i}. {option['label']}")
        hint = "номер варианта"
    label = item["label"]
    if item["kind"] == "feature" and item.get("symptom_title"):
        label = item["label"][0].upper() + item["label"][1:]
    try:
        answer = input(f"  ? {label} ({hint}, Enter — неизвестно): ").strip()
    except EOFError:
        return None
    return answer or None


def run_dialog_console(request, args, kb) -> None:
    """Консольный уточняющий диалог: вопросы решателя → ответы → повторное решение."""
    from .solver.dialog import run_dialog
    from .solver.report import format_solution

    def ask(item: dict) -> str | None:
        return _ask_console(item)

    first = True

    def ask_with_header(item: dict) -> str | None:
        nonlocal first
        if first:
            print("\nРешателю не хватает данных. Ответьте на вопросы (Enter — пропустить).")
            first = False
        return ask(item)

    result = run_dialog(request, ask_with_header, role=args.role, kb=kb)
    for issue in result.issues:
        print(f"  [{issue['severity']}] {issue['message']}")
    if result.rounds:
        print(f"\nРаундов уточнения: {len(result.rounds)}")
    print()
    print(format_solution(result.solution, show_trace=not args.no_trace))


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

    parser.add_argument("--solve", metavar="FILE", help="Решить задачу для пациента из YAML/JSON-файла")
    parser.add_argument("--role", default="professional", help="Роль пользователя: professional, nursing, student, patient")
    parser.add_argument("--json", action="store_true", help="Вывести решение в JSON")
    parser.add_argument("--no-trace", action="store_true", help="Не показывать ход вывода")
    parser.add_argument("--dialog", action="store_true", help="Вместе с --solve: уточняющий диалог в консоли")

    args = parser.parse_args(argv)
    if args.solve:
        run_solver(args)
        return
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

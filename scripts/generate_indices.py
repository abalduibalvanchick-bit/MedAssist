"""Генерирует индексы, каталоги и статистику базы знаний из самих карточек.

Запуск из корня проекта:
    python scripts/generate_indices.py

Создаёт/перезаписывает:
    kb/<domain>/index.md                 — все карточки домена
    kb/<domain>/<category>/index.md      — карточки категории со связями
    indices/<domain>_catalog.md          — каталог домена
    indices/statistics.md                — сводная статистика (для пояснительной записки)
    PROJECT_TREE.txt                     — дерево проекта

Ручное редактирование этих файлов не предусмотрено: при следующем запуске
они будут перезаписаны. Устаревшие каталоги схемы v1 удаляются.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.repository import KnowledgeRepository  # noqa: E402
from src.schema import load_schema  # noqa: E402

KB = ROOT / "kb"
INDICES = ROOT / "indices"
HEADER = "<!-- Сгенерировано scripts/generate_indices.py. Не редактировать вручную. -->\n\n"
LEGACY_CATALOGS = ["diagnostics_catalog.md", "therapy_catalog.md", "protocols_catalog.md"]
TREE_EXCLUDE = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", ".idea", ".vscode"}


def esc(text: str) -> str:
    return str(text).replace("|", "\\|")


def card_table(cards, base: Path, with_relations: bool = False) -> str:
    headers = ["ID", "Название", "Категория", "Срочность", "Статус", "Файл"]
    if with_relations:
        headers.insert(5, "Связей")
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for c in sorted(cards, key=lambda x: x.id):
        rel = c.file_path.relative_to(base).as_posix()
        row = [f"`{c.id}`", esc(c.title), f"`{c.category}`", f"`{c.urgency}`", f"`{c.status}`"]
        if with_relations:
            row.append(str(len(c.relations)))
        row.append(f"[{rel}]({rel})")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def generate(kb: Path = KB) -> dict[str, int]:
    schema = load_schema(kb / "_schema" / "schema.yaml")
    repo = KnowledgeRepository(kb).load()
    cards = repo.cards
    by_domain = defaultdict(list)
    by_cat = defaultdict(list)
    for c in cards:
        by_domain[c.domain].append(c)
        by_cat[(c.domain, c.category)].append(c)
    written = 0

    for domain, info in schema.domains.items():
        dom_dir = kb / info["folder"]
        dom_dir.mkdir(parents=True, exist_ok=True)
        dcards = by_domain.get(domain, [])
        text = [HEADER, f"# {info['title']}\n\n",
                f"Домен `{domain}`, префикс идентификаторов `{info['id_prefix']}`. Карточек: **{len(dcards)}**.\n\n"]
        counts = Counter(c.category for c in dcards)
        if counts:
            text.append("| Категория | Название | Карточек |\n|---|---|---|\n")
            for cat in sorted(schema.categories_of_domain(domain)):
                if counts.get(cat):
                    text.append(f"| [`{cat}`]({schema.categories[cat].folder}/index.md) | {schema.categories[cat].title} | {counts[cat]} |\n")
            text.append("\n## Все карточки\n\n")
            text.append(card_table(dcards, dom_dir))
        else:
            text.append("Карточки домена ещё не созданы.\n")
        (dom_dir / "index.md").write_text("".join(text), encoding="utf-8")
        written += 1

        for cat in sorted(schema.categories_of_domain(domain)):
            ccards = by_cat.get((domain, cat), [])
            if not ccards:
                continue
            cat_info = schema.categories[cat]
            cat_dir = dom_dir / cat_info.folder
            required = schema.machine_required_for_approved(cat)
            ready = sum(1 for c in ccards if required and all(c.metadata.get(f) not in (None, [], {}, "") for f in required))
            body = [HEADER, f"# {cat_info.title}\n\n",
                    f"Категория `{cat}` домена `{domain}`. Карточек: **{len(ccards)}**.",
                    f" С заполненным машиночитаемым слоем: **{ready}**.\n\n" if required else "\n\n",
                    card_table(ccards, cat_dir, with_relations=True)]
            (cat_dir / "index.md").write_text("".join(body), encoding="utf-8")
            written += 1

    # Каталоги и статистика.
    INDICES.mkdir(exist_ok=True)
    for legacy in LEGACY_CATALOGS:
        (INDICES / legacy).unlink(missing_ok=True)
    for domain, info in schema.domains.items():
        dcards = by_domain.get(domain, [])
        text = [HEADER, f"# Каталог: {info['title']}\n\n", f"Карточек: **{len(dcards)}**.\n\n"]
        text.append(card_table(dcards, ROOT) if dcards else "Карточки домена ещё не созданы.\n")
        (INDICES / f"{domain}_catalog.md").write_text("".join(text), encoding="utf-8")
        written += 1

    rel_types = Counter()
    cross = Counter()
    for c in cards:
        for r in c.relations:
            t = str(r.get("target", ""))
            rel_types[str(r.get("type", ""))] += 1
            target = repo.get_by_id(t)
            if target is not None and target.domain != c.domain:
                cross[(c.domain, target.domain)] += 1
    stats = [HEADER, "# Статистика базы знаний MedAssist\n\n",
             f"Всего карточек: **{len(cards)}**. Всего связей: **{sum(rel_types.values())}**, "
             f"из них междоменных: **{sum(cross.values())}**.\n\n",
             "## По доменам и категориям\n\n| Домен | Категория | Карточек |\n|---|---|---|\n"]
    for (domain, cat), cc in sorted(by_cat.items()):
        stats.append(f"| `{domain}` | `{cat}` | {len(cc)} |\n")
    stats.append("\n## Статусы\n\n| Статус | Карточек |\n|---|---|\n")
    for status, n in Counter(c.status for c in cards).most_common():
        stats.append(f"| `{status}` | {n} |\n")
    stats.append("\n## Типы связей\n\n| Тип | Количество |\n|---|---|\n")
    for t, n in rel_types.most_common():
        stats.append(f"| `{t}` | {n} |\n")
    stats.append("\n## Междоменные связи\n\n| Из домена | В домен | Количество |\n|---|---|---|\n")
    for (a, b), n in sorted(cross.items()):
        stats.append(f"| `{a}` | `{b}` | {n} |\n")
    (INDICES / "statistics.md").write_text("".join(stats), encoding="utf-8")
    written += 1

    # Дерево проекта.
    lines = [ROOT.name + "/"]

    def walk(path: Path, depth: int) -> None:
        entries = sorted(p for p in path.iterdir() if p.name not in TREE_EXCLUDE and not p.name.endswith(".pyc"))
        for p in sorted(entries, key=lambda x: (x.is_file(), x.name)):
            lines.append("    " * depth + p.name + ("/" if p.is_dir() else ""))
            if p.is_dir():
                walk(p, depth + 1)

    walk(ROOT, 1)
    (ROOT / "PROJECT_TREE.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    written += 1
    return {"files": written, "cards": len(cards)}


if __name__ == "__main__":
    result = generate()
    print(f"Сгенерировано файлов: {result['files']}, карточек в индексах: {result['cards']}")

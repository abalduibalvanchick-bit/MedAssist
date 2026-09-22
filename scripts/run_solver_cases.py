"""Прогон тестовых сценариев решателя с отчётом для пояснительной записки.

Запуск из корня проекта:
    python scripts/run_solver_cases.py [--repeat 20]

Результат: docs/solver_test_report.md — таблица по сценариям (ожидание,
факт, результат, медианное время решения) и сводка по группам.
"""

from __future__ import annotations

import argparse
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.solver import load_default_kb, solve  # noqa: E402
from tests.solver_cases import check_case, load_cases  # noqa: E402

GROUPS = {"typical": "типичные", "boundary": "граничные", "negative": "отрицательные"}


def expected_summary(exp: dict) -> str:
    parts = [f"статус {exp['status']}"] if "status" in exp else []
    if "urgency" in exp:
        parts.append(f"срочность {exp['urgency']}")
    if "hypotheses_top" in exp:
        parts.append(f"ведущая гипотеза {exp['hypotheses_top']}")
    for key in ("red_flags", "emergencies"):
        if exp.get(key):
            parts.append(", ".join(exp[key]))
    if exp.get("input_issues"):
        parts.append("замечания: " + ", ".join(exp["input_issues"]))
    return "; ".join(parts) or "см. сценарий"


def actual_summary(sol: dict) -> str:
    parts = [f"статус {sol.get('status')}"]
    if sol.get("urgency"):
        parts.append(f"срочность {sol['urgency']['level']}")
    if sol.get("hypotheses"):
        parts.append(f"ведущая гипотеза {sol['hypotheses'][0]['id']}")
    flags = [x["id"] for x in (sol.get("red_flags") or []) + (sol.get("emergencies") or [])]
    if flags:
        parts.append(", ".join(flags))
    if sol.get("input_issues"):
        parts.append("замечаний: " + str(len(sol["input_issues"])))
    return "; ".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeat", type=int, default=20)
    parser.add_argument("--out", default=str(ROOT / "docs" / "solver_test_report.md"))
    args = parser.parse_args(argv)
    t0 = time.perf_counter()
    kb = load_default_kb()
    load_ms = (time.perf_counter() - t0) * 1000
    rows, passed = [], {g: [0, 0] for g in GROUPS}
    for case in load_cases():
        request = {"patient": case.get("patient") or {}}
        solution = solve(request, role=case.get("role", "professional"), kb=kb)
        fails = check_case(case, solution)
        times = [solve(request, kb=kb, include_trace=False)["stats"]["time_ms"] for _ in range(args.repeat)]
        passed[case["group"]][1] += 1
        passed[case["group"]][0] += not fails
        rows.append((case["id"], GROUPS[case["group"]], case["title"], expected_summary(case.get("expect") or {}),
                     actual_summary(solution), "пройден" if not fails else "не пройден: " + "; ".join(fails),
                     statistics.median(times)))
    total_ok = sum(v[0] for v in passed.values())
    total = sum(v[1] for v in passed.values())
    lines = ["<!-- Сгенерировано scripts/run_solver_cases.py -->", "", "# Результаты тестирования решателя задач", "",
             f"Среда: Python {platform.python_version()}, {platform.system()} {platform.machine()}. "
             f"База знаний: {len(kb.cards)} карточек, {len(kb.rules)} правил, загрузка {load_ms:.0f} мс. "
             f"Время решения — медиана по {args.repeat} запускам.", "",
             f"Пройдено **{total_ok} из {total}** сценариев.", "",
             "| Группа | Пройдено |", "|---|---|"]
    lines += [f"| {GROUPS[g]} | {v[0]} из {v[1]} |" for g, v in passed.items()]
    lines += ["", "| ID | Группа | Сценарий | Ожидаемый результат | Фактический результат | Итог | Время, мс |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]:.2f} |" for r in rows]
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Пройдено {total_ok} из {total}. Отчёт: {args.out}")
    return 0 if total_ok == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

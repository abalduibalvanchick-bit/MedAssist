"""Проверка тестовых сценариев решателя (tests/cases/*.yaml).

Каждый сценарий содержит постановку задачи (patient), ожидаемый результат
(expect) и, по возможности, ожидаемые шаги трассы. Поддерживаемые проверки:

    status, urgency                   — точное совпадение
    red_flags, emergencies, profiles,
    working_diagnoses, exams,
    protocols, rules_fired            — ожидаемые элементы присутствуют
    rules_not_fired, no_scales        — элементы отсутствуют
    no_red_flags, no_emergencies,
    no_hypotheses                     — список пуст
    hypotheses_top                    — гипотеза с наибольшим весом
    scales: {ID: {value, category}}   — значение и категория шкалы
    warnings_from, questions_from     — источники предупреждений и вопросов
    questions_kinds, question_asks    — виды вопросов, фрагменты запрашиваемых данных
    input_issues                      — коды замечаний к входным данным
    trace_order                       — источники встречаются в трассе в этом порядке
    max_time_ms                       — ограничение времени решения (по умолчанию 200 мс)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CASES_DIR = Path(__file__).resolve().parent / "cases"
DEFAULT_MAX_TIME_MS = 200


def load_cases() -> list[dict[str, Any]]:
    return [yaml.safe_load(p.read_text(encoding="utf-8")) | {"file": p.name} for p in sorted(CASES_DIR.glob("*.yaml"))]


def _ids(items: list[dict[str, Any]] | None) -> list[str]:
    return [i["id"] for i in items or []]


def check_case(case: dict[str, Any], solution: dict[str, Any]) -> list[str]:
    """Возвращает список расхождений (пустой — тест пройден)."""
    exp = case.get("expect") or {}
    fails: list[str] = []

    def need(cond: bool, msg: str) -> None:
        if not cond:
            fails.append(msg)

    if "status" in exp:
        need(solution.get("status") == exp["status"], f"статус {solution.get('status')!r}, ожидался {exp['status']!r}")
    if "urgency" in exp:
        actual = (solution.get("urgency") or {}).get("level")
        need(actual == exp["urgency"], f"срочность {actual!r}, ожидалась {exp['urgency']!r}")
    for key in ("red_flags", "emergencies", "profiles", "working_diagnoses", "exams", "protocols"):
        missing = set(exp.get(key) or []) - set(_ids(solution.get(key)))
        need(not missing, f"{key}: нет {sorted(missing)}")
    fired = set(solution.get("fired_rules") or [])
    missing = set(exp.get("rules_fired") or []) - fired
    need(not missing, f"не сработали правила {sorted(missing)}")
    extra = set(exp.get("rules_not_fired") or []) & fired
    need(not extra, f"сработали лишние правила {sorted(extra)}")
    for key in ("red_flags", "emergencies", "hypotheses"):
        if exp.get(f"no_{key}"):
            need(not solution.get(key), f"{key} должен быть пуст, получено {_ids(solution.get(key))}")
    if "hypotheses_top" in exp:
        hyps = solution.get("hypotheses") or []
        need(bool(hyps) and hyps[0]["id"] == exp["hypotheses_top"],
             f"ведущая гипотеза {hyps[0]['id'] if hyps else None}, ожидалась {exp['hypotheses_top']}")
    scales = {s["id"]: s for s in solution.get("scales") or []}
    for sid, spec in (exp.get("scales") or {}).items():
        actual = scales.get(sid)
        if actual is None:
            fails.append(f"шкала {sid} не вычислена")
            continue
        if "value" in spec:
            need(actual.get("value") == spec["value"], f"{sid}: значение {actual.get('value')}, ожидалось {spec['value']}")
        if "category" in spec:
            need(actual.get("category") == spec["category"], f"{sid}: категория {actual.get('category')}, ожидалась {spec['category']}")
    for sid in exp.get("no_scales") or []:
        need(sid not in scales, f"шкала {sid} не должна быть определена")
    sources = {w["source"] for w in solution.get("warnings") or []}
    missing = set(exp.get("warnings_from") or []) - sources
    need(not missing, f"нет предупреждений от {sorted(missing)}")
    questions = solution.get("questions") or []
    missing = set(exp.get("questions_from") or []) - {q["source"] for q in questions}
    need(not missing, f"нет вопросов от {sorted(missing)}")
    missing = set(exp.get("questions_kinds") or []) - {q["kind"] for q in questions}
    need(not missing, f"нет вопросов вида {sorted(missing)}")
    asked = " | ".join(a for q in questions for a in q.get("ask") or [])
    for fragment in exp.get("question_asks") or []:
        need(fragment in asked, f"не запрошено «{fragment}»")
    codes = {i["code"] for i in solution.get("input_issues") or []}
    missing = set(exp.get("input_issues") or []) - codes
    need(not missing, f"нет замечаний к входу {sorted(missing)}")
    order = exp.get("trace_order") or []
    if order:
        trace_sources = [s["source"] for s in solution.get("trace") or []]
        positions = [trace_sources.index(s) if s in trace_sources else -1 for s in order]
        need(-1 not in positions and positions == sorted(positions), f"порядок в трассе {positions} для {order}")
    limit = exp.get("max_time_ms", DEFAULT_MAX_TIME_MS)
    elapsed = (solution.get("stats") or {}).get("time_ms", 0)
    need(elapsed <= limit, f"время {elapsed} мс больше {limit} мс")
    return fails

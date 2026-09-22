"""Интерфейс решателя задач MedAssist.

Единственная точка входа для консоли, тестов и будущего пользовательского
интерфейса (6 семестр):

    from src.solver import solve
    solution = solve({"patient": {...}}, role="professional")

Решение — словарь из простых типов (сериализуется в JSON без преобразований).
Поля решения:

    status          ok | need_more_data | refused | invalid
    urgency         срочность и её основания
    profiles, red_flags, emergencies, scales, hypotheses, working_diagnoses
    exams, routes, protocols, warnings, questions
    refusal, input_issues, disclaimer, explanation, trace, stats

Роль пользователя (access_level из схемы) определяет состав ответа: пациенту
не показываются гипотезы с весами, обследования и фармакологические
предупреждения; вместо них выводятся тревожные признаки из памяток.
"""

from __future__ import annotations

import time
from typing import Any

from .engine import URGENCY_LABELS, InferenceEngine
from .explain import render_explanation
from .facts import parse_case
from .knowledge import KnowledgeBase, load_default_kb
from .questions import build_questions

ROLES = ("professional", "nursing", "student", "patient")


def _card_ref(kb: KnowledgeBase, card_id: str, **extra: Any) -> dict[str, Any]:
    return {"id": card_id, "title": kb.title(card_id), **extra}


def _disclaimers(kb: KnowledgeBase, role: str, urgency: str) -> list[str]:
    texts = []
    for card in kb.category("disclaimer"):
        levels = card.metadata.get("applies_to_access_level") or []
        if card.urgency == "emergency":
            if urgency == "emergency":
                texts.insert(0, str(card.metadata.get("text", "")))
        elif role in levels:
            texts.append(str(card.metadata.get("text", "")))
    return texts


def _patient_advice(kb: KnowledgeBase, diagnoses: list[str]) -> list[dict[str, Any]]:
    advice = []
    for card in kb.category("patient_info"):
        if set(card.metadata.get("for") or []) & set(diagnoses):
            advice.append({"id": card.id, "title": card.title, "seek_help_when": list(card.metadata.get("seek_help_when") or [])})
    return advice


def solve(request: dict[str, Any], role: str = "professional", *, kb: KnowledgeBase | None = None,
          include_trace: bool = True) -> dict[str, Any]:
    """Решает задачу для описания пациента. Никогда не бросает исключений на плохих данных."""
    kb = kb or load_default_kb()          # загрузка базы не входит в замер времени решения
    started = time.perf_counter()
    if role not in ROLES:
        return {"status": "invalid", "input_issues": [{"severity": "error", "code": "BAD_ROLE",
                "message": f"Неизвестная роль «{role}»; допустимо: {', '.join(ROLES)}."}]}

    parsed = parse_case(request, kb)
    issues = [{"severity": i.severity, "code": i.code, "message": i.message} for i in parsed.issues]
    if parsed.has_errors:
        return {"status": "invalid", "role": role, "input_issues": issues,
                "disclaimer": _disclaimers(kb, role, "routine"),
                "stats": {"time_ms": round((time.perf_counter() - started) * 1000, 2)}}

    engine = InferenceEngine(kb)
    memory = engine.run(parsed.facts)
    questions = build_questions(memory, kb) if memory.refusal is None else []

    hypotheses = sorted(memory.hypotheses.values(), key=lambda h: (-h.score, h.target))
    concluded = bool(memory.facts.red_flags or memory.facts.emergencies or hypotheses
                     or memory.routes or memory.protocols or memory.facts.diseases)
    if memory.refusal is not None:
        status = "refused"
    elif not concluded:
        status = "need_more_data"
    else:
        status = "ok"

    solution: dict[str, Any] = {
        "status": status,
        "role": role,
        "urgency": {"level": memory.urgency, "label": URGENCY_LABELS.get(memory.urgency, memory.urgency),
                    "reasons": [s for s in memory.urgency_sources if s["level"] == memory.urgency]},
        "profiles": [_card_ref(kb, p) for p in sorted(memory.facts.profiles)],
        "red_flags": [_card_ref(kb, r) for r in sorted(memory.facts.red_flags)],
        "emergencies": [_card_ref(kb, e) for e in sorted(memory.facts.emergencies)],
        "working_diagnoses": [_card_ref(kb, d) for d in memory.working_diagnoses],
        "hypotheses": [_card_ref(kb, h.target, score=h.score, sources=h.sources) for h in hypotheses],
        "scales": [
            {"id": sid, "title": r.title, "value": r.value, "range": [r.low, r.high], "category": r.category,
             "category_label": r.category_label, "action": r.action,
             "items": [{"code": i.code, "label": i.label, "points": i.points, "detail": i.detail} for i in r.items]}
            for sid, r in sorted(memory.scales.items()) if r.category is not None
        ],
        "exams": [_card_ref(kb, eid, roles=v["roles"], sources=v["sources"]) for eid, v in sorted(memory.exams.items())],
        "routes": memory.routes,
        "protocols": [_card_ref(kb, p["id"], source=p["source"]) for p in memory.protocols],
        "warnings": memory.warnings,
        "questions": questions,
        "refusal": memory.refusal,
        "input_issues": issues,
        "fired_rules": memory.fired_rules,
        "disclaimer": _disclaimers(kb, role, memory.urgency),
        "explanation": render_explanation(memory, kb),
        "trace": [step.as_dict() for step in memory.trace] if include_trace else [],
        "stats": {"iterations": memory.iterations, "trace_steps": len(memory.trace),
                  "rules_fired": len(memory.fired_rules), "rules_total": len(kb.rules),
                  "time_ms": round((time.perf_counter() - started) * 1000, 2)},
    }

    if role == "patient":
        # Памятки — только по рабочим диагнозам: слабые гипотезы пациенту не показываются.
        solution["advice"] = _patient_advice(kb, memory.working_diagnoses)
        for key in ("hypotheses", "exams", "warnings", "scales", "fired_rules", "trace", "explanation", "protocols"):
            solution.pop(key, None)
    return solution

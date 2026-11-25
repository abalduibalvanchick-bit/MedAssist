"""Интерфейс решателя задач MedAssist.

Единственная точка входа для консоли, тестов и пользовательского
интерфейса:

    from src.solver import solve
    solution = solve({"patient": {...}}, role="professional")

Решение — словарь из простых типов (сериализуется в JSON без преобразований).
Поля решения:

    status          ok | need_more_data | refused | invalid
    urgency         срочность и её основания
    profiles, red_flags, emergencies, scales, hypotheses, working_diagnoses
    exams, deferred_exams, completed_exams, routing, routes, protocols, follow_up, warnings, questions
    refusal, input_issues, disclaimer, explanation, trace, stats

Роль пользователя (access_level из схемы) определяет состав ответа: пациенту
не показываются гипотезы с весами, обследования и фармакологические
предупреждения; вместо них выводятся тревожные признаки из памяток.
"""

from __future__ import annotations

import time
from typing import Any

from .differential import assess_differential
from .engine import URGENCY_LABELS, InferenceEngine
from .explain import render_explanation
from .facts import parse_case
from .knowledge import KnowledgeBase, known_exam_results, load_default_kb
from .questions import build_questions, detail_questions, rank_questions
from .protocols import execute_protocols
from .ranking import rank_hypotheses
from .routing import routing_to_dict, select_routes
from .therapy import assess_therapy

ROLES = ("professional", "nursing", "student", "patient")
_ROLE_ORDER = {"confirms": 0, "excludes": 1, "stratifies": 2, "supports": 3, "monitors": 4}
_REPEATABLE_FREE = {"excludes", "stratifies", "supports"}


def _card_ref(kb: KnowledgeBase, card_id: str, **extra: Any) -> dict[str, Any]:
    return {"id": card_id, "title": kb.title(card_id), **extra}


def _scale_relevant(kb: KnowledgeBase, scale_id: str, memory) -> bool:
    """Шкала показывается, если оценивает рабочий диагноз, гипотезу или неотложное состояние."""
    card = kb.get(scale_id)
    if card is None:
        return False
    targets = {str(r.get("target")) for r in card.relations}
    relevant = set(memory.working_diagnoses) | set(memory.hypotheses) | memory.facts.emergencies
    return bool(targets & relevant)


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
    routing = select_routes(memory, kb)          # T1: после неподвижной точки, до вопросов
    questions = build_questions(memory, kb) if memory.refusal is None else []
    questions.extend(routing.questions)
    hypotheses = rank_hypotheses(memory, kb)
    professional = role != "patient" and memory.refusal is None
    protocols, protocol_questions = execute_protocols(memory, routing, kb) if professional else ([], [])
    differential, differential_questions = assess_differential(memory, kb) if professional else ([], [])
    therapy, therapy_questions = assess_therapy(memory, kb) if professional else ({}, [])
    questions.extend(protocol_questions + differential_questions + therapy_questions)
    # Решение получено, если сделан хотя бы один вывод: распознано состояние, есть гипотеза,
    # маршрут, протокол, установленный диагноз, предупреждение или знание повысило срочность.
    raised = any(src["level"] in ("urgent", "emergency") for src in memory.urgency_sources)
    concluded = bool(memory.facts.red_flags or memory.facts.emergencies or hypotheses
                     or memory.routes or memory.protocols or memory.routing_refs or memory.facts.diseases
                     or memory.warnings or therapy.get("interactions") or raised)
    if memory.refusal is not None:
        status = "refused"
    elif not concluded:
        status = "need_more_data"
        if not questions:
            questions = detail_questions(memory, kb)
    else:
        status = "ok"

    if memory.refusal is None:
        questions = rank_questions(questions, memory, kb, include_hypotheses=professional)

    # Обследования: сначала подтверждающие и исключающие, затем оценка тяжести и прочие.
    # В экстренной ситуации обследования только из плановых правил (phase: planned)
    # выводятся отдельно — «после стабилизации», чтобы не смешиваться с неотложными.
    # Обследование, результат которого уже сообщён (поле measures карточки exam или
    # exam_results), не рекомендуется повторно, а выводится как выполненное. Исключение —
    # роли «подтверждение» и «контроль»: для них нужен повторный или динамический замер
    # (АД на двух визитах, тропонин в динамике).
    planned_rules = {r.id for r in kb.rules if r.phase == "planned"}
    exams, deferred_exams, completed_exams = [], [], []
    for eid, v in sorted(memory.exams.items(), key=lambda kv: (min(_ROLE_ORDER.get(r, 9) for r in kv[1]["roles"]), kv[0])):
        ref = _card_ref(kb, eid, roles=v["roles"], sources=v["sources"])
        known = known_exam_results(kb, eid, memory.facts)
        if known and set(v["roles"]) <= _REPEATABLE_FREE:
            completed_exams.append({**ref, "results": known})
        elif memory.urgency == "emergency" and set(v["sources"]) <= planned_rules:
            deferred_exams.append(ref)
        else:
            exams.append(ref)

    solution: dict[str, Any] = {
        "status": status,
        "role": role,
        "urgency": {"level": memory.urgency, "label": URGENCY_LABELS.get(memory.urgency, memory.urgency),
                    "reasons": [s for s in memory.urgency_sources if s["level"] == memory.urgency]},
        "profiles": [_card_ref(kb, p) for p in sorted(memory.facts.profiles)],
        "red_flags": [_card_ref(kb, r) for r in sorted(memory.facts.red_flags)],
        "emergencies": [_card_ref(kb, e) for e in sorted(memory.facts.emergencies)],
        "working_diagnoses": [_card_ref(kb, d) for d in memory.working_diagnoses],
        "hypotheses": hypotheses,
        "differential": differential,
        "therapy": therapy,
        "scales": [
            {"id": sid, "title": r.title, "value": r.value, "range": [r.low, r.high], "category": r.category,
             "category_label": r.category_label, "action": r.action,
             "items": [{"code": i.code, "label": i.label, "points": i.points, "detail": i.detail} for i in r.items]}
            for sid, r in sorted(memory.scales.items())
            if r.category is not None and _scale_relevant(kb, sid, memory)
        ],
        "exams": exams,
        "deferred_exams": deferred_exams,
        "completed_exams": completed_exams,
        "routes": memory.routes,
        "protocols": [p for p in protocols if p["kind"] != "follow_up"],
        "follow_up": [p for p in protocols if p["kind"] == "follow_up"],
        "routing": routing_to_dict(routing, kb),
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
        # Пациенту — куда и когда обращаться, без служебных таблиц решений.
        solution["routing"] = {k: solution["routing"][k] for k in ("route", "label", "timeframe", "provisional")}
        # Памятки — только по рабочим диагнозам: слабые гипотезы пациенту не показываются.
        solution["advice"] = _patient_advice(kb, memory.working_diagnoses)
        for key in ("hypotheses", "differential", "therapy", "exams", "deferred_exams", "completed_exams", "warnings", "scales", "fired_rules", "trace", "explanation", "protocols", "follow_up"):
            solution.pop(key, None)
    return solution

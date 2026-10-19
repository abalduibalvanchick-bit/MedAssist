"""Маршрутизация пациента по таблицам решений карточек routing (задача T1).

Модуль работает после неподвижной точки прямого вывода: ему нужны итоговые
рабочие диагнозы, шкалы, профили и распознанные опасные состояния.

1. Активация. Карточка routing рассматривается, если её поле for пересекается
   с рабочими диагнозами, распознанными неотложными состояниями или сообщёнными
   симптомами, либо на неё передал управление красный флаг или неотложное
   состояние (поле action, см. Conclusions.routing_refs).

2. Выбор строки. Строки decisions упорядочены от тяжёлого маршрута к лёгкому
   (это проверяет валидатор) и оцениваются по порядку в трёхзначной логике:

       нерешённые := []
       для каждой строки:
           истинно    → выбрать строку, закончить
           неизвестно → нерешённые += строка
       ничего не выбрано → маршрут по умолчанию (default)
       предварительно := есть нерешённая строка тяжелее выбранной

   Предварительный маршрут не скрывает более тяжёлый вариант: решатель задаёт
   вопрос с полями ввода, ответ на который подтверждает или исключает его.

3. Итог. Итоговый маршрут — самый тяжёлый из маршрутов карточек и действий
   route правил. Маршрут повышает срочность по solver.route_urgency; экстренная
   срочность без экстренного маршрута даёт экстренный маршрут (solver.urgency_route).
   Следующие шаги выбранной строки (next: протокол, алгоритм неотложной помощи)
   добавляются в дальнейшие действия.

Все соответствия и подписи берутся из схемы (раздел solver), пороги — из карточек.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..conditions import ConditionRefs, Truth, evaluate
from .engine import raise_urgency, record_step
from .explain import justify
from .inputs import inputs_from_refs, label_of, missing_inputs_deep

if TYPE_CHECKING:  # pragma: no cover
    from .engine import Conclusions
    from .knowledge import KnowledgeBase

_DEFAULT_SEVERITY = ["outpatient", "urgent_referral", "hospitalization", "emergency"]
_NEXT_AS_ACTIONS = ("protocol", "emergency_p")


@dataclass
class RouteDecision:
    """Решение по одной карточке маршрутизации."""

    card_id: str
    title: str
    route: str
    timeframe: str
    actions: list[str]
    explanation: str
    row: int | None                      # номер строки decisions; None — маршрут по умолчанию
    next: list[str] = field(default_factory=list)
    because: list[str] = field(default_factory=list)
    activated_by: list[str] = field(default_factory=list)
    unresolved: list[dict[str, Any]] = field(default_factory=list)  # более тяжёлые строки с неизвестным условием

    @property
    def provisional(self) -> bool:
        return bool(self.unresolved)


@dataclass
class RoutingResult:
    route: str | None = None
    timeframe: str = ""
    sources: list[str] = field(default_factory=list)
    decisions: list[RouteDecision] = field(default_factory=list)
    questions: list[dict[str, Any]] = field(default_factory=list)

    severity: list[str] = field(default_factory=lambda: list(_DEFAULT_SEVERITY), repr=False)

    @property
    def provisional(self) -> bool:
        """Итог предварительный, если хотя бы одна карточка не исключила маршрут тяжелее итогового."""
        return any(_sev_index(self.severity, u["route"]) > _sev_index(self.severity, self.route)
                   for d in self.decisions for u in d.unresolved)


def _sev_index(order: list[str], route: str | None) -> int:
    return order.index(route) if route in order else -1


def _activation(card, memory: "Conclusions") -> list[str]:
    """Чем активирована карточка: пересечение for с выводами и явные передачи управления."""
    facts = memory.facts
    present = set(memory.working_diagnoses) | set(facts.diseases) | facts.emergencies | facts.symptoms
    reasons = [target for target in (card.metadata.get("for") or []) if target in present]
    reasons += [ref["source"] for ref in memory.routing_refs if ref["id"] == card.id]
    return list(dict.fromkeys(reasons))


def _decide(card, memory: "Conclusions", kb: "KnowledgeBase", severity: list[str]) -> RouteDecision:
    schema = kb.schema
    unresolved: list[dict[str, Any]] = []
    chosen: dict[str, Any] | None = None
    row: int | None = None
    for index, decision in enumerate(card.metadata.get("decisions") or []):
        truth = evaluate(decision["when"], memory.facts, schema)
        if truth is Truth.TRUE:
            chosen, row = decision, index
            break
        if truth is Truth.UNKNOWN:
            unresolved.append({"row": index, "route": decision["route"], "when": decision["when"]})
    if chosen is None:
        chosen = dict(card.metadata.get("default") or {})
        because = ["ни одно условие таблицы решений не выполнено — маршрут по умолчанию"]
    else:
        because = justify(chosen["when"], memory.facts, kb)
    heavier = [u for u in unresolved if _sev_index(severity, u["route"]) > _sev_index(severity, chosen.get("route"))]
    return RouteDecision(
        card_id=card.id, title=card.title, route=str(chosen.get("route")), timeframe=str(chosen.get("timeframe", "")),
        actions=list(chosen.get("actions") or []), explanation=str(chosen.get("explanation", "")), row=row,
        next=[str(n) for n in chosen.get("next") or []], because=because, unresolved=heavier,
    )


def select_routes(memory: "Conclusions", kb: "KnowledgeBase") -> RoutingResult:
    """Выбирает маршрут по таблицам решений; дописывает трассу, срочность и дальнейшие действия."""
    schema = kb.schema
    severity = list(schema.solver_setting("route_severity", _DEFAULT_SEVERITY))
    route_urgency = dict(schema.solver_setting("route_urgency", {}))
    labels = dict(schema.solver_setting("route_labels", {}))
    result = RoutingResult(severity=severity)
    if memory.refusal is not None:
        return result
    iteration = memory.iterations + 1

    for card in kb.category("routing"):
        reasons = _activation(card, memory)
        if not reasons:
            continue
        decision = _decide(card, memory, kb, severity)
        decision.activated_by = reasons
        result.decisions.append(decision)
        effects = [f"маршрут: {labels.get(decision.route, decision.route)}"
                   + (f", {decision.timeframe}" if decision.timeframe else "")]
        if decision.provisional:
            effects.append("предварительно: не исключены " + ", ".join(
                labels.get(u["route"], u["route"]) for u in decision.unresolved))
        for target in decision.next:
            next_card = kb.get(target)
            if next_card is not None and next_card.category in _NEXT_AS_ACTIONS \
                    and not any(p["id"] == target for p in memory.protocols):
                memory.protocols.append({"id": target, "source": card.id})
                effects.append(f"переход: {next_card.title}")
        record_step(memory, "routing", card.id, card.title, decision.because, effects, iteration)
        if decision.provisional:
            refs = ConditionRefs()
            for item in decision.unresolved:
                missing = missing_inputs_deep(item["when"], memory.facts, kb)
                refs.params |= missing.params
                refs.facts |= missing.facts
                refs.features |= missing.features
                refs.card_ids |= missing.card_ids
            inputs = inputs_from_refs(refs, kb)
            if inputs:
                worst = max(decision.unresolved, key=lambda u: _sev_index(severity, u["route"]))
                result.questions.append({
                    "kind": "routing", "source": card.id, "inputs": inputs, "ask": [label_of(i) for i in inputs],
                    "text": f"Чтобы исключить маршрут «{labels.get(worst['route'], worst['route'])}» "
                            f"({card.title.split(': ', 1)[-1]}), уточните данные.",
                })

    # Итоговый маршрут: самый тяжёлый из карточек и действий route правил.
    candidates = [(d.route, d.timeframe, d.card_id) for d in result.decisions]
    candidates += [(r["route"], r.get("timeframe", ""), r["source"]) for r in memory.routes]
    urgency_route = dict(schema.solver_setting("urgency_route", {})).get(memory.urgency)
    if urgency_route:
        reasons = [s["source"] for s in memory.urgency_sources if s["level"] == memory.urgency]
        candidates += [(urgency_route, "немедленно", reasons[0] if reasons else "urgency")]
    if candidates:
        top = max(_sev_index(severity, c[0]) for c in candidates)
        best = [c for c in candidates if _sev_index(severity, c[0]) == top]
        result.route = best[0][0]
        result.timeframe = next((c[1] for c in best if c[1]), "")
        result.sources = list(dict.fromkeys(c[2] for c in best))
        level = route_urgency.get(result.route)
        if level:
            effects: list[str] = []
            raise_urgency(memory, level, result.sources[0],
                          f"маршрут «{labels.get(result.route, result.route)}»", effects)
            if effects:
                record_step(memory, "routing", result.sources[0], "Итоговый маршрут",
                            [f"маршрут: {labels.get(result.route, result.route)}"], effects, iteration)
    return result


def routing_to_dict(result: RoutingResult, kb: "KnowledgeBase") -> dict[str, Any]:
    labels = dict(kb.schema.solver_setting("route_labels", {}))
    return {
        "route": result.route,
        "label": labels.get(result.route, result.route) if result.route else None,
        "timeframe": result.timeframe,
        "provisional": result.provisional,
        "sources": result.sources,
        "decisions": [{
            "id": d.card_id, "title": d.title, "route": d.route, "label": labels.get(d.route, d.route),
            "timeframe": d.timeframe, "row": d.row, "actions": d.actions, "explanation": d.explanation,
            "next": d.next, "activated_by": d.activated_by, "provisional": d.provisional,
            "unresolved": [{"row": u["row"], "route": u["route"], "label": labels.get(u["route"], u["route"])}
                           for u in d.unresolved],
        } for d in result.decisions],
    }

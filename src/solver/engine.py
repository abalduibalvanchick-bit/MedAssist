"""Машина прямого вывода решателя MedAssist.

Алгоритм — прямой (от фактов к заключениям) вывод до неподвижной точки:

    повторять, пока рабочая память меняется (не более MAX_ITERATIONS раз):
        1. профили пациента        ← условия criteria карточек profile
        2. шкалы                   ← параметры карточек scale (интервально)
        3. красные флаги           ← условия triggers карточек redflag
        4. неотложные состояния    ← условия criteria карточек emergency
        5. продукционные правила   ← kb/rules, по убыванию приоритета;
                                     каждое правило срабатывает не более
                                     одного раза (рефрактерность)
    правило refuse прекращает вывод (граница применимости).

Все знания берутся из базы знаний; в коде нет ни одного медицинского порога.
Каждое срабатывание записывается в трассу вместе с фактами-основаниями.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..conditions import PatientFacts, Truth, evaluate
from .explain import justify
from .knowledge import KnowledgeBase, Rule
from .scales import ScaleResult, compute_scale

MAX_ITERATIONS = 20
# Суммарный вес гипотезы-заболевания, начиная с которого она считается рабочим
# диагнозом и становится доступна условиям {disease: ...}. Параметр решателя,
# а не медицинское знание: веса задаются в базе знаний (правила, presentation).
WORKING_DIAGNOSIS_SCORE = 3
URGENCY_ORDER = ["elective", "routine", "urgent", "emergency"]
URGENCY_LABELS = {"elective": "отложенная", "routine": "плановая", "urgent": "срочная", "emergency": "экстренная"}


@dataclass
class TraceStep:
    step: int
    iteration: int
    kind: str            # profile | scale | redflag | emergency | rule | diagnosis
    source_id: str
    title: str
    because: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"step": self.step, "iteration": self.iteration, "kind": self.kind, "source": self.source_id,
                "title": self.title, "because": self.because, "effects": self.effects}


@dataclass
class Hypothesis:
    target: str
    score: int = 0
    sources: list[str] = field(default_factory=list)


@dataclass
class Conclusions:
    """Рабочая память и результаты вывода."""

    facts: PatientFacts
    urgency: str = "routine"
    urgency_sources: list[dict[str, str]] = field(default_factory=list)
    hypotheses: dict[str, Hypothesis] = field(default_factory=dict)
    working_diagnoses: list[str] = field(default_factory=list)
    scales: dict[str, ScaleResult] = field(default_factory=dict)
    exams: dict[str, dict[str, Any]] = field(default_factory=dict)
    routes: list[dict[str, str]] = field(default_factory=list)
    protocols: list[dict[str, str]] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)
    clarifications: list[dict[str, str]] = field(default_factory=list)
    refusal: dict[str, str] | None = None
    fired_rules: list[str] = field(default_factory=list)
    trace: list[TraceStep] = field(default_factory=list)
    iterations: int = 0


class InferenceEngine:
    def __init__(self, kb: KnowledgeBase, *, working_diagnosis_score: int = WORKING_DIAGNOSIS_SCORE,
                 max_iterations: int = MAX_ITERATIONS) -> None:
        self.kb = kb
        self.schema = kb.schema
        self.working_diagnosis_score = working_diagnosis_score
        self.max_iterations = max_iterations

    # ------------------------------------------------------------------ запуск
    def run(self, facts: PatientFacts) -> Conclusions:
        memory = Conclusions(facts=facts)
        self._iteration = 0
        known_diseases = set(facts.diseases)
        memory.working_diagnoses = sorted(known_diseases)
        for iteration in range(1, self.max_iterations + 1):
            self._iteration = iteration
            memory.iterations = iteration
            changed = False
            changed |= self._derive_profiles(memory)
            changed |= self._derive_scales(memory)
            changed |= self._derive_cards(memory, "redflag", "triggers", memory.facts.red_flags)
            changed |= self._derive_cards(memory, "emergency", "criteria", memory.facts.emergencies)
            changed |= self._fire_rules(memory)
            if memory.refusal is not None or not changed:
                break
        return memory

    # ------------------------------------------------------------------ шаги
    def _record(self, memory: Conclusions, kind: str, source: str, title: str,
                because: list[str], effects: list[str]) -> None:
        memory.trace.append(TraceStep(len(memory.trace) + 1, self._iteration, kind, source, title, because, effects))

    def _derive_profiles(self, memory: Conclusions) -> bool:
        changed = False
        for card in self.kb.category("profile"):
            if card.id in memory.facts.profiles:
                continue
            condition = card.metadata.get("criteria")
            if condition and evaluate(condition, memory.facts, self.schema) is Truth.TRUE:
                memory.facts.profiles.add(card.id)
                self._record(memory, "profile", card.id, card.title,
                             justify(condition, memory.facts, self.kb), [f"профиль пациента: {card.title}"])
                changed = True
        return changed

    def _derive_scales(self, memory: Conclusions) -> bool:
        changed = False
        for card in self.kb.category("scale"):
            result = compute_scale(card, memory.facts, self.schema)
            memory.scales[card.id] = result
            effects = []
            if result.complete and memory.facts.scales.get(card.id) != result.value:
                memory.facts.scales[card.id] = result.value
                effects.append(f"{card.title}: {result.value:g} балл(ов)")
            if result.category and memory.facts.scale_categories.get(card.id) != result.category:
                memory.facts.scale_categories[card.id] = result.category
                effects.append(f"категория: {result.category_label}"
                               + ("" if result.complete else f" (сумма {result.low:g}–{result.high:g}, часть данных отсутствует)"))
            if effects:
                known = [f"{i.label}: {i.points:g}" + (f" ({i.detail})" if i.detail else "") for i in result.items if i.points is not None]
                self._record(memory, "scale", card.id, card.title, known, effects)
                changed = True
        return changed

    def _derive_cards(self, memory: Conclusions, category: str, field_name: str, target: set[str]) -> bool:
        changed = False
        for card in self.kb.category(category):
            if card.id in target:
                continue
            condition = card.metadata.get(field_name)
            if not condition or evaluate(condition, memory.facts, self.schema) is not Truth.TRUE:
                continue
            target.add(card.id)
            kind_label = "красный флаг" if category == "redflag" else "неотложное состояние"
            effects = [f"{kind_label}: {card.title}"]
            self._raise_urgency(memory, card.urgency, card.id, f"{kind_label} «{card.title}»", effects)
            follow = card.metadata.get("action") or card.metadata.get("emergency_protocol")
            if follow:
                self._add_protocol(memory, follow, card.id, effects)
            self._record(memory, category, card.id, card.title, justify(condition, memory.facts, self.kb), effects)
            changed = True
        return changed

    def _fire_rules(self, memory: Conclusions) -> bool:
        changed = False
        for rule in self.kb.rules:
            if rule.id in memory.fired_rules:
                continue
            if evaluate(rule.condition, memory.facts, self.schema) is not Truth.TRUE:
                continue
            memory.fired_rules.append(rule.id)
            effects = self._apply_actions(memory, rule)
            self._record(memory, "rule", rule.id, rule.title, justify(rule.condition, memory.facts, self.kb), effects)
            changed = True
            if memory.refusal is not None:
                break
        return changed

    # ------------------------------------------------------------------ действия
    def _apply_actions(self, memory: Conclusions, rule: Rule) -> list[str]:
        effects: list[str] = []
        for action in rule.actions:
            name, value = next(iter(action.items()))
            if name == "assert_hypothesis":
                target, weight = value["target"], int(value.get("weight", 1))
                hyp = memory.hypotheses.setdefault(target, Hypothesis(target))
                hyp.score += weight
                hyp.sources.append(rule.id)
                effects.append(f"гипотеза «{self.kb.title(target)}» +{weight} (итого {hyp.score})")
                card = self.kb.get(target)
                if (card is not None and card.category == "disease" and hyp.score >= self.working_diagnosis_score
                        and target not in memory.facts.diseases):
                    memory.facts.diseases.add(target)
                    memory.working_diagnoses.append(target)
                    effects.append(f"рабочий диагноз: {card.title}")
            elif name == "trigger_red_flag":
                if value not in memory.facts.red_flags:
                    memory.facts.red_flags.add(value)
                    effects.append(f"красный флаг: {self.kb.title(value)}")
                    self._raise_urgency(memory, self.kb.card_urgency(value), rule.id, rule.title, effects)
            elif name == "set_urgency":
                self._raise_urgency(memory, str(value), rule.id, rule.title, effects)
            elif name == "recommend_exam":
                target, role = (value["target"], value.get("role", "supports")) if isinstance(value, dict) else (value, "supports")
                entry = memory.exams.setdefault(target, {"roles": [], "sources": []})
                if role not in entry["roles"]:
                    entry["roles"].append(role)
                entry["sources"].append(rule.id)
                effects.append(f"обследование: {self.kb.title(target)} ({role})")
            elif name == "route":
                route, timeframe = (value["value"], value.get("timeframe", "")) if isinstance(value, dict) else (value, "")
                memory.routes.append({"route": route, "timeframe": timeframe, "source": rule.id})
                effects.append(f"маршрут: {route}" + (f", {timeframe}" if timeframe else ""))
            elif name == "apply_protocol":
                self._add_protocol(memory, str(value), rule.id, effects)
            elif name == "warn":
                memory.warnings.append({"text": str(value), "source": rule.id})
                effects.append("предупреждение о безопасности")
            elif name == "request_clarification":
                memory.clarifications.append({"text": str(value), "source": rule.id})
                effects.append("запрос уточнения")
            elif name == "refuse":
                memory.refusal = {"text": str(value), "source": rule.id}
                effects.append("отказ: вне области применимости")
        return effects

    def _raise_urgency(self, memory: Conclusions, level: str, source: str, reason: str, effects: list[str]) -> None:
        if level not in URGENCY_ORDER:
            return
        memory.urgency_sources.append({"level": level, "source": source, "reason": reason})
        if URGENCY_ORDER.index(level) > URGENCY_ORDER.index(memory.urgency):
            memory.urgency = level
            effects.append(f"срочность повышена: {URGENCY_LABELS[level]}")

    def _add_protocol(self, memory: Conclusions, card_id: str, source: str, effects: list[str]) -> None:
        if any(p["id"] == card_id for p in memory.protocols):
            return
        memory.protocols.append({"id": card_id, "source": source})
        effects.append(f"переход: {self.kb.title(card_id)}")

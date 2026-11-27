"""Снимки рабочей памяти и связи между фактами прямого вывода."""

from collections.abc import Iterable
from typing import Any

from ..conditions import PatientFacts
from .knowledge import KnowledgeBase


FactKey = tuple[str, str]


class InferenceGraph:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.stop = ""
        self.nodes: list[dict[str, Any]] = []
        self.steps: list[dict[str, Any]] = []
        self.active: dict[FactKey, int] = {}
        self.missing: dict[FactKey, int] = {}

    def _new_node(self, key: FactKey, value, step: int, *, absent=False) -> int:
        kind, code = key
        titles = {"urgency": "Срочность", "warning": "Предупреждение", "clarification": "Уточнение",
                  "route": "Маршрут из правила", "refusal": "Граница применимости"}
        label = titles.get(kind) or self.kb.label(kind, code)
        if absent:
            value = "не сообщено"
        elif isinstance(value, bool):
            value = "да" if value else "нет"
        elif kind == "scale" and isinstance(value, tuple):
            value = f"{value[0]:g}–{value[1]:g} балл. (интервал)"
        elif kind in ("scale", "hypothesis"):
            value = f"{value:g} балл."
        elif kind == "exam_result":
            card = self.kb.get(code)
            value = next((item["label"] for item in card.metadata.get("results", []) if item["value"] == value), value)
        elif kind == "scale_category":
            card = self.kb.get(code)
            value = next((item["label"] for item in card.metadata.get("interpretation", []) if item["category"] == value), value)
        elif kind == "exam":
            roles = {"confirms": "подтверждение", "excludes": "исключение", "supports": "поддержка гипотезы",
                     "stratifies": "оценка тяжести", "monitors": "наблюдение"}
            value = ", ".join(roles.get(role, role) for role in value.split(", "))
        elif kind == "route":
            route, timeframe = value
            route = self.kb.schema.solver_setting("route_labels", {}).get(route, route)
            value = " · ".join(filter(None, (route, timeframe)))
        ident = len(self.nodes)
        self.nodes.append({"id": ident, "kind": kind, "code": code, "label": label,
                           "value": value, "step": step, "absent": absent})
        return ident

    def seed(self, facts: PatientFacts, *, skip: frozenset[FactKey] = frozenset()) -> None:
        for key, value in self.fact_values(facts).items():
            if key not in self.active and key not in skip:
                self.active[key] = self._new_node(key, value, 0)

    @staticmethod
    def fact_values(facts: PatientFacts) -> dict[FactKey, Any]:
        values = {}
        for kind, positive, negative in (
            ("symptom", facts.symptoms, facts.denied_symptoms),
            ("feature", facts.features, facts.denied_features),
            ("disease", facts.diseases, ()),
            ("profile", facts.profiles, ()),
            ("redflag", facts.red_flags, ()),
            ("emergency", facts.emergencies, ()),
            ("medication", facts.medications, ()),
        ):
            values.update(((kind, code), True) for code in sorted(positive))
            values.update(((kind, code), False) for code in sorted(negative))
        for kind, items in (
            ("param", facts.params), ("fact", facts.facts), ("exam_result", facts.exam_results),
            ("scale", facts.scale_bounds | facts.scales), ("scale_category", facts.scale_categories),
        ):
            values.update(((kind, code), value) for code, value in sorted(items.items()))
        return values

    def record(self, title: str, source: str, iteration: int,
               reads: Iterable[FactKey], changes: dict[FactKey, Any], *,
               effects: Iterable[str] = (), evidence: Iterable[str] = ()) -> None:
        inputs = []
        for key in dict.fromkeys(reads):
            ident = self.active.get(key)
            if ident is None:
                if key not in self.missing:
                    self.missing[key] = self._new_node(key, None, 0, absent=True)
                ident = self.missing[key]
            inputs.append(ident)
        number = len(self.steps) + 1
        outputs = []
        for key, value in changes.items():
            if key in self.active and self.active[key] not in inputs:
                inputs.append(self.active[key])
            ident = self.active[key] = self._new_node(key, value, number)
            outputs.append(ident)
        self.steps.append({"step": number, "iteration": iteration, "source": source,
                           "title": title, "inputs": inputs, "outputs": outputs,
                           "effects": list(effects), "evidence": list(evidence)})

    def as_dict(self) -> dict[str, Any]:
        return {"nodes": self.nodes, "steps": self.steps, "stop": self.stop}

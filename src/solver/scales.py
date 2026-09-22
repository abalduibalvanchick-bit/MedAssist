"""Расчёт клинических шкал по машиночитаемому слою карточек scale.

Сумма баллов вычисляется интервально. Для параметра, по которому данных нет,
берутся минимальный и максимальный возможные баллы. Если интервал вырожден
(все данные есть), значение шкалы известно точно. Если интервал целиком
попадает в один диапазон интерпретации, известна категория, даже когда
часть данных отсутствует. Иначе шкала остаётся невычисленной, а недостающие
параметры попадают в список уточняющих вопросов.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..conditions import PatientFacts, Truth, collect_references, evaluate
from ..models import KnowledgeCard
from ..schema import Schema


@dataclass
class ScaleItem:
    code: str
    label: str
    points: float | None          # None — данных нет
    detail: str = ""


@dataclass
class ScaleResult:
    scale_id: str
    title: str
    low: float
    high: float
    items: list[ScaleItem] = field(default_factory=list)
    category: str | None = None
    category_label: str | None = None
    action: str | None = None
    missing: set[str] = field(default_factory=set)   # коды параметров/фактов/признаков

    @property
    def complete(self) -> bool:
        return self.low == self.high

    @property
    def value(self) -> float | None:
        return self.low if self.complete else None


def _interpret(card: KnowledgeCard, total: float) -> dict[str, Any] | None:
    for band in card.metadata.get("interpretation") or []:
        lo = float(band.get("min", float("-inf")))
        hi = band.get("max")
        if total >= lo and (hi is None or total <= float(hi)):
            return band
    return None


def compute_scale(card: KnowledgeCard, facts: PatientFacts, schema: Schema) -> ScaleResult:
    meta = card.metadata
    result = ScaleResult(scale_id=card.id, title=card.title, low=0.0, high=0.0)
    policy = meta.get("missing_policy") or "skip"
    for param in meta.get("parameters") or []:
        code, label = str(param.get("code")), str(param.get("label", param.get("code")))
        if param.get("points_from"):
            name = param["points_from"]
            value = facts.params.get(name)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                result.low += float(value)
                result.high += float(value)
                result.items.append(ScaleItem(code, label, float(value), f"{name}={value}"))
            else:
                spec = schema.parameters.get(name, {})
                result.low += float(spec.get("min", 0))
                result.high += float(spec.get("max", 0))
                result.missing.add(name)
                result.items.append(ScaleItem(code, label, None, "нет данных"))
            continue
        options = param.get("options") or []
        chosen = None
        undecided = []
        for option in options:
            truth = evaluate(option["when"], facts, schema)
            if truth is Truth.TRUE:
                chosen = option
                break
            if truth is Truth.UNKNOWN:
                undecided.append(option)
        if chosen is not None:
            pts = float(chosen.get("points", 0))
            result.low += pts
            result.high += pts
            result.items.append(ScaleItem(code, label, pts, str(chosen.get("label", ""))))
        else:
            points = [float(o.get("points", 0)) for o in undecided] or [0.0]
            result.low += min(points)
            result.high += max(points)
            for option in undecided:
                refs = collect_references(option["when"], schema)
                result.missing |= refs.params | refs.facts | refs.features
            result.items.append(ScaleItem(code, label, None, "нет данных"))

    low_band, high_band = _interpret(card, result.low), _interpret(card, result.high)
    category_known = low_band is not None and low_band is high_band
    if policy == "fail" and not result.complete:
        category_known = False
    if category_known:
        result.category = str(low_band.get("category"))
        result.category_label = str(low_band.get("label", result.category))
        result.action = low_band.get("action")
    return result

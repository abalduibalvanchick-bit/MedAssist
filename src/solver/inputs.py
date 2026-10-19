"""Описание данных, которые решатель может запросить у пользователя.

Уточняющий вопрос содержит не только текст, но и список «полей ввода»:
что именно нужно сообщить, какого типа значение и в каких пределах. По коду
поля ответ подставляется обратно в описание пациента (модуль dialog), поэтому
интерфейс может задать вопрос и повторно решить задачу без разбора текста.

Виды полей:
    param        числовой или логический параметр из словаря схемы (sbp, urea)
    fact         факт анамнеза из словаря схемы (smoker, confusion) — да/нет
    feature      признак симптома (chest_pain.at_rest) — да/нет
    symptom      симптом (карточка symptom) — есть/нет
    exam_result  результат обследования (карточка exam) — выбор из вариантов
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:  # pragma: no cover
    from ..conditions import ConditionRefs, PatientFacts
    from .knowledge import KnowledgeBase

INPUT_KINDS = ("param", "fact", "feature", "symptom", "exam_result")


def kind_of(code: str, kb: "KnowledgeBase") -> str | None:
    """Определяет вид поля по коду: словарь схемы, признаки симптомов, карточки."""
    if code in kb.schema.parameters:
        return "param"
    if code in kb.schema.facts:
        return "fact"
    if code in kb.feature_owner:
        return "feature"
    card = kb.get(code)
    if card is not None and card.category == "symptom":
        return "symptom"
    if card is not None and card.category == "exam":
        return "exam_result"
    return None


def describe_input(code: str, kb: "KnowledgeBase", kind: str | None = None) -> dict[str, Any] | None:
    """Описание поля ввода: код, вид, подпись, тип значения и ограничения."""
    kind = kind or kind_of(code, kb)
    if kind == "param":
        spec = kb.schema.parameters.get(code, {})
        item: dict[str, Any] = {"kind": kind, "code": code, "label": str(spec.get("label", code)),
                                "type": "boolean" if spec.get("type") == "boolean" else "number"}
        for key in ("unit", "min", "max"):
            if spec.get(key) is not None:
                item[key] = spec[key]
        return item
    if kind == "fact":
        return {"kind": kind, "code": code, "label": kb.label("fact", code), "type": "boolean"}
    if kind == "feature":
        owner = kb.feature_owner.get(code)
        return {"kind": kind, "code": code, "label": kb.label("feature", code), "type": "boolean",
                "symptom": owner, "symptom_title": kb.title(owner) if owner else ""}
    if kind == "symptom":
        return {"kind": kind, "code": code, "label": kb.title(code), "type": "boolean"}
    if kind == "exam_result":
        card = kb.get(code)
        options = [{"value": str(r.get("value")), "label": str(r.get("label", r.get("value")))}
                   for r in (card.metadata.get("results") or []) if isinstance(r, dict)] if card else []
        return {"kind": kind, "code": code, "label": kb.title(code), "type": "choice", "options": options}
    return None


def is_known(item: dict[str, Any], facts: "PatientFacts") -> bool:
    """Сообщено ли уже значение поля (тогда спрашивать его не нужно)."""
    code, kind = item["code"], item["kind"]
    if kind == "param":
        return code in facts.params
    if kind == "fact":
        return code in facts.facts
    if kind == "feature":
        return code in facts.features or code in facts.denied_features
    if kind == "symptom":
        return code in facts.symptoms or code in facts.denied_symptoms
    if kind == "exam_result":
        return code in facts.exam_results
    return False


def inputs_from_refs(refs: "ConditionRefs", kb: "KnowledgeBase",
                     askable_cards: Iterable[str] = ("symptom", "exam")) -> list[dict[str, Any]]:
    """Поля ввода по ссылкам условия (результат missing_inputs и т. п.)."""
    items: list[dict[str, Any]] = []
    for code in sorted(refs.params):
        items.append(describe_input(code, kb, "param"))
    for code in sorted(refs.facts):
        items.append(describe_input(code, kb, "fact"))
    for code in sorted(refs.features):
        items.append(describe_input(code, kb, "feature"))
    allowed = set(askable_cards)
    for cid in sorted(refs.card_ids):
        card = kb.get(cid)
        if card is not None and card.category in allowed:
            items.append(describe_input(cid, kb, "symptom" if card.category == "symptom" else "exam_result"))
    return [i for i in items if i is not None]


def known_atoms(node: Any) -> list[str]:
    """Коды из метаатомов {known: код} условия правила, в порядке появления."""
    found: list[str] = []
    if isinstance(node, dict):
        if "known" in node and len(node) == 1:
            found.append(str(node["known"]))
        for value in node.values():
            for code in known_atoms(value):
                if code not in found:
                    found.append(code)
    elif isinstance(node, list):
        for value in node:
            for code in known_atoms(value):
                if code not in found:
                    found.append(code)
    return found


def label_of(item: dict[str, Any]) -> str:
    """Подпись поля для текстового вопроса (как раньше выводилась в поле ask)."""
    if item["kind"] == "param" and item.get("unit"):
        return f"{item['label']}, {item['unit']}"
    if item["kind"] == "symptom":
        return f"симптом: {item['label']}"
    if item["kind"] == "exam_result":
        return f"результат обследования: {item['label']}"
    return item["label"]


_DERIVED_FIELDS = {"redflag": "triggers", "emergency": "criteria", "profile": "criteria"}


def missing_inputs_deep(condition: Any, facts: "PatientFacts", kb: "KnowledgeBase", depth: int = 3) -> "ConditionRefs":
    """Недостающие входные данные условия с раскрытием выводимых сущностей.

    Неизвестный атом {redflag: X} (а также emergency, profile) сам по себе спросить нельзя;
    вместо него запрашиваются недостающие данные условия карточки X (рекурсивно, до depth).
    """
    from ..conditions import ConditionRefs, missing_inputs

    result = ConditionRefs()
    refs = missing_inputs(condition, facts, kb.schema)
    result.params |= refs.params
    result.facts |= refs.facts
    result.features |= refs.features
    for cid in refs.card_ids:
        card = kb.get(cid)
        field_name = _DERIVED_FIELDS.get(card.category) if card is not None else None
        if field_name and depth > 0 and card.metadata.get(field_name):
            inner = missing_inputs_deep(card.metadata[field_name], facts, kb, depth - 1)
            result.params |= inner.params
            result.facts |= inner.facts
            result.features |= inner.features
            result.card_ids |= inner.card_ids
        else:
            result.card_ids.add(cid)
    return result

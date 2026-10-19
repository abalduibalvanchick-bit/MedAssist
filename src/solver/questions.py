"""Формирование уточняющих вопросов.

Источники вопросов, в порядке важности:
1. действия request_clarification сработавших правил;
2. неисключённые красные флаги и неотложные состояния: условие карточки
   осталось «неизвестным», но часть его уже выполнена — решатель просит
   именно те данные, которых не хватает, чтобы подтвердить или исключить
   опасное состояние (безопасность прежде всего);
3. шкалы, относящиеся к рабочим диагнозам, которые не удалось
   вычислить из-за нехватки данных.

Ранжирование вопросов по информативности — задача диагностического модуля;
здесь порядок задаётся категорией источника и срочностью карточки.

Каждый вопрос содержит:
    text    формулировку для человека;
    ask     подписи запрашиваемых данных (для текстового вывода);
    inputs  поля ввода с кодами и типами значений (модуль inputs) — по ним
            интерфейс подставляет ответы и повторно решает задачу (модуль dialog).
Для действий request_clarification поля ввода выводятся из метаатомов
{known: код} условия правила: правило срабатывает, когда значение не
сообщено, значит, именно его и нужно запросить.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..conditions import EvalTrace, Truth, evaluate, missing_inputs
from .inputs import describe_input, inputs_from_refs, is_known, known_atoms, label_of

if TYPE_CHECKING:  # pragma: no cover
    from .engine import Conclusions
    from .knowledge import KnowledgeBase

_ASKABLE_CATEGORIES = {"symptom", "exam"}


def _question(kind: str, source: str, text: str, inputs: list[dict[str, Any]]) -> dict[str, Any]:
    return {"kind": kind, "source": source, "text": text, "ask": [label_of(i) for i in inputs], "inputs": inputs}


def _clarification_inputs(rule_id: str, memory: "Conclusions", kb: "KnowledgeBase") -> list[dict[str, Any]]:
    rule = next((r for r in kb.rules if r.id == rule_id), None)
    if rule is None:
        return []
    items = [describe_input(code, kb) for code in known_atoms(rule.condition)]
    return [i for i in items if i is not None and not is_known(i, memory.facts)]


# Клинические «якоря»: условие опасного состояния считается частично
# выполненным, только если истинен хотя бы один такой атом. Одних общих
# фактов и параметров (возраст, спутанность сознания) недостаточно — иначе
# решатель задавал бы вопросы о состояниях, не связанных с жалобами.
_ANCHOR_ATOMS = ("symptom", "feature", "disease", "exam_result", "redflag", "emergency")


def _partially_met(condition: dict[str, Any], memory: "Conclusions", kb: "KnowledgeBase") -> bool:
    trace: list[EvalTrace] = []
    evaluate(condition, memory.facts, kb.schema, trace=trace)
    return any(e.result is Truth.TRUE and any(a in e.node for a in _ANCHOR_ATOMS) for e in trace)


def build_questions(memory: "Conclusions", kb: "KnowledgeBase") -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    seen_texts: set[str] = set()
    facts = memory.facts
    if not (facts.symptoms or facts.diseases or facts.exam_results):
        questions.append(_question("general", "", "Опишите основные жалобы пациента: какие симптомы, когда появились, как менялись.", []))

    for item in memory.clarifications:
        if item["text"] not in seen_texts:
            seen_texts.add(item["text"])
            questions.append(_question("clarification", item["source"], item["text"],
                                       _clarification_inputs(item["source"], memory, kb)))

    for category, field_name, derived in (("emergency", "criteria", memory.facts.emergencies),
                                          ("redflag", "triggers", memory.facts.red_flags)):
        for card in kb.category(category):
            condition = card.metadata.get(field_name)
            if card.id in derived or not condition:
                continue
            if evaluate(condition, memory.facts, kb.schema) is not Truth.UNKNOWN:
                continue
            if not _partially_met(condition, memory, kb):
                continue
            inputs = inputs_from_refs(missing_inputs(condition, memory.facts, kb.schema), kb, _ASKABLE_CATEGORIES)
            if inputs:
                questions.append(_question("safety_check", card.id,
                                           f"Чтобы подтвердить или исключить «{card.title}», уточните данные.", inputs))

    # Шкалы уточняются только для рабочих диагнозов: для слабых гипотез
    # вопросы о шкалах были бы шумом (особенно в экстренной ситуации).
    relevant = set(memory.working_diagnoses)
    for scale_id, result in memory.scales.items():
        if result.category is not None or not result.missing:
            continue
        card = kb.get(scale_id)
        targets = {str(r.get("target")) for r in card.relations} if card else set()
        if not targets & relevant:
            continue
        inputs = [i for i in (describe_input(code, kb) for code in sorted(result.missing)) if i is not None]
        questions.append(_question("scale", scale_id, f"Для расчёта шкалы «{card.title}» не хватает данных.", inputs))
    return questions

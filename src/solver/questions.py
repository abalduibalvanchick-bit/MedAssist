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
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..conditions import EvalTrace, Truth, evaluate, missing_inputs

if TYPE_CHECKING:  # pragma: no cover
    from .engine import Conclusions
    from .knowledge import KnowledgeBase

_ASKABLE_CATEGORIES = {"symptom", "exam"}


def _labels_for(refs, kb: "KnowledgeBase") -> list[str]:
    labels = [kb.label("param", p) for p in sorted(refs.params)]
    labels += [kb.label("fact", f) for f in sorted(refs.facts)]
    labels += [kb.label("feature", f) for f in sorted(refs.features)]
    for cid in sorted(refs.card_ids):
        card = kb.get(cid)
        if card is not None and card.category in _ASKABLE_CATEGORIES:
            labels.append(("результат обследования: " if card.category == "exam" else "симптом: ") + card.title)
    return labels


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
        questions.append({"kind": "general", "source": "", "ask": [],
                          "text": "Опишите основные жалобы пациента: какие симптомы, когда появились, как менялись."})

    for item in memory.clarifications:
        if item["text"] not in seen_texts:
            seen_texts.add(item["text"])
            questions.append({"kind": "clarification", "text": item["text"], "source": item["source"], "ask": []})

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
            ask = _labels_for(missing_inputs(condition, memory.facts, kb.schema), kb)
            if ask:
                questions.append({"kind": "safety_check", "source": card.id,
                                  "text": f"Чтобы подтвердить или исключить «{card.title}», уточните данные.", "ask": ask})

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
        ask = []
        for code in sorted(result.missing):
            kind = "param" if code in kb.schema.parameters else "fact" if code in kb.schema.facts else "feature"
            ask.append(kb.label(kind, code))
        questions.append({"kind": "scale", "source": scale_id,
                          "text": f"Для расчёта шкалы «{card.title}» не хватает данных.", "ask": ask})
    return questions

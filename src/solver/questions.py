"""Формирование уточняющих вопросов.

Источники вопросов, в порядке важности:
1. действия request_clarification сработавших правил;
2. неисключённые красные флаги и неотложные состояния: условие карточки
   осталось «неизвестным», но часть его уже выполнена — решатель просит
   именно те данные, которых не хватает, чтобы подтвердить или исключить
   опасное состояние (безопасность прежде всего);
3. шкалы, относящиеся к рабочим диагнозам, которые не удалось
   вычислить из-за нехватки данных;
4. недостающие данные частично выполненных диагностических правил,
   затем признаки жалобы, если результата и более конкретных вопросов ещё нет.

Функция rank_questions назначает приоритет по влиянию недостающих данных.

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

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from ..conditions import Truth, evaluate, missing_inputs
from .inputs import describe_input, inputs_from_refs, is_known, known_atoms, label_of, missing_inputs_deep

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
# выполненным, только если истинен хотя бы один такой атом — проявление
# текущего обращения (жалоба, её признак, результат обследования, уже
# распознанное опасное состояние). Общих фактов и параметров (возраст,
# спутанность) и фоновых диагнозов из анамнеза недостаточно — иначе решатель
# спрашивал бы о состояниях, не связанных с жалобами (пациента с известной
# мигренью без головной боли — о мигренозном статусе).
_ANCHOR_ATOMS = ("symptom", "feature", "exam_result", "redflag", "emergency")


def _anchor_atoms(node: Any):
    """Все атомы-якоря условия (без учёта порядка вычисления и сокращённой оценки)."""
    if isinstance(node, dict):
        if any(a in node for a in _ANCHOR_ATOMS) and not any(c in node for c in ("all", "any", "not", "at_least")):
            yield node
            return
        for key, value in node.items():
            if key == "not":
                continue  # отрицаемое проявление якорем не является
            yield from _anchor_atoms(value)
    elif isinstance(node, list):
        for value in node:
            yield from _anchor_atoms(value)


def _partially_met(condition: dict[str, Any], memory: "Conclusions", kb: "KnowledgeBase") -> bool:
    """Истинен ли хотя бы один атом-якорь условия. Атомы оцениваются по отдельности,
    поэтому результат не зависит от порядка ветвей any/all и сокращённого вычисления."""
    return any(evaluate(atom, memory.facts, kb.schema) is Truth.TRUE for atom in _anchor_atoms(condition))


def detail_questions(memory: "Conclusions", kb: "KnowledgeBase") -> list[dict[str, Any]]:
    """Уточнение жалоб: признаки сообщённых симптомов из их карточек (поле features).

    Используется, когда данных недостаточно ни для одного вывода, а других вопросов нет:
    решатель не должен отвечать «нужны данные», ничего не спросив (требование Ф6).
    """
    questions = []
    for sid in sorted(memory.facts.symptoms):
        card = kb.get(sid)
        codes = [str(f.get("code")) for f in (card.metadata.get("features") or []) if isinstance(f, dict)] if card else []
        inputs = [describe_input(code, kb, "feature") for code in codes]
        inputs = [i for i in inputs if i is not None and not is_known(i, memory.facts)]
        if inputs:
            questions.append(_question("symptom_details", sid, f"Уточните характер жалобы «{card.title}».", inputs))
    return questions


def fallback_questions(memory: "Conclusions", kb: "KnowledgeBase") -> list[dict[str, Any]]:
    """Сначала запросить данные, которые могут изменить вывод по гипотезе."""
    questions = []
    facts = memory.facts
    depth = kb.schema.solver_setting("question_dependency_depth", 3)
    seen = set()
    for rule in kb.rules:
        if rule.domain != "diag" or not any("assert_hypothesis" in action for action in rule.actions):
            continue
        if evaluate(rule.condition, facts, kb.schema) is not Truth.UNKNOWN:
            continue
        if not _partially_met(rule.condition, memory, kb):
            continue
        refs = missing_inputs_deep(rule.condition, facts, kb, depth=depth)
        inputs = [item for item in inputs_from_refs(refs, kb, _ASKABLE_CATEGORIES)
                  if not is_known(item, facts) and (item["type"] != "choice" or item["options"])]
        codes = frozenset(item["code"] for item in inputs)
        if not codes or codes in seen:
            continue
        seen.add(codes)
        questions.append(_question("rule_inputs", rule.id, "Уточните известные сопутствующие признаки или измерения.", inputs))

    return questions or detail_questions(memory, kb) or [
        _question("additional_context", "", "По введённым данным решатель не сформировал вывод и не нашёл конкретных уточнений. "
                  "Если известны другие симптомы или результаты обследований, добавьте их в форму.", [])
    ]


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
    # В экстренной ситуации вопросы для шкал не задаются: время уходит на неотложные
    # действия, а оценка хронического заболевания выполняется после стабилизации.
    relevant = set(memory.working_diagnoses) if memory.urgency != "emergency" else set()
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


def rank_questions(questions, memory, kb, *, include_hypotheses=True):
    """Распределяет важность вывода между недостающими полями и суммирует вклады."""
    weights = kb.schema.solver_setting("question_weights", {})
    if include_hypotheses and memory.urgency != "emergency":
        for hypothesis in sorted(memory.hypotheses.values(), key=lambda h: (-h.score, h.target))[:3]:
            card = kb.get(hypothesis.target)
            inputs = {}
            for entry in card.metadata.get("presentation", []):
                item = describe_input(entry["symptom"], kb, "symptom")
                if item and not is_known(item, memory.facts):
                    inputs[item["code"]] = item
            if inputs:
                questions.append(_question("hypothesis", card.id,
                                           f"Уточните признаки для сопоставления с гипотезой «{card.title}».",
                                           list(inputs.values())))

    def weight(question):
        kind = question["kind"]
        if kind in ("differential", "safety_check"):
            urgency = question.get("urgency") or kb.card_urgency(question["source"])
            return weights.get(urgency, 1)
        return weights.get(kind, 1)

    scores = defaultdict(float)
    evaluated = []
    counted = set()
    for question in questions:
        codes = {item["code"] for item in question["inputs"]}
        importance = weight(question)
        dependency = (question["kind"], question["source"], question.get("target"),
                      frozenset(codes))
        if dependency not in counted:
            counted.add(dependency)
            for code in codes:
                scores[code] += importance / len(codes)
        evaluated.append((question, codes, importance))

    ranked = []
    for question, codes, importance in evaluated:
        inputs = sorted(
            ({**item, "priority": round(scores[item["code"]], 4)} for item in question["inputs"]),
            key=lambda item: (-item["priority"], item["code"]),
        )
        ranked.append({**question, "inputs": inputs, "ask": [label_of(item) for item in inputs],
                       "priority": round(max((scores[code] for code in codes), default=importance), 4)})
    ranked.sort(key=lambda q: (-q["priority"], q["inputs"][0]["code"] if q["inputs"] else "",
                              q["source"], q["kind"]))
    return ranked

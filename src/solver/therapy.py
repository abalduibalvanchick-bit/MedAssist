"""Оценка вариантов терапии и взаимодействий по формальным карточкам."""

from ..conditions import Truth, evaluate
from ..pharmacology import drug_classes, effective_contraindications
from .engine import record_step
from .explain import justify, justify_false
from .inputs import inputs_from_refs, is_known, label_of, missing_inputs_deep

_STATUS = ("available", "caution", "verify", "excluded")
_LABEL = {
    "available": "по данным базы ограничений не выявлено",
    "caution": "требуется осторожность",
    "verify": "требуется проверка",
    "excluded": "исключён",
}


def _expand_profiles(node, kb):
    if isinstance(node, list):
        return [_expand_profiles(value, kb) for value in node]
    if isinstance(node, dict):
        if set(node) == {"profile"}:
            card = kb.get(node["profile"])
            if card and card.metadata.get("criteria"):
                return card.metadata["criteria"]
        return {key: _expand_profiles(value, kb) for key, value in node.items()}
    return node


def _checks(agent, kb):
    if agent.category == "drug":
        return effective_contraindications(agent, kb.cards)
    entries = agent.metadata.get("contraindications", [])
    if agent.category == "nonpharm":
        return [{"when": condition, "absolute": True, "source": agent.id,
                 "explanation": "Сработало противопоказание из карточки."} for condition in entries]
    return [{**entry, "source": agent.id} for entry in entries]


def _agent_codes(agent, kb):
    return {agent.id, *(card.id for card in drug_classes(agent, kb.cards))}


def assess_therapy(memory, kb):
    facts = memory.facts
    questions = []
    depth = kb.schema.solver_setting("question_dependency_depth", 3)

    def check(condition):
        return evaluate(_expand_profiles(condition, kb), facts, kb.schema)

    def ask(condition, source, text):
        refs = missing_inputs_deep(_expand_profiles(condition, kb), facts, kb, depth=depth)
        inputs = [item for item in inputs_from_refs(refs, kb) if not is_known(item, facts)
                  and (item["type"] != "choice" or item["options"])]
        if inputs:
            questions.append({"kind": "therapy", "source": source, "text": text,
                              "inputs": inputs, "ask": [label_of(item) for item in inputs]})

    def assess_option(option, regime):
        agent = kb.get(option["agent"])
        status, reasons, pending = "available", [], []
        condition = option.get("when")
        if condition:
            truth = check(condition)
            if truth is Truth.FALSE:
                status = "excluded"
                reasons.append({"source": regime.id, "text": "Условие применения схемы не выполнено.",
                                "evidence": justify_false(_expand_profiles(condition, kb), facts, kb)})
            elif truth is Truth.UNKNOWN:
                status = "verify"
                reasons.append({"source": regime.id, "text": "Недостаточно данных об условии схемы.", "evidence": []})
                pending.append((condition, regime.id))

        for item in _checks(agent, kb):
            truth = check(item["when"])
            if truth is Truth.FALSE:
                continue
            if truth is Truth.UNKNOWN:
                outcome = "verify"
                evidence = []
                pending.append((item["when"], item["source"]))
            else:
                outcome = "excluded" if item["absolute"] else "caution"
                evidence = justify(_expand_profiles(item["when"], kb), facts, kb)
            status = max(status, outcome, key=_STATUS.index)
            reasons.append({"source": item["source"], "text": item.get("explanation", ""),
                            "state": truth.value, "evidence": evidence})

        if status != "excluded":
            for condition, source in pending:
                ask(condition, source, f"Уточните данные для проверки варианта «{agent.title}».")

        adjustments = []
        if status != "excluded":
            for item in agent.metadata.get("dose_adjustments", []):
                if check(item["when"]) is Truth.TRUE:
                    adjustments.append({"source": agent.id, "text": item["note"]})
            codes = _agent_codes(agent, kb)
            for card in kb.category("dosing"):
                for item in card.metadata.get("rules", []):
                    if item["agent"] in codes and check(item["when"]) is Truth.TRUE:
                        adjustments.append({"source": card.id, "text": item["adjustment"]})

        return {"id": agent.id, "title": agent.title, "status": status, "label": _LABEL[status],
                "note": option.get("note", ""), "reasons": reasons, "dose_notes": adjustments}

    regimens = []
    targets = facts.diseases | facts.emergencies
    for card in kb.category("regimen"):
        matches = sorted(targets.intersection(card.metadata.get("for", [])))
        if not matches:
            continue
        lines = [{"line": line["line"], "options": [assess_option(option, card) for option in line["options"]]}
                 for line in card.metadata["lines"]]
        regimens.append({"id": card.id, "title": card.title, "for": matches, "lines": lines})
        record_step(memory, "therapy", card.id, card.title, [kb.title(target) for target in matches],
                    [f"Проверено вариантов: {sum(len(line['options']) for line in lines)}"], memory.iterations + 1)

    medication_codes = set()
    for cid in facts.medications:
        medication_codes.update(_agent_codes(kb.get(cid), kb))
    interactions = []
    published = set()

    def add_interaction(card, participants, severity, text, state):
        key = (card.id, tuple(sorted(participants)), severity)
        if key in published:
            return
        published.add(key)
        interactions.append({"source": card.id, "title": card.title, "between": participants,
                             "severity": severity, "text": text, "state": state})
        record_step(memory, "interaction", card.id, card.title, [kb.title(cid) for cid in participants],
                    ["Обнаружено взаимодействие" if state == "true" else "Взаимодействие требует проверки"],
                    memory.iterations + 1)

    for card in kb.category("interaction"):
        participants = card.metadata["between"]
        if not set(participants) <= medication_codes:
            continue
        trigger = card.metadata.get("trigger")
        truth = check(trigger) if trigger else Truth.TRUE
        if truth is Truth.FALSE:
            continue
        add_interaction(card, participants, card.metadata["severity"],
                        card.metadata.get("management", "") if truth is Truth.TRUE else "Недостаточно данных.",
                        truth.value)
        if truth is Truth.UNKNOWN:
            ask(trigger, card.id, f"Уточните условия взаимодействия «{card.title}».")

    for cid in sorted(facts.medications):
        card = kb.get(cid)
        for item in card.metadata.get("interactions", []):
            other = item.get("with")
            if other in medication_codes and other not in _agent_codes(card, kb):
                add_interaction(card, [cid, other], item["severity"],
                                f"В карточке указано взаимодействие с «{kb.title(other)}».", "true")

    return {"regimens": regimens, "interactions": interactions}, questions

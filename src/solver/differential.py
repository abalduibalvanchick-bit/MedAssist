"""Оценка ветвей дифференциальной диагностики из карточек базы знаний."""

from ..conditions import Truth, evaluate
from .engine import URGENCY_ORDER, record_step
from .explain import justify, justify_false
from .inputs import inputs_from_refs, is_known, label_of, missing_inputs_deep
from .knowledge import known_exam_results


_STATUS = {"supported": "поддерживается", "unlikely": "маловероятна", "unresolved": "не исключена"}
_ORDER = ("supported", "unresolved", "unlikely")
_PRIORS = ("low", "medium", "high")


def assess_differential(memory, kb):
    tables, questions = [], []
    for card in kb.category("difdiag"):
        leading = card.metadata.get("leading_symptom")
        if leading not in memory.facts.symptoms:
            continue
        branches = []
        for branch in card.metadata.get("branches", []):
            supporting, against = branch["supporting"], branch.get("against")
            facts = memory.facts
            positive = evaluate(supporting, facts, kb.schema)
            negative = evaluate(against, facts, kb.schema) if against else Truth.FALSE
            if positive is Truth.FALSE or negative is Truth.TRUE:
                status = "unlikely"
            elif positive is Truth.TRUE:
                status = "supported"
            else:
                status = "unresolved"
            evidence_for = justify(supporting, facts, kb) if positive is Truth.TRUE else []
            evidence_against = []
            if negative is Truth.TRUE:
                evidence_against.extend(justify(against, facts, kb))
            if positive is Truth.FALSE:
                evidence_against.extend(justify_false(supporting, facts, kb))
            target, urgency = branch["target"], branch["urgency"]
            exam = branch.get("key_exam")
            recommend = exam and status != "unlikely" and urgency in ("urgent", "emergency")
            result = {
                "id": target, "title": kb.title(target), "status": status, "label": _STATUS[status],
                "prior": branch["prior"], "urgency": urgency, "for": evidence_for, "against": evidence_against,
                "key_exam": {"id": exam, "title": kb.title(exam), "recommended": bool(recommend),
                             "completed": bool(known_exam_results(kb, exam, facts))} if exam else None,
            }
            branches.append(result)
            if status == "unlikely":
                continue
            if status == "supported":
                record_step(memory, "differential", card.id, card.title, evidence_for,
                            [f"Ветвь поддерживается: {result['title']}"], memory.iterations + 1)
            if urgency not in ("urgent", "emergency"):
                continue
            inputs = {}
            depth = kb.schema.solver_setting("question_dependency_depth", 3)
            for condition, truth in ((supporting, positive), (against, negative)):
                if truth is Truth.UNKNOWN:
                    refs = missing_inputs_deep(condition, facts, kb, depth=depth)
                    for item in inputs_from_refs(refs, kb):
                        if not is_known(item, facts) and (item["type"] != "choice" or item["options"]):
                            inputs[item["code"]] = item
            if inputs:
                questions.append({"kind": "differential", "source": card.id, "target": target,
                                  "urgency": urgency, "inputs": list(inputs.values()),
                                  "ask": [label_of(i) for i in inputs.values()],
                                  "text": f"Уточните данные для ветви «{result['title']}»."})
        branches.sort(key=lambda item: (_ORDER.index(item["status"]), -URGENCY_ORDER.index(item["urgency"]),
                                       -_PRIORS.index(item["prior"]), item["id"]))
        tables.append({"id": card.id, "title": card.title, "leading_symptom": leading, "branches": branches})
    return tables, questions

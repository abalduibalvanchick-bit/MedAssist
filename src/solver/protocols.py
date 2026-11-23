"""Применение карточек протоколов к итоговой рабочей памяти решателя."""

from collections import deque

from ..conditions import Truth, describe, evaluate
from .knowledge import KnowledgeBase, known_exam_results
from .engine import Conclusions, record_step
from .routing import RoutingResult
from .explain import justify, justify_false
from .inputs import describe_input, inputs_from_refs, label_of, missing_inputs_deep


def _decision(condition, memory, kb, questions, card, label):
    truth = evaluate(condition, memory.facts, kb.schema)
    evidence = []
    if truth is Truth.TRUE:
        evidence = justify(condition, memory.facts, kb)
    elif truth is Truth.FALSE:
        evidence = justify_false(condition, memory.facts, kb)
    if truth is Truth.UNKNOWN:
        refs = missing_inputs_deep(condition, memory.facts, kb)
        inputs = inputs_from_refs(refs, kb)
        for scale_id in sorted(refs.card_ids & memory.scales.keys()):
            for code in sorted(memory.scales[scale_id].missing):
                field = describe_input(code, kb)
                if field and field not in inputs:
                    inputs.append(field)
        evidence = [f"нет данных: {label_of(field)}" for field in inputs]
        if inputs:
            questions.append({"kind": "protocol", "source": card.id, "inputs": inputs,
                              "ask": [label_of(i) for i in inputs], "text": f"Уточните данные: {label}."})
    return {"truth": truth.value, "condition": condition, "reason": describe(condition, kb.schema),
            "evidence": evidence}


def _steps(card, memory, kb, questions):
    steps = []
    for step in card.metadata["steps"]:
        item = {"id": step["id"], "action": step["action"], "status": "applicable", "refs": []}
        if "when" in step:
            decision = _decision(step["when"], memory, kb, questions, card, step["action"])
            item["condition"] = decision
            item["status"] = {"true": "applicable", "false": "not_required", "unknown": "conditional"}[decision["truth"]]
        for ref in step.get("refs", []):
            target = kb.get(ref)
            detail = {"id": ref, "title": kb.title(ref)}
            if target and target.category == "exam":
                values = known_exam_results(kb, ref, memory.facts)
                if values:
                    detail.update(status="result_known", results=values)
            item["refs"].append(detail)
        # Наличие результата по отдельной ссылке не завершает составной шаг
        # (в том числе повторные измерения и динамическое наблюдение).
        steps.append(item)
    return steps


def execute_protocols(memory: Conclusions, routing: RoutingResult, kb: KnowledgeBase):
    """Обойти переходы один раз на карточку и вернуть планы и поля для диалога."""
    if memory.refusal:
        return [], []
    queue = deque((p["id"], p["source"]) for p in memory.protocols)
    for card in kb.category("protocol"):
        for target in card.metadata.get("for", []):
            if target in memory.working_diagnoses or target in memory.facts.emergencies:
                queue.append((card.id, target))
    for decision in routing.decisions:
        queue.extend((ref, decision.card_id) for ref in decision.next)
    plans, questions, seen = [], [], set()
    while queue:
        cid, source = queue.popleft()
        card = kb.get(cid)
        if cid in seen or not card or card.category not in ("protocol", "emergency_p", "follow_up"):
            continue
        seen.add(cid)
        meta = card.metadata
        plan = {"id": cid, "source": source, "title": card.title, "kind": card.category, "status": "applicable"}
        plans.append(plan)
        entry = meta.get("entry") or meta.get("criteria")
        if entry:
            gate = _decision(entry, memory, kb, questions, card, card.title)
            plan["entry"] = gate
            if gate["truth"] != "true":
                plan["status"] = "conditional" if gate["truth"] == "unknown" else "not_applicable"
        effects = [plan["status"]]
        if plan["status"] == "applicable":
            if card.category == "protocol":
                plan["branches"] = []
                for branch in meta.get("branches", []):
                    decision = _decision(branch["when"], memory, kb, questions, card, branch["explanation"])
                    plan["branches"].append({**decision, "then": branch["then"], "explanation": branch["explanation"]})
                    if decision["truth"] == "true":
                        queue.append((branch["then"], cid))
                        effects.append(f"переход к {branch['then']}")
                plan["steps"] = _steps(card, memory, kb, questions)
                for step in plan["steps"]:
                    if step["status"] == "applicable":
                        queue.extend((r["id"], cid) for r in step["refs"] if kb.get(r["id"]).category == "follow_up")
                plan["targets"] = []
                for target in meta.get("targets", []):
                    condition = {k: target[k] for k in ("param", "op", "value")}
                    truth = evaluate(condition, memory.facts, kb.schema)
                    plan["targets"].append({**target, "actual": memory.facts.params.get(target["param"]),
                                            "status": {Truth.TRUE: "achieved", Truth.FALSE: "not_achieved",
                                                       Truth.UNKNOWN: "unknown"}[truth]})
            elif card.category == "emergency_p":
                plan["phases"] = meta["phases"]
            else:
                plan["schedule"] = meta["schedule"]
                plan["monitor"] = []
                for item in meta["monitor"]:
                    monitoring = dict(item)
                    if item.get("target"):
                        monitoring["assessment"] = evaluate(item["target"], memory.facts, kb.schema).value
                    plan["monitor"].append(monitoring)
                if meta.get("deterioration"):
                    state = evaluate(meta["deterioration"], memory.facts, kb.schema)
                    plan["deterioration"] = {"truth": state.value, "condition": meta["deterioration"]}
                    if state is Truth.TRUE and meta.get("on_deterioration"):
                        plan["deterioration"]["then"] = meta["on_deterioration"]
                        queue.append((meta["on_deterioration"], cid))
        record_step(memory, "protocol", cid, card.title, [source, *plan.get("entry", {}).get("evidence", [])],
                    effects, memory.iterations + 1)
    return plans, questions

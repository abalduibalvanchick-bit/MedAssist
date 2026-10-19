"""Достижимость знаний и корректность вариантов шкал.

1. Для каждого правила, красного флага, неотложного состояния и профиля
   строится пациент-«свидетель», на котором условие истинно (tests/witness.py),
   и проверяется, что решатель приходит к этому выводу. Тест автоматически
   распространяется на новые правила и карточки: недостижимое правило
   (опечатка в коде признака, невозможный порог) будет обнаружено, даже если
   ни один сценарий его не затрагивает.
2. Для каждого пункта шкалы с вариантами проверяется полнота: при любых
   сообщённых значениях входных данных хотя бы один вариант истинен
   (нет «дыр» на границах диапазонов, нет пунктов, которые нельзя заполнить).
"""

from __future__ import annotations

import itertools

import pytest

from src.conditions import PatientFacts, Truth, collect_references, evaluate
from src.solver import load_default_kb, solve
from tests.witness import Unsatisfiable, witness_for

KB = load_default_kb()

TARGETS = [("rule", r.id, r.condition, "fired_rules") for r in KB.rules]
for _category, _field, _key in (("redflag", "triggers", "red_flags"), ("emergency", "criteria", "emergencies"),
                                ("profile", "criteria", "profiles")):
    TARGETS += [(_category, c.id, c.metadata[_field], _key) for c in KB.category(_category) if c.metadata.get(_field)]


@pytest.mark.parametrize("kind,target_id,condition,key", TARGETS, ids=[t[1] for t in TARGETS])
def test_knowledge_is_reachable(kind, target_id, condition, key):
    try:
        request = witness_for(condition, KB)
    except Unsatisfiable as exc:  # pragma: no cover - сообщает, что свидетель не построен
        pytest.skip(f"свидетель не построен: {exc}")
    solution = solve(request, kb=KB)
    produced = solution.get(key) or []
    ids = produced if key == "fired_rules" else [item["id"] for item in produced]
    assert target_id in ids, (f"{target_id} не выведен для пациента {request['patient']}; "
                              f"статус {solution['status']}, замечания {solution.get('input_issues')}")


def _nodes(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from _nodes(value)


def _samples(name: str, conditions: list) -> list[float]:
    spec = KB.schema.parameters[name]
    lo, hi = spec.get("min", 0), spec.get("max", 1000)
    values = {lo, hi}
    for node in _nodes(conditions):
        if node.get("param") == name and "value" in node and not isinstance(node["value"], bool):
            for threshold in (node["value"] if isinstance(node["value"], list) else [node["value"]]):
                for delta in (-1, -0.1, 0, 0.1, 1):
                    values.add(round(threshold + delta, 1))
    return sorted(v for v in values if lo <= v <= hi)


SCALE_ITEMS = [(card.id, item) for card in KB.category("scale")
               for item in card.metadata.get("parameters") or [] if item.get("options")]


@pytest.mark.parametrize("scale_id,item", SCALE_ITEMS, ids=[f"{s}:{i['code']}" for s, i in SCALE_ITEMS])
def test_scale_item_options_are_exhaustive(scale_id, item):
    conditions = [o["when"] for o in item["options"]]
    refs = collect_references({"any": conditions}, KB.schema)
    params = sorted(p for p in refs.params if KB.schema.parameters[p].get("type") != "boolean")
    bool_params = sorted(p for p in refs.params if KB.schema.parameters[p].get("type") == "boolean")
    facts, cards = sorted(refs.facts), sorted(refs.card_ids)
    domains = [_samples(p, conditions) for p in params] + [[True, False]] * (len(bool_params) + len(facts) + len(cards))
    for combo in itertools.product(*domains):
        f = PatientFacts()
        values = iter(combo)
        for p in params + bool_params:
            f.params[p] = next(values)
        for name in facts:
            f.facts[name] = next(values)
        for cid in cards:
            if next(values):
                f.diseases.add(cid)
        truths = [evaluate(c, f, KB.schema) for c in conditions]
        assert Truth.TRUE in truths, f"{scale_id}:{item['code']} — ни один вариант не подходит для {combo}"


def test_rules_suspecting_emergency_raise_urgency():
    """Правило, выдвигающее гипотезу неотложного состояния, повышает срочность не ниже «срочной»:
    иначе неотложное состояние подозревается, а обследование допускается в плановом порядке."""
    offenders = []
    for rule in KB.rules:
        targets = [a["assert_hypothesis"]["target"] for a in rule.actions if "assert_hypothesis" in a]
        if not any(KB.get(t).category == "emergency" for t in targets):
            continue
        levels = [a["set_urgency"] for a in rule.actions if "set_urgency" in a]
        if not any(level in ("urgent", "emergency") for level in levels):
            offenders.append(rule.id)
    assert not offenders, f"не повышают срочность: {offenders}"


ROUTING_ROWS = [(card.id, i) for card in KB.category("routing") for i, _ in enumerate(card.metadata.get("decisions") or [])]


@pytest.mark.parametrize("card_id,row", ROUTING_ROWS, ids=[f"{c}:{r + 1}" for c, r in ROUTING_ROWS])
def test_routing_row_is_reachable(card_id, row):
    """Каждая строка таблицы решений может быть выбрана: строится пациент, для которого её условие
    истинно, а условия всех предыдущих (более тяжёлых) строк ложны. Строка, условие которой влечёт
    условие более ранней строки, недостижима — это мёртвое знание в базе."""
    card = KB.get(card_id)
    decisions = card.metadata["decisions"]
    condition = {"all": [decisions[row]["when"], *({"not": d["when"]} for d in decisions[:row])]}
    try:
        request = witness_for(condition, KB)
    except Unsatisfiable as exc:
        pytest.fail(f"{card_id}, строка {row + 1}: условие несовместимо с отрицанием предыдущих строк ({exc})")
    patient = request["patient"]
    for disease in card.metadata.get("for") or []:     # активировать карточку
        if KB.get(disease).category == "disease" and disease not in patient.get("diseases", []):
            patient.setdefault("diseases", []).append(disease)
    solution = solve(request, kb=KB)
    chosen = {d["id"]: d["row"] for d in solution["routing"]["decisions"]}
    assert chosen.get(card_id) == row, (f"{card_id}: для пациента {patient} выбрана строка "
                                        f"{chosen.get(card_id)}, ожидалась {row} — строка недостижима или "
                                        f"перекрыта более ранней")

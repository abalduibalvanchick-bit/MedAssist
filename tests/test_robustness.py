"""Устойчивость решателя (требование Н5): никакие входные данные не приводят к падению.

Случайные описания пациента генерируются с фиксированным зерном (результат
воспроизводим): корректные коды вперемешку с мусором — строки вместо чисел,
NaN, списки вместо словарей, несуществующие идентификаторы, неверные роли.
Решатель обязан вернуть решение со статусом, а не исключение.
"""

from __future__ import annotations

import json
import random

import pytest

from src.solver import apply_answers, load_default_kb, run_dialog, solve

KB = load_default_kb()
JUNK = [None, "", "abc", -1, 1e9, [], {}, [1, 2], {"a": 1}, True, 3.5, "DIAG-SYMPTOM-999", float("nan"), float("inf")]
STATUSES = {"ok", "need_more_data", "refused", "invalid"}


def _random_patient(rnd: random.Random) -> dict:
    schema = KB.schema
    params, facts, features = list(schema.parameters), list(schema.facts), list(KB.feature_owner)
    symptoms = [c.id for c in KB.category("symptom")]

    def junk():
        return rnd.choice(JUNK)

    patient: dict = {}
    if rnd.random() < 0.8:
        patient["age"] = rnd.choice([rnd.randint(0, 100), junk()])
    if rnd.random() < 0.6:
        patient["symptoms"] = rnd.sample(symptoms, rnd.randint(0, 3)) + ([junk()] if rnd.random() < 0.2 else [])
    if rnd.random() < 0.6:
        patient["features"] = rnd.sample(features, rnd.randint(0, 4))
    if rnd.random() < 0.3:
        patient["denied_features"] = rnd.sample(features, rnd.randint(0, 3))
    if rnd.random() < 0.7:
        patient["params"] = {k: (rnd.uniform(schema.parameters[k].get("min", 0), schema.parameters[k].get("max", 100))
                                 if rnd.random() < 0.8 else junk()) for k in rnd.sample(params, rnd.randint(0, 8))}
    if rnd.random() < 0.6:
        patient["facts"] = {k: (rnd.random() < 0.5 if rnd.random() < 0.85 else junk()) for k in rnd.sample(facts, rnd.randint(0, 5))}
    if rnd.random() < 0.1:
        patient[rnd.choice(["params", "facts", "symptoms", "exam_results", "diseases"])] = junk()
    return patient


@pytest.mark.parametrize("seed", range(5))
def test_solver_never_crashes_on_random_input(seed):
    rnd = random.Random(seed)
    for _ in range(200):
        request = rnd.choice([{"patient": _random_patient(rnd)}, _random_patient(rnd), rnd.choice(JUNK),
                              {"patient": rnd.choice(JUNK)}])
        role = rnd.choice(["professional", "patient", "nursing", "student", "unknown_role"])
        solution = solve(request, role=role, kb=KB)
        assert solution["status"] in STATUSES
        json.dumps(solution, ensure_ascii=False)


def test_dialog_never_crashes_on_random_answers():
    rnd = random.Random(42)
    for _ in range(40):
        request = {"patient": _random_patient(rnd)}
        result = run_dialog(request, lambda item: rnd.choice([None, "да", "нет", "7", "x", 1, "2", "nan"]), kb=KB)
        assert result.solution["status"] in STATUSES
        apply_answers(request, {rnd.choice(list(KB.schema.parameters)): rnd.choice(JUNK)}, KB)


@pytest.mark.parametrize("params", [3.5, [1, 2], True, "sbp=120"])
def test_params_must_be_a_mapping(params):
    solution = solve({"patient": {"age": 40, "params": params}}, kb=KB)
    assert solution["status"] == "invalid"
    assert any(i["code"] == "BAD_INPUT" for i in solution["input_issues"])


@pytest.mark.parametrize("value", [float("nan"), float("inf"), "nan"])
def test_non_finite_numbers_are_rejected(value):
    solution = solve({"patient": {"age": 40, "params": {"sbp": value}}}, kb=KB)
    assert solution["status"] == "invalid"
    assert any(i["code"] == "BAD_VALUE" for i in solution["input_issues"])

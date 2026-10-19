"""Тесты уточняющего диалога, полей ввода вопросов и ограничений входных данных."""

from __future__ import annotations

import copy
import json

import pytest

from src.schema import Schema
from src.solver import apply_answers, load_default_kb, pending_inputs, run_dialog, solve
from src.solver.engine import InferenceEngine
from src.solver.facts import check_input_constraints, parse_case
from src.solver.inputs import describe_input, kind_of, known_atoms

PNEUMONIA_NO_UREA = {"patient": {"age": 70, "features": ["cough.productive", "fever.chills"],
                                 "params": {"rr": 24, "sbp": 110, "dbp": 70, "spo2": 95},
                                 "facts": {"confusion": False}}}


@pytest.fixture(scope="module")
def kb():
    return load_default_kb()


# ------------------------------------------------------------------ поля ввода
def test_input_kinds_resolved_from_vocabulary(kb):
    assert kind_of("urea", kb) == "param"
    assert kind_of("smoker", kb) == "fact"
    assert kind_of("chest_pain.at_rest", kb) == "feature"
    assert kind_of("DIAG-SYMPTOM-002", kb) == "symptom"
    assert kind_of("DIAG-EXAM-002", kb) == "exam_result"
    assert kind_of("no_such_code", kb) is None


def test_describe_input_carries_type_and_limits(kb):
    urea = describe_input("urea", kb)
    assert urea["type"] == "number" and urea["unit"] == "ммоль/л" and urea["min"] < urea["max"]
    ecg = describe_input("DIAG-EXAM-002", kb)
    assert ecg["type"] == "choice" and any(o["value"] == "st_elevation" for o in ecg["options"])
    assert describe_input("confusion", kb)["type"] == "boolean"


def test_known_atoms_extracts_codes_in_order():
    node = {"all": [{"symptom": "X"}, {"not": {"known": "spo2"}}, {"any": [{"not": {"known": "rr"}}, {"known": "spo2"}]}]}
    assert known_atoms(node) == ["spo2", "rr"]


def test_every_question_input_has_code_and_known_kind(kb):
    for patient in (PNEUMONIA_NO_UREA["patient"], {"age": 50, "symptoms": ["DIAG-SYMPTOM-001"]},
                    {"age": 60, "features": ["chest_pain.exertional"]}):
        solution = solve({"patient": patient}, kb=kb)
        for question in solution["questions"]:
            assert len(question["ask"]) == len(question["inputs"])
            for item in question["inputs"]:
                assert kind_of(item["code"], kb) == item["kind"]


def test_clarification_question_gets_inputs_from_known_atoms(kb):
    solution = solve({"patient": {"age": 50, "symptoms": ["DIAG-SYMPTOM-001"]}}, kb=kb)
    clarifications = [q for q in solution["questions"] if q["kind"] == "clarification"]
    assert clarifications, "ожидался запрос измерить АД"
    assert any(i["code"] == "sbp" for q in clarifications for i in q["inputs"])


def test_scale_question_asks_missing_urea(kb):
    solution = solve(PNEUMONIA_NO_UREA, kb=kb)
    codes = [i["code"] for i in pending_inputs(solution)]
    assert "urea" in codes


def test_solution_with_inputs_is_json_serializable(kb):
    json.dumps(solve(PNEUMONIA_NO_UREA, kb=kb), ensure_ascii=False)


# ------------------------------------------------------------------ подстановка ответов
def test_apply_answers_does_not_mutate_original(kb):
    original = copy.deepcopy(PNEUMONIA_NO_UREA)
    new, issues = apply_answers(PNEUMONIA_NO_UREA, {"urea": "8,5"}, kb)
    assert PNEUMONIA_NO_UREA == original
    assert new["patient"]["params"]["urea"] == 8.5 and not issues


def test_apply_answers_places_each_kind(kb):
    new, issues = apply_answers({"patient": {"age": 60}}, {
        "smoker": "да", "chest_pain.at_rest": True, "DIAG-SYMPTOM-004": "нет",
        "DIAG-EXAM-002": "st_elevation", "troponin_positive": "нет", "sbp": 150}, kb)
    patient = new["patient"]
    assert not issues
    assert patient["facts"]["smoker"] is True
    assert patient["features"] == ["chest_pain.at_rest"]
    assert patient["denied_symptoms"] == ["DIAG-SYMPTOM-004"]
    assert patient["exam_results"]["DIAG-EXAM-002"] == "st_elevation"
    assert patient["params"]["troponin_positive"] is False and patient["params"]["sbp"] == 150


def test_apply_answers_choice_by_option_number(kb):
    new, _ = apply_answers({"patient": {}}, {"DIAG-EXAM-002": "2"}, kb)
    ecg = describe_input("DIAG-EXAM-002", kb)
    assert new["patient"]["exam_results"]["DIAG-EXAM-002"] == ecg["options"][1]["value"]


def test_apply_answers_reports_bad_values(kb):
    _, issues = apply_answers({"patient": {}}, {"urea": "много", "smoker": "иногда", "xyz": 1}, kb)
    assert {i["code"] for i in issues} == {"BAD_ANSWER", "UNKNOWN_INPUT"}
    assert len(issues) == 3


def test_feature_answer_switches_between_lists(kb):
    first, _ = apply_answers({"patient": {"denied_features": ["chest_pain.at_rest"]}}, {"chest_pain.at_rest": "да"}, kb)
    assert first["patient"]["features"] == ["chest_pain.at_rest"] and first["patient"]["denied_features"] == []


# ------------------------------------------------------------------ цикл диалога
def test_dialog_answer_completes_scale(kb):
    before = solve(PNEUMONIA_NO_UREA, kb=kb)
    assert all(s["id"] != "PROT-SCALE-004" or s["value"] is None for s in before["scales"])
    result = run_dialog(PNEUMONIA_NO_UREA, lambda item: 8 if item["code"] == "urea" else None, kb=kb)
    curb = next(s for s in result.solution["scales"] if s["id"] == "PROT-SCALE-004")
    assert curb["value"] == 2
    assert result.rounds and result.rounds[0].answers == {"urea": 8}
    assert "urea" not in [i["code"] for i in pending_inputs(result.solution)]


def test_dialog_stops_when_nothing_answered(kb):
    calls = []
    result = run_dialog({"patient": {"age": 50, "symptoms": ["DIAG-SYMPTOM-001"]}},
                        lambda item: calls.append(item["code"]), kb=kb)
    assert result.rounds == [] and calls
    assert len(calls) == len(set(calls)), "одно поле не должно спрашиваться дважды"


def test_dialog_can_escalate_urgency(kb):
    # Боль в груди без подробностей; ответ «боль в покое» должен дать экстренную срочность.
    request = {"patient": {"age": 62, "symptoms": ["DIAG-SYMPTOM-002"]}}
    answers = {"chest_pain.at_rest": "да", "symptom_duration_min": 30}
    result = run_dialog(request, lambda item: answers.get(item["code"]), kb=kb)
    assert result.solution["urgency"]["level"] == "emergency"


def test_dialog_respects_round_limit(kb):
    result = run_dialog(PNEUMONIA_NO_UREA, lambda item: None, kb=kb, max_rounds=0)
    assert result.rounds == []


def test_dialog_skips_refused_patient(kb):
    result = run_dialog({"patient": {"age": 7, "symptoms": ["DIAG-SYMPTOM-004"]}}, lambda item: 1, kb=kb)
    assert result.solution["status"] == "refused" and result.rounds == []


# ------------------------------------------------------------------ знания вне кода
def test_input_constraints_come_from_schema(kb):
    ids = {c["id"] for c in kb.schema.input_constraints}
    assert {"IC-001", "IC-002"} <= ids


def test_sbp_dbp_constraint(kb):
    parsed = parse_case({"patient": {"age": 40, "params": {"sbp": 90, "dbp": 95}}}, kb)
    assert any(i.code == "CONTRADICTION" and "90" in i.message for i in parsed.issues)
    ok = parse_case({"patient": {"age": 40, "params": {"sbp": 130}}}, kb)
    assert not ok.has_errors, "одно значение без пары не проверяется"


def test_pregnancy_constraint_unknown_age_is_not_violation(kb):
    assert parse_case({"patient": {"facts": {"pregnant": True}, "params": {"sbp": 120}}}, kb).has_errors is False
    assert parse_case({"patient": {"age": 8, "facts": {"pregnant": True}}}, kb).has_errors is True


def test_constraint_list_is_extensible_without_code(kb):
    raw = copy.deepcopy(kb.schema.raw)
    raw["input_constraints"].append({"id": "IC-999", "compare": {"left": "hr", "op": "<", "right": "sbp"},
                                     "message": "ЧСС {hr} больше САД {sbp}"})
    schema = Schema(raw=raw, path=kb.schema.path)
    assert not schema.self_check()
    facts = parse_case({"patient": {"age": 40, "params": {"hr": 200, "sbp": 150, "dbp": 90}}}, kb).facts
    assert check_input_constraints(facts, schema) == ["ЧСС 200 больше САД 150"]


def test_schema_self_check_rejects_bad_constraint(kb):
    raw = copy.deepcopy(kb.schema.raw)
    raw["input_constraints"].append({"id": "IC-998", "compare": {"left": "nope", "op": "?", "right": "sbp"}})
    problems = Schema(raw=raw, path=kb.schema.path).self_check()
    assert any("nope" in p for p in problems) and any("оператор" in p for p in problems)
    assert any("message" in p for p in problems)


def test_working_diagnosis_threshold_from_schema(kb):
    assert InferenceEngine(kb).working_diagnosis_score == kb.schema.solver_setting("working_diagnosis_score", None)
    facts = parse_case(PNEUMONIA_NO_UREA, kb).facts
    strict = InferenceEngine(kb, working_diagnosis_score=100).run(facts)
    assert strict.working_diagnoses == []


def test_routing_reference_is_not_reported_as_protocol(kb):
    solution = solve({"patient": {"age": 25, "symptoms": ["DIAG-SYMPTOM-004"], "features": ["headache.meningism"]}}, kb=kb)
    assert all(kb.get(p["id"]).category in ("protocol", "emergency_p") for p in solution["protocols"])
    assert any(d["id"] == "PROT-ROUTING-006" for d in solution["routing"]["decisions"])


def test_validator_checks_forbid_conditions(kb):
    from src.cli import build_repository
    from src.validator import KnowledgeBaseValidator

    raw = copy.deepcopy(kb.schema.raw)
    raw["input_constraints"].append({"id": "IC-997", "forbid": {"param": "no_such_param", "op": ">", "value": 1},
                                     "message": "тест"})
    schema = Schema(raw=raw, path=kb.schema.path)
    report = KnowledgeBaseValidator(build_repository(), schema=schema).validate()
    assert any(i.code == "CONSTRAINT_BAD_CONDITION" and i.card_id == "IC-997" for i in report.errors)


# ------------------------------------------------------------------ факты, выводимые по словарю схемы
def test_hypotension_derived_from_measured_sbp(kb):
    solution = solve({"patient": {"age": 60, "symptoms": ["DIAG-SYMPTOM-002"], "params": {"sbp": 80, "dbp": 50}}}, kb=kb)
    assert solution["urgency"]["level"] == "emergency"
    assert "RULE-PROT-001" in solution["fired_rules"]
    assert any(step["kind"] == "input" and step["source"] == "hypotension" for step in solution["trace"])


def test_normal_sbp_derives_no_hypotension(kb):
    facts = parse_case({"patient": {"age": 60, "params": {"sbp": 125, "dbp": 80}}}, kb).facts
    assert facts.facts["hypotension"] is False


def test_confusion_derived_from_gcs(kb):
    solution = solve({"patient": {"age": 40, "symptoms": ["DIAG-SYMPTOM-004"], "params": {"gcs": 12}}}, kb=kb)
    assert solution["urgency"]["level"] == "emergency" and "RULE-PROT-003" in solution["fired_rules"]
    assert parse_case({"patient": {"params": {"gcs": 15}}}, kb).facts.facts["confusion"] is False


def test_measurement_wins_over_reported_fact(kb):
    parsed = parse_case({"patient": {"age": 60, "params": {"sbp": 80, "dbp": 50}, "facts": {"hypotension": False}}}, kb)
    assert parsed.facts.facts["hypotension"] is True
    assert any(i.code == "INCONSISTENT_FACT" for i in parsed.issues) and not parsed.has_errors


def test_unknown_measurement_leaves_fact_unknown(kb):
    assert "hypotension" not in parse_case({"patient": {"age": 60}}, kb).facts.facts


def test_known_disease_fact_establishes_diagnosis(kb):
    solution = solve({"patient": {"age": 55, "params": {"sbp": 150, "dbp": 95}, "facts": {"known_hypertension": True}}}, kb=kb)
    assert [d["id"] for d in solution["working_diagnoses"]] == ["DIAG-DISEASE-001"]
    assert "RULE-PROT-008" in solution["fired_rules"]
    false_fact = parse_case({"patient": {"facts": {"known_hypertension": False}}}, kb).facts
    assert "DIAG-DISEASE-001" not in false_fact.diseases


def test_every_implied_disease_mapping_is_a_disease_card(kb):
    implied = {spec["implies_disease"] for spec in kb.schema.facts.values() if spec.get("implies_disease")}
    assert implied and all(kb.get(d).category == "disease" for d in implied)


def test_validator_rejects_bad_fact_vocabulary(kb):
    from src.cli import build_repository
    from src.validator import KnowledgeBaseValidator

    raw = copy.deepcopy(kb.schema.raw)
    raw["facts"]["obesity"]["derived_from"] = {"fact": "smoker"}
    raw["facts"]["smoker"]["implies_disease"] = "PROT-SCALE-001"
    report = KnowledgeBaseValidator(build_repository(), schema=Schema(raw=raw, path=kb.schema.path)).validate()
    codes = {(i.code, i.card_id) for i in report.errors}
    assert ("FACT_BAD_DERIVATION", "obesity") in codes and ("FACT_BAD_DISEASE", "smoker") in codes


def test_safety_question_anchor_does_not_depend_on_branch_order(kb):
    from src.conditions import PatientFacts
    from src.solver.questions import _partially_met

    class Memory:
        facts = PatientFacts(features={"headache.recurrent_attacks"}, diseases={"DIAG-DISEASE-005"})

    a = {"all": [{"any": [{"disease": "DIAG-DISEASE-005"}, {"feature": "headache.recurrent_attacks"}]},
                 {"feature": "headache.over_72h"}]}
    b = {"all": [{"any": [{"feature": "headache.recurrent_attacks"}, {"disease": "DIAG-DISEASE-005"}]},
                 {"feature": "headache.over_72h"}]}
    assert _partially_met(a, Memory, kb) and _partially_met(b, Memory, kb)
    only_background = {"all": [{"disease": "DIAG-DISEASE-005"}, {"feature": "headache.over_72h"}]}
    assert not _partially_met(only_background, Memory, kb), "фоновый диагноз — не якорь"
    negated = {"all": [{"not": {"feature": "headache.recurrent_attacks"}}, {"feature": "headache.over_72h"}]}
    assert not _partially_met(negated, Memory, kb), "отрицаемое проявление — не якорь"

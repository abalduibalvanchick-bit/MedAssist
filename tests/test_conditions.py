"""Тесты схемы v2 и мини-языка условий."""

from __future__ import annotations

import pytest

from src.conditions import (
    ConditionError,
    PatientFacts,
    Truth,
    collect_references,
    describe,
    evaluate,
    missing_inputs,
    validate_condition,
)
from src.schema import load_schema

schema = load_schema()


# ---------------------------------------------------------------- схема
def test_schema_loads_and_is_consistent():
    assert schema.version == 2
    assert schema.self_check() == []


def test_schema_domains_and_categories():
    assert schema.domain_codes == {"diag", "pharm", "prot", "glb"}
    assert schema.categories["scale"].domain == "prot"
    assert schema.categories["scale"].folder == "scales"
    assert schema.normalize_domain("protocols") == "prot"
    assert schema.normalize_domain("therapy") == "pharm"
    assert schema.normalize_category("drug_class") == "drugclass"


def test_every_relation_has_consistent_inverse():
    rel = schema.relation_types
    for name, info in rel.items():
        inverse = info.inverse_name()
        assert inverse in rel, name
        assert rel[inverse].inverse_name() == name, name


def test_legacy_relation_aliases_point_to_v2_types():
    for alias, target in schema.legacy_relation_aliases.items():
        assert target["type"] in schema.relation_types, alias
        assert schema.normalize_relation_type(alias) == target["type"]


def test_machine_layer_defined_for_every_category():
    for category in schema.categories:
        assert schema.machine_layer(category) is not None, category


# --------------------------------------------------- статическая проверка
def test_valid_condition_has_no_issues():
    cond = {"all": [
        {"symptom": "DIAG-SYMPTOM-002"},
        {"param": "sbp", "op": ">=", "value": 180},
        {"not": {"fact": "pregnant"}},
        {"at_least": {"n": 1, "of": [{"fact": "smoker"}, {"param": "age", "op": "between", "value": [18, 65]}]}},
    ]}
    assert validate_condition(cond, schema) == []


@pytest.mark.parametrize("cond, fragment", [
    ({}, "непустым словарём"),
    ({"symptom": "DIAG-SYMPTOM-002", "all": []}, "одновременно"),
    ({"param": "unknown_param", "op": ">", "value": 1}, "Неизвестный параметр"),
    ({"param": "sbp", "op": "~", "value": 1}, "Недопустимый оператор"),
    ({"param": "sbp", "op": "between", "value": [200, 100]}, "min больше max"),
    ({"fact": "not_a_fact"}, "Неизвестный факт"),
    ({"symptom": "PROT-SCALE-001"}, "категории"),
    ({"feature": "no_dot"}, "<symptom>.<feature>"),
    ({"at_least": {"n": 3, "of": [{"fact": "smoker"}]}}, "больше числа альтернатив"),
    ({"scale_category": "PROT-SCALE-001"}, "требует ключ value"),
    ({"unknown_atom": 1}, "Неизвестный узел"),
])
def test_invalid_conditions_are_reported(cond, fragment):
    issues = validate_condition(cond, schema)
    assert issues, cond
    assert any(fragment in issue.message for issue in issues), [i.message for i in issues]


def test_validation_uses_known_ids_when_provided():
    cond = {"symptom": "DIAG-SYMPTOM-999"}
    assert validate_condition(cond, schema) == []
    issues = validate_condition(cond, schema, known_ids={"DIAG-SYMPTOM-001"})
    assert any("несуществующую" in i.message for i in issues)


# -------------------------------------------------------------- оценка
def facts_for_acs() -> PatientFacts:
    return PatientFacts(
        symptoms={"DIAG-SYMPTOM-002"},
        features={"chest_pain.pressing"},
        facts={"smoker": True, "pregnant": False},
        params={"sbp": 190, "age": 62, "troponin_positive": True},
        diseases={"DIAG-DISEASE-001"},
    )


def test_atoms_evaluate_true_false_unknown():
    f = facts_for_acs()
    assert evaluate({"symptom": "DIAG-SYMPTOM-002"}, f, schema).is_true()
    assert evaluate({"symptom": "DIAG-SYMPTOM-003"}, f, schema).is_unknown()
    assert evaluate({"fact": "pregnant"}, f, schema).is_false()
    assert evaluate({"fact": "on_anticoagulants"}, f, schema).is_unknown()
    assert evaluate({"param": "sbp", "op": ">=", "value": 180}, f, schema).is_true()
    assert evaluate({"param": "hr", "op": ">", "value": 100}, f, schema).is_unknown()
    assert evaluate({"param": "age", "op": "between", "value": [60, 70]}, f, schema).is_true()
    assert evaluate({"param": "troponin_positive"}, f, schema).is_true()
    assert evaluate({"disease": "DIAG-DISEASE-001"}, f, schema).is_true()
    assert evaluate({"redflag": "DIAG-REDFLAG-001"}, f, schema).is_unknown()


def test_closed_world_turns_unknown_into_false():
    f = facts_for_acs()
    f.closed_world = True
    assert evaluate({"symptom": "DIAG-SYMPTOM-003"}, f, schema).is_false()
    assert evaluate({"fact": "on_anticoagulants"}, f, schema).is_false()


def test_denied_symptom_is_false_in_open_world():
    f = PatientFacts(denied_symptoms={"DIAG-SYMPTOM-003"})
    assert evaluate({"symptom": "DIAG-SYMPTOM-003"}, f, schema).is_false()


def test_three_valued_combinators():
    f = facts_for_acs()
    known_true = {"symptom": "DIAG-SYMPTOM-002"}
    known_false = {"fact": "pregnant"}
    unknown = {"symptom": "DIAG-SYMPTOM-003"}
    assert evaluate({"all": [known_true, unknown]}, f, schema).is_unknown()
    assert evaluate({"all": [known_false, unknown]}, f, schema).is_false()
    assert evaluate({"any": [known_true, unknown]}, f, schema).is_true()
    assert evaluate({"any": [known_false, unknown]}, f, schema).is_unknown()
    assert evaluate({"not": unknown}, f, schema).is_unknown()
    assert evaluate({"not": known_false}, f, schema).is_true()


def test_at_least_semantics():
    f = facts_for_acs()
    t, fl, u = {"symptom": "DIAG-SYMPTOM-002"}, {"fact": "pregnant"}, {"symptom": "DIAG-SYMPTOM-003"}
    assert evaluate({"at_least": {"n": 1, "of": [t, fl]}}, f, schema).is_true()
    assert evaluate({"at_least": {"n": 2, "of": [t, fl]}}, f, schema).is_false()
    assert evaluate({"at_least": {"n": 2, "of": [t, u]}}, f, schema).is_unknown()
    assert evaluate({"at_least": {"n": 2, "of": [t, u, fl]}}, f, schema).is_unknown()


def test_evaluate_rejects_malformed_node():
    with pytest.raises(ConditionError):
        evaluate({"bogus": 1}, PatientFacts(), schema)


def test_trace_records_every_node():
    from src.conditions import EvalTrace
    trace: list[EvalTrace] = []
    cond = {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}
    evaluate(cond, facts_for_acs(), schema, trace=trace)
    paths = [t.path for t in trace]
    assert "$.all[0]" in paths and "$.all[1]" in paths and "$" in paths
    assert trace[-1].result is Truth.TRUE


def test_missing_inputs_lists_only_unknown_atoms():
    cond = {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "hr", "op": ">", "value": 100}, {"fact": "on_anticoagulants"}]}
    missing = missing_inputs(cond, facts_for_acs(), schema)
    assert missing.params == {"hr"}
    assert missing.facts == {"on_anticoagulants"}
    assert missing.card_ids == set()


# -------------------------------------------------------------- ссылки
def test_collect_references():
    cond = {"any": [
        {"symptom": "DIAG-SYMPTOM-002"},
        {"all": [{"param": "sbp", "op": ">=", "value": 180}, {"fact": "smoker"}, {"feature": "chest_pain.pressing"}]},
        {"scale": "PROT-SCALE-001", "op": ">=", "value": 4},
    ]}
    refs = collect_references(cond, schema)
    assert refs.card_ids == {"DIAG-SYMPTOM-002", "PROT-SCALE-001"}
    assert refs.params == {"sbp"}
    assert refs.facts == {"smoker"}
    assert refs.features == {"chest_pain.pressing"}


def test_describe_is_russian_and_uses_labels():
    cond = {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}, {"not": {"fact": "pregnant"}}]}
    text = describe(cond, schema, labels={"DIAG-SYMPTOM-002": "Боль в груди"})
    assert "Боль в груди" in text
    assert "Систолическое АД >= 180" in text
    assert "НЕ Беременность" in text

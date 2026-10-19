"""Маршрутизация по таблицам решений (задача T1): покрытие таблиц сценариями и свойства модуля."""

from __future__ import annotations

import pytest

from src.solver import load_default_kb, run_dialog, solve
from tests.solver_cases import load_cases

KB = load_default_kb()
CASES = load_cases()


def _chosen_rows() -> set[tuple[str, object]]:
    rows = set()
    for case in CASES:
        solution = solve({"patient": case.get("patient") or {}}, kb=KB)
        for d in (solution.get("routing") or {}).get("decisions", []):
            rows.add((d["id"], "default" if d["row"] is None else d["row"]))
    return rows


def test_every_routing_row_and_default_is_covered_by_a_scenario():
    """Критерий готовности T1: каждая строка каждой таблицы и маршрут по умолчанию — в сценарии."""
    covered = _chosen_rows()
    missing = []
    for card in KB.category("routing"):
        for row in [*range(len(card.metadata.get("decisions") or [])), "default"]:
            if (card.id, row) not in covered:
                missing.append(f"{card.id}:{row if row == 'default' else row + 1}")
    assert not missing, f"не покрыты сценариями: {missing}"


PNEUMONIA = {"patient": {"age": 70, "features": ["cough.productive", "fever.chills"],
                         "params": {"rr": 24, "sbp": 110, "dbp": 70, "urea": 8, "spo2": 95},
                         "facts": {"confusion": False}}}


def test_pneumonia_curb2_elderly_is_hospitalized():
    routing = solve(PNEUMONIA, kb=KB)["routing"]
    assert (routing["route"], routing["timeframe"]) == ("hospitalization", "в течение суток")
    assert routing["decisions"][0]["row"] == 1


def test_provisional_route_resolved_by_dialog_both_ways():
    no_dyspnea = run_dialog(PNEUMONIA, lambda item: "нет" if item["code"] == "DIAG-SYMPTOM-003" else None, kb=KB)
    assert no_dyspnea.solution["routing"]["route"] == "hospitalization"
    assert no_dyspnea.solution["routing"]["provisional"] is False
    cyanosis = run_dialog(PNEUMONIA, lambda item: "да" if item["code"] == "dyspnea.cyanosis" else None, kb=KB)
    assert cyanosis.solution["routing"]["route"] == "emergency"
    assert cyanosis.solution["urgency"]["level"] == "emergency"


def test_routing_question_asks_signs_of_unresolved_red_flag():
    questions = [q for q in solve(PNEUMONIA, kb=KB)["questions"] if q["kind"] == "routing"]
    codes = {i["code"] for q in questions for i in q["inputs"]}
    assert {"DIAG-SYMPTOM-003", "dyspnea.cyanosis"} <= codes


def test_excluded_red_flag_does_not_make_route_provisional():
    # САД 165 и ДАД 95 исключают осложнённый криз: строка 1 таблицы АГ ложна, маршрут окончательный.
    solution = solve({"patient": {"age": 62, "params": {"sbp": 165, "dbp": 95},
                                  "facts": {"smoker": True, "known_diabetes": False, "known_hypertension": True}}}, kb=KB)
    assert solution["routing"]["route"] == "urgent_referral" and solution["routing"]["provisional"] is False


def test_emergency_urgency_without_table_gives_emergency_route():
    solution = solve({"patient": {"age": 40, "symptoms": ["DIAG-SYMPTOM-004"], "params": {"gcs": 12}}}, kb=KB)
    assert solution["urgency"]["level"] == "emergency"
    assert solution["routing"]["route"] == "emergency" and solution["routing"]["decisions"] == []


def test_route_never_lowers_urgency_and_next_protocol_added():
    solution = solve({"patient": {"age": 64, "symptoms": ["DIAG-SYMPTOM-002"], "params": {"sbp": 200, "dbp": 115},
                                  "facts": {"known_hypertension": True}}}, kb=KB)
    assert solution["urgency"]["level"] == "emergency"
    assert any(p["id"] == "PROT-EMERGENCY_P-001" for p in solution["protocols"])


def test_refused_patient_has_no_route():
    solution = solve({"patient": {"age": 7, "symptoms": ["DIAG-SYMPTOM-004"]}}, kb=KB)
    assert solution["status"] == "refused" and solution["routing"]["route"] is None


def test_patient_role_sees_route_without_decision_tables():
    routing = solve(PNEUMONIA, role="patient", kb=KB)["routing"]
    assert set(routing) == {"route", "label", "timeframe", "provisional"}
    assert routing["label"] == "госпитализация"


def test_every_routing_step_is_traced():
    solution = solve(PNEUMONIA, kb=KB)
    traced = {t["source"] for t in solution["trace"] if t["kind"] == "routing"}
    assert {d["id"] for d in solution["routing"]["decisions"]} <= traced


@pytest.mark.parametrize("severity_key", ["route_severity", "route_urgency", "urgency_route", "route_labels"])
def test_routing_settings_come_from_schema(severity_key):
    assert KB.schema.solver_setting(severity_key, None), f"solver.{severity_key} должен быть задан в схеме"

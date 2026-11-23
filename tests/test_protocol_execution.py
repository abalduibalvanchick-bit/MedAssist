"""Проверка протоколов через публичный solve, включая каждую ветвь шести карточек."""
import pytest

from src.solver import load_default_kb, solve
from tests.solver_cases import load_cases

KB = load_default_kb()
PATIENTS = {case["id"]: case["patient"] for case in load_cases()}
# Сумма баллов шкалы риска диабета >= 15.
PATIENTS["very_high"] = {
    "age": 70, "params": {"diabetes_duration_years": 12, "bmi": 32, "hba1c": 9,
                          "sbp": 150, "egfr": 45, "microalbuminuria": True},
    "facts": {"smoker": True, "prior_cv_event": True},
}
# Для каждой ветви — вход с известным диагнозом и ожидаемый переход.
BRANCHES = [
    ("001", "TYP-14", "EMERGENCY_P-001"), ("001", "BND-03", "ROUTING-001"), ("001", "TYP-16", "ROUTING-001"),
    ("002", "TYP-08", "EMERGENCY_P-002"), ("002", "TYP-28", "ROUTING-002"), ("002", "very_high", "ROUTING-002"),
    ("003", "TYP-01", "EMERGENCY_P-003"), ("003", "TYP-18", "ROUTING-003"),
    ("004", "BND-01", "EMERGENCY_P-004"), ("004", "BND-08", "ROUTING-004"),
    ("005", "BND-01", "EMERGENCY_P-005"), ("005", "TYP-19", "ROUTING-005"),
    ("006", "BND-05", "ROUTING-006"), ("006", "TYP-15", "EMERGENCY_P-006"), ("006", "TYP-20", "ROUTING-006"),
]


@pytest.mark.parametrize("suffix,case,target", BRANCHES)
def test_branch_transition(suffix, case, target):
    card = KB.get("PROT-PROTOCOL-" + suffix)
    cases = [c for s, c, _ in BRANCHES if s == suffix]
    assert len(cases) == len(card.metadata["branches"])
    request = {"patient": PATIENTS[case] | {"diseases": card.metadata["for"]}}
    result = solve(request, kb=KB)
    plans = {p["id"]: p for p in result["protocols"]}
    branch = plans[card.id]["branches"][cases.index(case)]
    assert branch["truth"] == "true"
    assert branch["then"] == "PROT-" + target
    assert branch["evidence"]
    if target.startswith("EMERGENCY"):
        emergency = plans[branch["then"]]
        if emergency["status"] == "applicable":
            assert emergency["phases"] == KB.get(branch["then"]).metadata["phases"]
        else:
            assert emergency["entry"]["truth"] != "true" and "phases" not in emergency


def test_missing_data_and_repeat_evaluation():
    request = {"diseases": ["DIAG-DISEASE-006"], "age": 58}
    def plan_at(**params):
        result = solve({"patient": request | {"params": params}}, kb=KB)
        plan = next(p for p in result["protocols"] if p["id"] == "PROT-PROTOCOL-002")
        step = next(s for s in plan["steps"] if s["id"] == "metformin")
        return result, step, plan["targets"][0]
    result, step, target = plan_at()
    assert step["status"] == "conditional" and target["status"] == "unknown"
    assert any(q["kind"] == "protocol" and any(i["code"] == "egfr" for i in q["inputs"]) for q in result["questions"])
    assert result["follow_up"][0]["schedule"]
    _, step, target = plan_at(egfr=29, hba1c=7)
    assert step["status"] == "not_required" and target["status"] == "not_achieved"
    _, step, target = plan_at(egfr=30, hba1c=6.9)
    assert step["status"] == "applicable" and target["status"] == "achieved"
    patient = solve({"patient": request}, role="patient", kb=KB)
    assert "protocols" not in patient and "follow_up" not in patient
    assert all(q["kind"] != "protocol" for q in patient["questions"])

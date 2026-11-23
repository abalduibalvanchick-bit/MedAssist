from src.solver import solve
from tests.solver_cases import load_cases


def test_ranking_keeps_rule_weight_and_counts_each_manifestation_once():
    patient = {"age": 70, "features": ["cough.acute", "cough.productive", "fever.chills"]}
    def pneumonia(extra):
        result = solve({"patient": patient | extra})
        return next(h for h in result["hypotheses"] if h["id"] == "DIAG-DISEASE-003")
    base = pneumonia({})
    assert base["rank_score"] == base["score"] + 6
    denied = pneumonia({"denied_symptoms": ["DIAG-SYMPTOM-003"]})
    assert denied["rank_score"] == denied["score"] + 5
    assert [a["contribution"] for a in denied["arguments"]] == [3, 3, -1]


def test_critical_leader_is_preserved_when_disease_has_more_presentation_points():
    patient = next(c["patient"] for c in load_cases() if c["id"] == "TYP-01")
    first, second, *_ = solve({"patient": patient})["hypotheses"]
    assert first["id"] == "DIAG-EMERGENCY-001" and first["time_critical_priority"]
    assert second["rank_score"] > first["rank_score"]

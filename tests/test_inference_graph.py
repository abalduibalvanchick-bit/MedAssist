"""Граф отражает реальные зависимости и версии фактов прямого вывода."""

import yaml

from src.solver import solve
from src.web.scenarios import ROOT


def scenario():
    return yaml.safe_load((ROOT / "examples" / "pneumonia_no_urea.yaml").read_text(encoding="utf-8"))


def test_graph_connects_inputs_to_conclusions_and_preserves_previous_versions():
    solution = solve(scenario(), include_graph=True)
    graph = solution["inference_graph"]
    nodes, steps = graph["nodes"], graph["steps"]
    by_source = {step["source"]: step for step in steps if step["source"].startswith("RULE-")}
    first = by_source["RULE-DIAG-005"]
    second = by_source["RULE-DIAG-004"]
    workup = by_source["RULE-DIAG-043"]
    assert {nodes[i]["code"] for i in first["inputs"]} == {"DIAG-SYMPTOM-008", "DIAG-SYMPTOM-004", "rr"}
    declared = next(nodes[i] for i in first["outputs"] if nodes[i]["kind"] == "disease")
    old_weight = next(nodes[i] for i in first["outputs"] if nodes[i]["kind"] == "hypothesis")
    new_weight = next(nodes[i] for i in second["outputs"] if nodes[i]["kind"] == "hypothesis")
    assert old_weight["id"] in second["inputs"]
    assert (old_weight["value"], new_weight["value"]) == ("3 балл.", "6 балл.")
    assert declared["id"] in workup["inputs"]
    assert any(nodes[i]["code"] == "urea" and nodes[i]["absent"] for i in workup["inputs"])
    scale = next(step for step in steps if step["source"] == "PROT-SCALE-004")
    assert any(nodes[i]["value"].startswith("1–2") for i in scale["outputs"])
    assert not any(step["source"] == "PROT-ROUTING-004" for step in steps)
    for step in steps:
        assert all(nodes[i]["step"] < step["step"] for i in step["inputs"])
        assert all(nodes[i]["step"] == step["step"] for i in step["outputs"])
    assert [step["iteration"] for step in steps] == sorted(step["iteration"] for step in steps)


def test_graph_is_optional_and_excluded_from_patient_view():
    request = scenario()
    plain = solve(request)
    captured = solve(request, include_graph=True)
    captured.pop("inference_graph")
    plain["stats"].pop("time_ms")
    captured["stats"].pop("time_ms")
    assert plain == captured
    assert "inference_graph" not in solve(request, role="patient", include_graph=True)

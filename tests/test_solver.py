"""Тесты решателя: сценарии tests/cases и свойства ядра."""

from __future__ import annotations

import json

import pytest

from src.solver import load_default_kb, solve
from src.solver.engine import InferenceEngine
from src.solver.facts import parse_case
from tests.solver_cases import check_case, load_cases

CASES = load_cases()


@pytest.fixture(scope="module")
def kb():
    return load_default_kb()


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_case(case, kb):
    solution = solve({"patient": case.get("patient") or {}}, role=case.get("role", "professional"), kb=kb)
    fails = check_case(case, solution)
    assert not fails, f"{case['id']} {case['title']}: " + "; ".join(fails)


def test_case_groups_are_represented():
    groups = {c["group"] for c in CASES}
    assert groups == {"typical", "boundary", "negative"}


def test_determinism(kb):
    patient = CASES[0]["patient"]
    first = solve({"patient": patient}, kb=kb)
    for _ in range(5):
        again = solve({"patient": patient}, kb=kb)
        for key in ("status", "urgency", "hypotheses", "fired_rules", "trace", "questions"):
            assert again[key] == first[key]


def test_solution_is_json_serializable(kb):
    for case in CASES:
        json.dumps(solve({"patient": case.get("patient") or {}}, kb=kb), ensure_ascii=False)


def test_patient_role_hides_professional_details(kb):
    solution = solve({"patient": CASES[0]["patient"]}, role="patient", kb=kb)
    for key in ("hypotheses", "exams", "warnings", "trace", "explanation"):
        assert key not in solution
    assert solution["urgency"]["level"] == "emergency"
    assert any("103" in text for text in solution["disclaimer"])


def test_bad_role_is_rejected(kb):
    assert solve({"patient": {}}, role="admin", kb=kb)["status"] == "invalid"


def test_feature_implies_symptom(kb):
    parsed = parse_case({"features": ["chest_pain.pressing"]}, kb)
    assert "DIAG-SYMPTOM-002" in parsed.facts.symptoms


def test_every_trace_step_has_basis(kb):
    solution = solve({"patient": CASES[0]["patient"]}, kb=kb)
    for step in solution["trace"]:
        assert step["because"], step


def test_fixpoint_terminates_and_rules_fire_once(kb):
    parsed = parse_case(CASES[0]["patient"], kb)
    memory = InferenceEngine(kb).run(parsed.facts)
    assert memory.iterations < 20
    assert len(memory.fired_rules) == len(set(memory.fired_rules))


def test_no_domain_constants_in_solver_code():
    """Знания хранятся в базе: в коде решателя (кроме документации) нет ID карточек и правил."""
    import ast
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / "src" / "solver"
    pattern = re.compile(r"(DIAG|PHARM|PROT|GLB|RULE)-[A-Z_]+-\d{3}")
    offenders = []
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                      if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))
                      and n.body and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings \
                    and pattern.search(node.value):
                offenders.append(f"{path.name}: {node.value[:40]}")
    assert offenders == []

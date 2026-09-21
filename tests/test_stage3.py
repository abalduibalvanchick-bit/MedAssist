"""Тесты инструментов наполнения и проверок этапа 3."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import apply_patch  # noqa: E402
import sync_relations  # noqa: E402
from src.conditions import PatientFacts, evaluate  # noqa: E402
from src.machine_refs import iter_machine_refs  # noqa: E402
from src.markdown_parser import parse_markdown_file  # noqa: E402
from src.repository import KnowledgeRepository  # noqa: E402
from src.schema import load_schema  # noqa: E402
from src.validator import KnowledgeBaseValidator  # noqa: E402

schema = load_schema()

COMMON = {
    "schema_version": 2, "body_system": ["cardiovascular"], "tags": ["t"], "urgency": "routine",
    "access_level": "professional", "target_specialist": ["therapist"], "age_group": ["adult"],
    "sources": ["A", "B"], "clinical_guidelines": ["КР"], "last_medical_review": "2026-09-01",
    "medical_reviewer": "модельная верификация (учебный проект)", "author": "Инженер знаний №1",
    "version": "2.0", "date_created": "2026-09-01", "date_updated": "2026-09-01",
    "status": "medical_review", "disclaimer": True,
}
BODY = "\n# Заголовок\n\n" + "Содержательный текст карточки. " * 40 + "\n"


def put(kb: Path, rel: str, meta: dict) -> Path:
    p = kb / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n" + BODY, encoding="utf-8")
    return p


@pytest.fixture
def kb(tmp_path: Path) -> Path:
    kb = tmp_path / "kb"
    (kb / "_schema").mkdir(parents=True)
    shutil.copy(ROOT / "kb" / "_schema" / "schema.yaml", kb / "_schema" / "schema.yaml")
    put(kb, "diag/symptoms/diag_symptom_chest_pain.md", {**COMMON, "id": "DIAG-SYMPTOM-001", "title": "Боль", "domain": "diag",
        "category": "symptom", "relations": [], "features": [{"code": "chest_pain.pressing", "label": "давящая"}]})
    put(kb, "diag/diseases/diag_disease_ihd.md", {**COMMON, "id": "DIAG-DISEASE-001", "title": "ИБС", "domain": "diag",
        "category": "disease", "relations": []})
    return kb


def validate(kb: Path):
    return KnowledgeBaseValidator(KnowledgeRepository(kb).load(), rules_root=kb / "rules").validate()


def codes(report, severity=None):
    return {i.code for i in report.issues if severity is None or i.severity == severity}


# ------------------------------------------------------------ apply_patch
def test_apply_patch_sets_fields_and_is_idempotent(kb):
    patch = {"DIAG-DISEASE-001": {
        "set": {"presentation": [{"symptom": "DIAG-SYMPTOM-001", "weight": 3, "frequency": "common", "features": ["chest_pain.pressing"]}]},
        "add_relations": [{"target": "DIAG-SYMPTOM-001", "type": "has_symptom"}],
        "add_sources": ["C"],
    }}
    log = apply_patch.apply(patch, kb, "2026-09-16", dry_run=False)
    assert log and log[0].startswith("~ DIAG-DISEASE-001")
    card = parse_markdown_file(kb / "diag/diseases/diag_disease_ihd.md")
    assert card.metadata["presentation"][0]["weight"] == 3
    assert card.metadata["sources"] == ["A", "B", "C"]
    assert card.metadata["version"] == "2.1"
    assert apply_patch.apply(patch, kb, "2026-09-16", dry_run=False) == []  # повторно — без изменений


def test_apply_patch_creates_card_and_dry_run_writes_nothing(kb):
    patch = {"_anchor": {"x": 1}, "DIAG-EXAM-001": {"create": {"file": "diag_exam_ecg.md"},
             "set": {**COMMON, "title": "ЭКГ", "domain": "diag", "category": "exam", "relations": []}, "body": "# ЭКГ\n"}}
    assert apply_patch.apply(patch, kb, "2026-09-16", dry_run=True)
    assert not (kb / "diag/exams/diag_exam_ecg.md").exists()
    apply_patch.apply(patch, kb, "2026-09-16", dry_run=False)
    assert parse_markdown_file(kb / "diag/exams/diag_exam_ecg.md").id == "DIAG-EXAM-001"


# --------------------------------------------------- слой и граф связей
def test_machine_refs_and_sync_relations(kb, monkeypatch):
    apply_patch.apply({"DIAG-DISEASE-001": {"set": {"presentation": [
        {"symptom": "DIAG-SYMPTOM-001", "weight": 2, "frequency": "common"}]}}}, kb, "2026-09-16", dry_run=False)
    card = parse_markdown_file(kb / "diag/diseases/diag_disease_ihd.md")
    refs = list(iter_machine_refs(card.metadata, schema, "disease"))
    assert [(r.target, r.implies) for r in refs] == [("DIAG-SYMPTOM-001", "has_symptom")]
    assert "MACHINE_REF_NO_RELATION" in codes(validate(kb), "WARNING")
    sync_relations.main(["--kb", str(kb)])
    card = parse_markdown_file(kb / "diag/diseases/diag_disease_ihd.md")
    assert {"target": "DIAG-SYMPTOM-001", "type": "has_symptom"}.items() <= card.relations[0].items()
    assert "MACHINE_REF_NO_RELATION" not in codes(validate(kb))


def test_unknown_top_level_field_is_warned(kb):
    apply_patch.apply({"DIAG-DISEASE-001": {"set": {"add_sources": ["ошибочно вложенный ключ патча"]}}}, kb, "2026-09-16", dry_run=False)
    assert "UNKNOWN_FIELD" in codes(validate(kb), "WARNING")


# ------------------------------------------------------------------ шкалы
def scale(kb: Path, interpretation, parameters=None, policy="skip"):
    params = parameters or [
        {"code": "a", "label": "A", "options": [{"when": {"fact": "smoker"}, "points": 1}, {"when": {"not": {"fact": "smoker"}}, "points": 0}]},
        {"code": "b", "label": "B", "options": [{"when": {"param": "age", "op": ">=", "value": 65}, "points": 2}, {"when": {"param": "age", "op": "<", "value": 65}, "points": 0}]},
    ]
    put(kb, "prot/scales/prot_scale_test.md", {**COMMON, "id": "PROT-SCALE-001", "title": "Шкала", "domain": "prot",
        "category": "scale", "relations": [], "parameters": params, "interpretation": interpretation, "missing_policy": policy})


def test_scale_full_coverage_passes(kb):
    scale(kb, [{"min": 0, "max": 1, "category": "low", "label": "низкий"}, {"min": 2, "max": None, "category": "high", "label": "высокий"}])
    assert not codes(validate(kb)) & {"SCALE_GAP", "SCALE_OVERLAP", "SCALE_COVERAGE"}


@pytest.mark.parametrize("interp, code", [
    ([{"min": 0, "max": 1, "category": "a", "label": "a"}, {"min": 3, "max": 3, "category": "b", "label": "b"}], "SCALE_GAP"),
    ([{"min": 0, "max": 2, "category": "a", "label": "a"}, {"min": 2, "max": 3, "category": "b", "label": "b"}], "SCALE_OVERLAP"),
    ([{"min": 0, "max": 1, "category": "a", "label": "a"}, {"min": 2, "max": 2, "category": "b", "label": "b"}], "SCALE_COVERAGE"),
    ([{"min": 1, "max": None, "category": "a", "label": "a"}], "SCALE_COVERAGE"),
])
def test_scale_coverage_errors(kb, interp, code):
    scale(kb, interp)
    assert code in codes(validate(kb), "ERROR")


def test_scale_points_from_parameter_range(kb):
    params = [{"code": f"q{i}", "label": f"q{i}", "points_from": f"act_q{i}"} for i in range(1, 6)]
    scale(kb, [{"min": 5, "max": 15, "category": "a", "label": "a"}, {"min": 16, "max": 25, "category": "b", "label": "b"}], params, policy="fail")
    assert not codes(validate(kb)) & {"SCALE_GAP", "SCALE_OVERLAP", "SCALE_COVERAGE", "SCALE_PARAM_SOURCE"}


# ----------------------------------------------------------- метаатом known
def test_known_atom_is_never_unknown():
    facts = PatientFacts(params={"sbp": 150}, facts={"smoker": False})
    assert evaluate({"known": "sbp"}, facts, schema).is_true()
    assert evaluate({"known": "smoker"}, facts, schema).is_true()
    assert evaluate({"known": "hr"}, facts, schema).is_false()
    assert evaluate({"not": {"known": "hr"}}, facts, schema).is_true()


# ---------------------------------------------------- реальная база знаний
@pytest.fixture(scope="module")
def real_report():
    repo = KnowledgeRepository(ROOT / "kb").load()
    return repo, KnowledgeBaseValidator(repo).validate()


def test_real_kb_is_clean(real_report):
    repo, report = real_report
    assert report.errors == [], [i.message for i in report.errors][:5]
    assert [i for i in report.issues if i.severity == "WARNING"] == []
    assert report.stats["заглушек"] == 0
    assert report.stats["сирот (без входящих связей)"] == 0


def test_real_kb_machine_layer_complete(real_report):
    repo, _ = real_report
    from src.card_writer import machine_layer_missing
    missing = {c.id: machine_layer_missing(c.metadata, schema, c.category) for c in repo.cards}
    assert {k: v for k, v in missing.items() if v} == {}


def test_real_rules_count_and_coverage(real_report):
    _, report = real_report
    assert report.total_rules >= 40
    rules = [r for f in sorted((ROOT / "kb" / "rules").glob("*.yaml")) for r in yaml.safe_load(f.read_text(encoding="utf-8"))]
    domains = {r["domain"] for r in rules}
    assert domains == {"diag", "prot", "pharm", "glb"}


@pytest.mark.parametrize("facts, expected", [
    (PatientFacts(symptoms={"DIAG-SYMPTOM-002"}, features={"chest_pain.pressing", "chest_pain.at_rest"},
                  params={"age": 62, "symptom_duration_min": 30}), {"RULE-DIAG-002", "RULE-DIAG-023"}),
    (PatientFacts(params={"age": 7}, profiles={"GLB-PROFILE-004"}), {"RULE-GLB-001"}),
    (PatientFacts(symptoms={"DIAG-SYMPTOM-010"}, features={"focal_deficit.face_droop"}), {"RULE-DIAG-015", "RULE-DIAG-032"}),
])
def test_rules_fire_on_reference_patients(facts, expected):
    rules = [r for f in sorted((ROOT / "kb" / "rules").glob("*.yaml")) for r in yaml.safe_load(f.read_text(encoding="utf-8"))]
    fired = {r["id"] for r in rules if evaluate(r["if"], facts, schema).is_true()}
    assert expected <= fired


def test_redflag_and_emergency_on_reference_patient():
    repo = KnowledgeRepository(ROOT / "kb").load()
    facts = PatientFacts(symptoms={"DIAG-SYMPTOM-002"}, features={"chest_pain.pressing", "chest_pain.at_rest"},
                         params={"symptom_duration_min": 30})
    assert evaluate(repo.get_by_id("DIAG-REDFLAG-005").metadata["triggers"], facts, schema).is_true()
    facts.red_flags.add("DIAG-REDFLAG-005")
    assert evaluate(repo.get_by_id("DIAG-EMERGENCY-001").metadata["criteria"], facts, schema).is_true()

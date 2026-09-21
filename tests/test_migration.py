"""Тесты мигратора v1 -> v2 на синтетической базе."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import migrate_v1_to_v2 as mig  # noqa: E402
from src.markdown_parser import parse_markdown_file  # noqa: E402
from src.repository import KnowledgeRepository  # noqa: E402
from src.schema import load_schema  # noqa: E402
from src.validator import KnowledgeBaseValidator  # noqa: E402

schema = load_schema()

V1 = {
    "body_system": ["cardiovascular"], "tags": ["t"], "urgency": "routine", "access_level": "professional",
    "target_specialist": ["therapist"], "age_group": ["adult"], "sources": ["A", "B"],
    "clinical_guidelines": ["КР"], "last_medical_review": "2026-04-09", "medical_reviewer": "—",
    "author": "Инженер знаний №1", "version": "1.0", "date_created": "2026-04-09", "date_updated": "2026-04-09",
    "status": "approved", "disclaimer": True,
}
BODY = "\n# Заголовок\n\n" + "Содержательный текст карточки. " * 40 + "\n"


def put(kb: Path, rel: str, meta: dict) -> None:
    p = kb / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n" + BODY, encoding="utf-8")


def build_v1(kb: Path) -> None:
    (kb / "_schema").mkdir(parents=True)
    shutil.copy(ROOT / "kb" / "_schema" / "schema.yaml", kb / "_schema" / "schema.yaml")
    put(kb, "diagnostics/symptoms/diag_symptom_chest_pain.md", {
        **V1, "id": "DIAG-SYMPTOM-001", "title": "Боль", "domain": "diag", "category": "symptom",
        "related": ["DIAG-DISEASE-001", "DIAG-EXAM-001"],
        "relations": [{"target": "DIAG-DISEASE-001", "type": "associated_with", "description": "встречается"}]})
    put(kb, "diagnostics/diseases/diag_disease_ihd.md", {
        **V1, "id": "DIAG-DISEASE-001", "title": "ИБС", "domain": "diag", "category": "disease",
        "related": ["DIAG-SYMPTOM-001"], "relations": [{"target": "DIAG-SYMPTOM-001", "type": "has_symptom"}]})
    put(kb, "diagnostics/exams/diag_exam_ecg.md", {
        **V1, "id": "DIAG-EXAM-001", "title": "ЭКГ", "domain": "diag", "category": "exam", "evidence_level": "I",
        "related": ["DIAG-DISEASE-001"], "relations": [{"target": "DIAG-DISEASE-001", "type": "diagnosed_by"}]})
    put(kb, "protocols/emergency/prot_emergency_crisis.md", {
        **V1, "id": "PROT-EMERGENCY_P-001", "title": "Криз", "domain": "protocols", "category": "emergency_p",
        "urgency": "emergency", "related": ["DIAG-DISEASE-001"],
        "relations": [{"target": "DIAG-DISEASE-001", "type": "emergency_protocol_for"}]})


def test_migration_end_to_end(tmp_path):
    kb = tmp_path / "kb"
    build_v1(kb)
    log = mig.migrate(kb, schema, dry_run=False)

    assert log.migrated == 4
    assert not (kb / "diagnostics").exists() and not (kb / "protocols").exists()
    assert (kb / "prot" / "emergency" / "prot_emergency_p_crisis.md").exists()

    sym = parse_markdown_file(kb / "diag" / "symptoms" / "diag_symptom_chest_pain.md")
    assert sym.schema_version == 2 and "related" not in sym.metadata
    types = {(r["target"], r["type"]) for r in sym.relations}
    assert ("DIAG-DISEASE-001", "symptom_of") in types         # associated_with -> по паре категорий
    assert ("DIAG-EXAM-001", "diagnosed_by") in types          # перенесено из related
    assert sym.metadata["medical_reviewer"] == schema.model_review_marker
    assert sym.metadata["status"] == "medical_review"          # approved без машиночитаемого слоя
    assert sym.metadata["version"] == "2.0"

    exam = parse_markdown_file(kb / "diag" / "exams" / "diag_exam_ecg.md")
    assert exam.relations[0]["type"] == "diagnoses"            # обращение направления
    assert "evidence_level" not in exam.metadata and exam.metadata["recommendation_class"] == "I"

    ep = parse_markdown_file(kb / "prot" / "emergency" / "prot_emergency_p_crisis.md")
    assert ep.domain == "prot"

    report = KnowledgeBaseValidator(KnowledgeRepository(kb).load(), rules_root=kb / "rules").validate()
    assert report.is_valid, [i.message for i in report.errors]


def test_migration_is_idempotent(tmp_path):
    kb = tmp_path / "kb"
    build_v1(kb)
    mig.migrate(kb, schema, dry_run=False)
    snapshot = {p: p.read_text(encoding="utf-8") for p in kb.rglob("*.md")}
    log = mig.migrate(kb, schema, dry_run=False)
    assert log.migrated == 0 and log.skipped_v2 == 4
    assert {p: p.read_text(encoding="utf-8") for p in kb.rglob("*.md")} == snapshot


def test_dry_run_changes_nothing(tmp_path):
    kb = tmp_path / "kb"
    build_v1(kb)
    before = {p: p.read_text(encoding="utf-8") for p in kb.rglob("*.md")}
    log = mig.migrate(kb, schema, dry_run=True)
    assert log.migrated == 4 and log.folder_moves
    assert {p: p.read_text(encoding="utf-8") for p in kb.rglob("*.md")} == before


def test_resolver_prefers_pair_default():
    assert mig.resolve_relation(schema, "influences_routing", "routing", "scale")[0] == "assessed_by"
    assert mig.resolve_relation(schema, "diagnosed_by", "exam", "disease")[0] == "diagnoses"
    assert mig.resolve_relation(schema, "related_to", "screening", "protocol")[0] == "screening_for"
    assert mig.resolve_relation(schema, "associated_with", "checklist", "symptom")[0] == "associated_with"

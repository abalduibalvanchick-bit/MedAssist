"""Тесты валидатора для карточек схемы v2 и правил kb/rules."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.repository import KnowledgeRepository
from src.validator import KnowledgeBaseValidator

COMMON = {
    "schema_version": 2,
    "body_system": ["cardiovascular"],
    "tags": ["test"],
    "urgency": "routine",
    "access_level": "professional",
    "target_specialist": ["therapist"],
    "age_group": ["adult"],
    "sources": ["Источник 1", "Источник 2"],
    "clinical_guidelines": ["КР, 2024"],
    "last_medical_review": "2026-09-01",
    "medical_reviewer": "модельная верификация (учебный проект)",
    "author": "Инженер знаний №1",
    "version": "2.0",
    "date_created": "2026-09-01",
    "date_updated": "2026-09-01",
    "status": "medical_review",
    "disclaimer": True,
}


def write_card(kb: Path, domain_folder: str, cat_folder: str, filename: str, meta: dict, body: str = "# Заголовок\n\n" + "Текст. " * 120) -> Path:
    path = kb / domain_folder / cat_folder / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n\n" + body, encoding="utf-8")
    return path


def symptom(kb: Path, **extra) -> None:
    meta = {**COMMON, "id": "DIAG-SYMPTOM-001", "title": "Боль в груди", "domain": "diag", "category": "symptom",
            "relations": [{"target": "DIAG-DISEASE-001", "type": "symptom_of", "description": "встречается при"}],
            "synonyms": ["загрудинная боль"],
            "features": [{"code": "chest_pain.pressing", "label": "давящая"}], **extra}
    write_card(kb, "diag", "symptoms", "diag_symptom_chest_pain.md", meta)


def disease(kb: Path, **extra) -> None:
    meta = {**COMMON, "id": "DIAG-DISEASE-001", "title": "ИБС", "domain": "diag", "category": "disease",
            "relations": [{"target": "DIAG-SYMPTOM-001", "type": "has_symptom", "description": "проявляется"}],
            "presentation": [{"symptom": "DIAG-SYMPTOM-001", "weight": 3, "frequency": "very_common", "features": ["chest_pain.pressing"]}],
            "exams": [{"exam": "DIAG-EXAM-001", "role": "confirms"}], **extra}
    write_card(kb, "diag", "diseases", "diag_disease_ihd.md", meta)


def exam(kb: Path, **extra) -> None:
    meta = {**COMMON, "id": "DIAG-EXAM-001", "title": "ЭКГ", "domain": "diag", "category": "exam",
            "relations": [{"target": "DIAG-DISEASE-001", "type": "diagnoses", "description": "подтверждает"}],
            "results": [{"value": "st_elevation", "label": "подъём ST", "indicates": ["DIAG-DISEASE-001"]}], **extra}
    write_card(kb, "diag", "exams", "diag_exam_ecg.md", meta)


def redflag(kb: Path, **extra) -> None:
    meta = {**COMMON, "id": "DIAG-REDFLAG-001", "title": "Затяжная боль", "domain": "diag", "category": "redflag",
            "urgency": "emergency",
            "relations": [{"target": "DIAG-DISEASE-001", "type": "red_flag_for", "description": "опасный признак"}],
            "triggers": {"all": [{"symptom": "DIAG-SYMPTOM-001"}, {"param": "symptom_duration_min", "op": ">", "value": 20}]},
            "indicates": ["DIAG-DISEASE-001"], **extra}
    write_card(kb, "diag", "red_flags", "diag_redflag_prolonged_pain.md", meta)


@pytest.fixture
def kb(tmp_path: Path) -> Path:
    kb = tmp_path / "kb"
    symptom(kb)
    disease(kb)
    exam(kb)
    redflag(kb)
    return kb


def run(kb: Path, rules_root: Path | None = None):
    repo = KnowledgeRepository(kb).load()
    return KnowledgeBaseValidator(repo, rules_root=rules_root or (kb / "rules")).validate()


def codes(report, severity="ERROR") -> set[str]:
    return {i.code for i in report.issues if i.severity == severity}


# --------------------------------------------------------------- базовый
def test_valid_v2_base_passes(kb):
    report = run(kb)
    assert report.errors == [], [i.message for i in report.errors]
    assert report.is_valid
    assert report.stats["карточек схемы v2"] == "4 из 4"
    assert report.stats["с заполненным машиночитаемым слоем"] == "4 из 4"


# ----------------------------------------------------------- инварианты
def test_domain_id_mismatch(kb):
    symptom(kb, domain="prot")
    assert "DOMAIN_ID_MISMATCH" in codes(run(kb))


def test_wrong_folder_is_reported(kb):
    (kb / "diag" / "symptoms" / "diag_symptom_chest_pain.md").rename(kb / "diag" / "diseases" / "diag_symptom_chest_pain.md")
    report = run(kb)
    assert "BAD_LOCATION" in codes(report) or "FOLDER_CATEGORY_MISMATCH" in codes(report)


def test_bad_file_name(kb):
    (kb / "diag" / "symptoms" / "diag_symptom_chest_pain.md").rename(kb / "diag" / "symptoms" / "chest_pain.md")
    assert "BAD_FILE_NAME" in codes(run(kb))


def test_removed_field_related_is_error(kb):
    symptom(kb, related=["DIAG-DISEASE-001"])
    assert "REMOVED_FIELD" in codes(run(kb))


def test_legacy_domain_alias_not_allowed_in_v2(kb):
    disease(kb, domain="diagnostics")
    assert "DOMAIN_ID_MISMATCH" in codes(run(kb))


# --------------------------------------------------------- перечисления
def test_enum_violations(kb):
    symptom(kb, urgency="routine | urgent", body_system=["cardiovascular | respiratory"], target_specialist=["therapist", "shaman"])
    c = codes(run(kb))
    assert {"BAD_ENUM_URGENCY", "BAD_ENUM_BODY_SYSTEM", "BAD_ENUM_TARGET_SPECIALIST"} <= c


def test_empty_reviewer_is_error(kb):
    symptom(kb, medical_reviewer="—")
    assert "EMPTY_REVIEWER" in codes(run(kb))


def test_single_source_is_warning(kb):
    symptom(kb, sources=["Только один"])
    report = run(kb)
    assert "FEW_SOURCES" in codes(report, "WARNING")
    assert report.is_valid


def test_emergency_requires_emergency_urgency(kb):
    redflag(kb)  # redflag не обязан быть emergency, проверяем категорию emergency
    meta = {**COMMON, "id": "DIAG-EMERGENCY-001", "title": "ОКС", "domain": "diag", "category": "emergency",
            "relations": [{"target": "DIAG-SYMPTOM-001", "type": "has_symptom"}], "criteria": {"symptom": "DIAG-SYMPTOM-001"}}
    write_card(kb, "diag", "emergencies", "diag_emergency_acs.md", meta)
    assert "EMERGENCY_URGENCY" in codes(run(kb))


# ---------------------------------------------------------------- связи
def test_unknown_relation_type_is_error_with_hint(kb):
    symptom(kb, relations=[{"target": "DIAG-DISEASE-001", "type": "may_indicate"}])
    report = run(kb)
    assert "UNKNOWN_RELATION_TYPE" in codes(report)
    assert any("symptom_of" in i.message for i in report.errors)


def test_relation_category_constraints(kb):
    # has_symptom допустима только от disease/emergency к symptom
    symptom(kb, relations=[{"target": "DIAG-DISEASE-001", "type": "has_symptom"}])
    assert "RELATION_SOURCE_CATEGORY" in codes(run(kb))


def test_contradictory_explicit_relations_error(kb):
    # Два маршрута объявляют друг друга следующим шагом — противоречие направления.
    base = {**COMMON, "domain": "prot", "category": "routing"}
    write_card(kb, "prot", "routing", "prot_routing_a.md",
               {**base, "id": "PROT-ROUTING-001", "title": "A", "relations": [{"target": "PROT-ROUTING-002", "type": "next_step"}]})
    write_card(kb, "prot", "routing", "prot_routing_b.md",
               {**base, "id": "PROT-ROUTING-002", "title": "B", "relations": [{"target": "PROT-ROUTING-001", "type": "next_step"}]})
    assert "CONTRADICTORY_RELATION" in codes(run(kb))


def test_different_types_between_same_pair_are_allowed(kb):
    symptom(kb, relations=[{"target": "DIAG-DISEASE-001", "type": "symptom_of"},
                           {"target": "DIAG-DISEASE-001", "type": "associated_with"}])
    assert "CONTRADICTORY_RELATION" not in codes(run(kb))


def test_broken_relation(kb):
    symptom(kb, relations=[{"target": "DIAG-DISEASE-999", "type": "symptom_of"}])
    assert "BROKEN_RELATION" in codes(run(kb))


# --------------------------------------------------- машиночитаемый слой
def test_bad_condition_in_machine_layer(kb):
    redflag(kb, triggers={"all": [{"symptom": "DIAG-SYMPTOM-001"}, {"param": "nonexistent", "op": ">", "value": 1}]})
    report = run(kb)
    assert "BAD_CONDITION" in codes(report)
    assert any("Неизвестный параметр" in i.message for i in report.errors)


def test_unknown_feature_reference(kb):
    disease(kb, presentation=[{"symptom": "DIAG-SYMPTOM-001", "weight": 3, "frequency": "common", "features": ["chest_pain.nonexistent"]}])
    assert "UNKNOWN_FEATURE" in codes(run(kb))


def test_machine_id_category_check(kb):
    disease(kb, exams=[{"exam": "DIAG-SYMPTOM-001", "role": "confirms"}])
    assert "MACHINE_ID_CATEGORY" in codes(run(kb))


def test_machine_enum_check(kb):
    disease(kb, presentation=[{"symptom": "DIAG-SYMPTOM-001", "weight": 7, "frequency": "common"}])
    assert "MACHINE_ENUM" in codes(run(kb))


def test_approved_requires_machine_layer(kb):
    disease(kb, status="approved", presentation=[], exams=[])
    assert "APPROVED_WITHOUT_MACHINE_LAYER" in codes(run(kb))


def test_approved_with_machine_layer_passes(kb):
    disease(kb, status="approved")
    assert "APPROVED_WITHOUT_MACHINE_LAYER" not in codes(run(kb))


def test_exam_result_value_checked_against_exam_card(kb):
    redflag(kb, triggers={"exam_result": "DIAG-EXAM-001", "value": "no_such_value"})
    report = run(kb)
    assert any("не объявлено в results" in i.message for i in report.errors)


# --------------------------------------------------------------- правила
def write_rule(kb: Path, rule: dict, name: str = "diag_rules.yaml") -> Path:
    path = kb / "rules" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump([rule], allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


GOOD_RULE = {
    "id": "RULE-DIAG-001",
    "domain": "diag",
    "title": "Затяжная загрудинная боль",
    "if": {"all": [{"symptom": "DIAG-SYMPTOM-001"}, {"param": "symptom_duration_min", "op": ">", "value": 20}]},
    "then": [{"trigger_red_flag": "DIAG-REDFLAG-001"}, {"assert_hypothesis": {"target": "DIAG-DISEASE-001", "weight": 3}}, {"set_urgency": "emergency"}],
    "source_cards": ["DIAG-REDFLAG-001", "DIAG-DISEASE-001"],
    "explanation": "Боль в груди дольше 20 минут — критерий красного флага.",
}


def test_good_rule_passes(kb):
    write_rule(kb, GOOD_RULE)
    report = run(kb)
    assert report.total_rules == 1
    assert report.errors == [], [i.message for i in report.errors]


def test_rule_missing_fields_and_bad_id(kb):
    write_rule(kb, {"id": "R1", "domain": "diag", "if": {"fact": "smoker"}, "then": [{"set_urgency": "urgent"}]})
    c = codes(run(kb))
    assert {"RULE_MISSING_FIELD", "RULE_BAD_ID", "RULE_NO_SOURCES"} <= c


def test_rule_bad_action_and_value(kb):
    rule = {**GOOD_RULE, "then": [{"explode": "x"}, {"set_urgency": "asap"}, {"assert_hypothesis": {"target": "DIAG-EXAM-001"}}]}
    write_rule(kb, rule)
    c = codes(run(kb))
    assert {"RULE_UNKNOWN_ACTION", "RULE_BAD_VALUE", "RULE_TARGET_CATEGORY"} <= c


def test_rule_bad_condition_and_broken_source(kb):
    rule = {**GOOD_RULE, "if": {"symptom": "DIAG-SYMPTOM-404"}, "source_cards": ["DIAG-SYMPTOM-404"]}
    write_rule(kb, rule)
    c = codes(run(kb))
    assert {"RULE_BAD_CONDITION", "RULE_BROKEN_SOURCE"} <= c


def test_duplicate_rule_ids(kb):
    write_rule(kb, GOOD_RULE, "a.yaml")
    write_rule(kb, GOOD_RULE, "b.yaml")
    assert "RULE_DUPLICATE_ID" in codes(run(kb))


# ----------------------------------------------------------- качество
def test_stub_detection(kb):
    symptom(kb)
    path = kb / "diag" / "symptoms" / "diag_symptom_chest_pain.md"
    text = path.read_text(encoding="utf-8")
    head, _, _ = text.partition("---\n\n")
    path.write_text(head + "---\n\n# Боль\n\n> Служебная интеграционная карточка.\n", encoding="utf-8")
    report = run(kb)
    assert "STUB_CARD" in codes(report, "WARNING")
    assert report.stats["заглушек"] == 1


def test_v1_card_still_validates_in_compat_mode(kb):
    meta = {k: v for k, v in COMMON.items() if k != "schema_version"}
    meta.update({"id": "PROT-SCALE-001", "title": "Шкала", "domain": "protocols", "category": "scale",
                 "related": ["DIAG-DISEASE-001"], "relations": [{"target": "DIAG-DISEASE-001", "type": "uses_protocol"}]})
    write_card(kb, "protocols", "scales", "prot_scale_test.md", meta)
    report = run(kb)
    assert report.is_valid, [i.message for i in report.errors]
    assert "SCHEMA_V1" in codes(report, "INFO")

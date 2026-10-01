"""Наследование противопоказаний препаратом от фармакологической группы."""

from __future__ import annotations

from pathlib import Path

from src.models import KnowledgeCard
from src.pharmacology import duplicated_class_contraindications, effective_contraindications
from src.repository import KnowledgeRepository

ROOT = Path(__file__).resolve().parents[1]


def card(cid, category, meta=None, relations=None):
    return KnowledgeCard(metadata={"id": cid, "title": cid, "domain": "pharm", "category": category,
                                   **(meta or {}), "relations": relations or []}, content="", file_path=Path(cid))


HF = {"fact": "heart_failure"}
LIVER = {"fact": "hepatic_failure"}
ASTHMA_A = {"any": [{"fact": "known_asthma"}, {"disease": "DIAG-DISEASE-004"}]}
ASTHMA_B = {"any": [{"disease": "DIAG-DISEASE-004"}, {"fact": "known_asthma"}]}


def base():
    cls = card("C", "drugclass", {"contraindications": [
        {"when": HF, "absolute": False, "explanation": "ХСН", "not_for": ["D2"]},
        {"when": LIVER, "absolute": False, "explanation": "печень"},
        {"when": ASTHMA_A, "absolute": False, "explanation": "астма"}]})
    d1 = card("D1", "drug", {"contraindications": [{"when": LIVER, "absolute": True, "explanation": "тяжёлая печёночная"}]},
              [{"target": "C", "type": "included_in"}])
    d2 = card("D2", "drug", {}, [{"target": "C", "type": "included_in"}])
    return {"C": cls, "D1": d1, "D2": d2}


def test_inheritance_and_own_override():
    cards = base()
    eff = {e["explanation"]: e for e in effective_contraindications(cards["D1"], cards)}
    assert set(eff) == {"тяжёлая печёночная", "ХСН", "астма"}       # групповое «печень» перекрыто собственным
    assert eff["тяжёлая печёночная"]["absolute"] is True and eff["тяжёлая печёночная"]["source"] == "D1"
    assert eff["ХСН"]["source"] == "C"


def test_not_for_excludes_member():
    cards = base()
    assert "ХСН" not in {e["explanation"] for e in effective_contraindications(cards["D2"], cards)}


def test_duplicate_detection_ignores_branch_order_but_not_absoluteness():
    cards = base()
    cards["D2"].metadata["contraindications"] = [{"when": ASTHMA_B, "absolute": False, "explanation": "астма"}]
    assert duplicated_class_contraindications(cards["D2"], cards) == [("астма", "C")]
    assert duplicated_class_contraindications(cards["D1"], cards) == []   # строже группового — уточнение


def test_real_kb_drugs_have_no_duplicates_and_inherit():
    repo = KnowledgeRepository(ROOT / "kb").load()
    cards = {c.id: c for c in repo.cards}
    for drug in (c for c in repo.cards if c.category == "drug"):
        assert duplicated_class_contraindications(drug, cards) == [], drug.id
    enalapril = {e["explanation"] for e in effective_contraindications(cards["PHARM-DRUG-001"], cards)}
    assert "ангионевротический отёк в анамнезе" in enalapril               # унаследовано от иАПФ
    amlodipine = {e["source"] + ":" + e["explanation"][:10] for e in effective_contraindications(cards["PHARM-DRUG-002"], cards)}
    assert not any("недигидроп" in x for x in amlodipine)                   # исключение not_for

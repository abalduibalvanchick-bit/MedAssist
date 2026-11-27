"""Приёмочные проверки новых контуров решателя."""

import json
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from src.reference import answer_reference, search_reference
from src.solver import load_default_kb, solve
from src.web.__main__ import Handler
from src.web.scenarios import ROOT
from tests.solver_cases import check_case, load_cases


@pytest.mark.parametrize("table", load_default_kb().category("difdiag"), ids=lambda card: card.id)
def test_every_differential_card_is_executed(table):
    result = solve({"patient": {"age": 40, "symptoms": [table.metadata["leading_symptom"]]}})
    evaluated = next(t for t in result["differential"] if t["id"] == table.id)
    assert {b["id"] for b in evaluated["branches"]} == {b["target"] for b in table.metadata["branches"]}
    assert all(b["status"] in {"supported", "unresolved", "unlikely"} for b in evaluated["branches"])
    assert all(b["key_exam"] is None or "recommended" in b["key_exam"] for b in evaluated["branches"])


def test_differential_explains_explicit_negative_and_keeps_unknowns():
    first = solve({"patient": {"age": 45, "features": ["cough.productive"], "denied_symptoms": ["DIAG-SYMPTOM-004"]}})
    branches = first["differential"][0]["branches"]
    pneumonia = next(b for b in branches if b["id"] == "DIAG-DISEASE-003")
    assert pneumonia["status"] == "unlikely" and pneumonia["against"]
    assert any(b["status"] == "unresolved" for b in branches)
    assert [q["priority"] for q in first["questions"]] == sorted(
        (q["priority"] for q in first["questions"]), reverse=True)


def test_therapy_excludes_known_and_checks_unknown_contraindications():
    patient = {"age": 31, "diseases": ["DIAG-DISEASE-001"]}
    unknown = solve({"patient": patient})
    known = solve({"patient": {**patient, "facts": {"pregnant": True}}})
    def agent(solution):
        return next(o for o in solution["therapy"]["regimens"][0]["lines"][0]["options"]
                    if o["id"] == "PHARM-DRUGCLASS-001")
    assert agent(unknown)["status"] == "verify"
    assert agent(known)["status"] == "excluded"
    assert agent(known)["reasons"]
    assert "therapy" not in solve({"patient": patient}, role="patient")


def test_interaction_reads_reported_medications_and_trigger():
    data = {"params": {"egfr": 50}, "facts": {"contrast_study_planned": True}}
    assert not solve({"patient": data})["therapy"]["interactions"]
    result = solve({"patient": {**data, "medications": ["PHARM-DRUG-020"]}})
    assert result["status"] == "ok"
    interaction = result["therapy"]["interactions"][0]
    assert interaction["source"] == "PHARM-INTERACTION-001"
    assert any(t["source"] == interaction["source"] for t in result["trace"])


def test_reference_finds_expected_card_and_declines_unrelated_query():
    result = answer_reference("Из чего состоит шкала CURB-65?")
    assert result["status"] == "ok" and result["mode"] == "extracts"
    assert result["sources"][0]["id"] == "PROT-SCALE-004"
    assert all(word in result["answer"][0]["text"].lower() for word in ("спутанность", "мочевина", "частота дыхания", "сад", "возраст"))
    routing = search_reference("Как направить пациента с бронхиальной астмой?")
    assert routing[0]["id"] == "PROT-ROUTING-005"
    for question, card in (
        ("Куда обращаться при астме?", "PROT-ROUTING-005"),
        ("Что измеряет пульсоксиметр?", "DIAG-EXAM-010"),
        ("Для чего нужна спирометрия при астме?", "DIAG-EXAM-008"),
    ):
        assert search_reference(question)[0]["id"] == card
    assert result["answer"][0]["source"] == 1
    assert answer_reference("Рецепт карамельного торта")["status"] == "not_found"
    patient_result = search_reference("Противопоказания эналаприла", "patient")
    assert all(load_default_kb().get(item["id"]).metadata["access_level"] == "patient" for item in patient_result)


def test_reference_verifies_generated_evidence_and_falls_back():
    question = "Что означает пульсоксиметрия?"
    def generator(_, sources):
        return [{"source": 1, "text": "Ответ по карточке", "evidence": sources[0]["excerpt"]}]
    result = answer_reference(question, generator=generator)
    assert result["mode"] == "generated"
    assert result["answer"][0]["source"] == 1
    assert result["answer"][0]["text"] == result["answer"][0]["evidence"]
    assert result["answer"][0]["text"] != "Ответ по карточке"
    fallback = answer_reference(question, generator=lambda *_: [{"source": 22, "text": "Ответ", "evidence": "Посторонняя цитата"}])
    assert fallback["mode"] == "extracts"


def test_web_runs_example_and_reference_on_same_server():
    handler = partial(Handler, generator=None)
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        root = f"http://127.0.0.1:{server.server_port}"

        def fetch(path, data=None):
            headers = {"Content-Type": "application/json"}
            body = json.dumps(data).encode() if data is not None else None
            with urlopen(Request(root + path, data=body, headers=headers), timeout=5) as response:
                return json.load(response)

        try:
            kb = load_default_kb()
            overview = fetch("/api/catalog")
            assert overview["counts"] == {"cards": len(kb.cards), "rules": len(kb.rules)}
            expected_fields = {
                "param": set(kb.schema.parameters), "fact": set(kb.schema.facts),
                "feature": set(kb.feature_owner), "symptom": {card.id for card in kb.category("symptom")},
                "exam_result": {card.id for card in kb.category("exam") if card.metadata.get("results")},
            }
            assert {kind: {item["code"] for item in rows} for kind, rows in overview["fields"].items()} == expected_fields
            assert {item["id"] for item in overview["diseases"]} == {
                card.id for kind in ("disease", "emergency") for card in kb.category(kind)
            }
            assert {item["id"] for item in overview["medications"]} == {
                card.id for kind in ("drug", "drugclass") for card in kb.category(kind)
            }
            demo = fetch("/api/examples/pneumonia_no_urea")["request"]["patient"]
            result = fetch("/api/solve", {"patient": demo, "answers": {"urea": "8"}})
            assert result["patient"]["params"]["urea"] == 8
            assert result["solution"]["explanation"]
            assert fetch("/api/reference", {"question": "Из чего состоит шкала CURB-65?"})["sources"]
            regression = {case["id"]: case for case in load_cases()}
            assert {example["code"] for example in overview["examples"] if "code" in example} == regression.keys()
            assert {example["id"] for example in overview["examples"] if "code" not in example} == {
                file.stem for file in (ROOT / "examples").glob("*.yaml")
            }
            for example in overview["examples"]:
                case = fetch("/api/examples/" + example["id"])
                assert "expect" not in case
                if "code" in case:
                    spec = regression[case["code"]]
                    assert case["request"]["patient"] == spec["patient"]
                    solution = fetch("/api/solve", {**case["request"], "role": case["role"]})["solution"]
                    assert check_case(spec, solution) == [], spec["id"]
                else:
                    assert fetch("/api/solve", case["request"])["solution"]["status"] != "invalid"
                    if case["group"] == "published":
                        assert case["source"].startswith("https://pmc.ncbi.nlm.nih.gov/")

            library = fetch("/api/knowledge")
            assert {card["id"] for card in library["cards"]} == kb.cards.keys()
            assert {rule["id"] for rule in library["rules"]} == {rule.id for rule in kb.rules}
            for record in library["cards"]:
                full = fetch("/api/knowledge/" + record["id"])
                assert full["metadata"]["id"] == record["id"]
                assert full["content"] == kb.get(record["id"]).content
            for record in library["rules"]:
                assert fetch("/api/knowledge-rules/" + record["id"])["metadata"]["then"]
            for ident in library["demos"]:
                assert fetch("/api/knowledge-demos/" + ident)["content"]
            assert fetch("/api/knowledge?role=patient")["rules"] == []
            with pytest.raises(HTTPError) as exc:
                fetch("/api/knowledge/PHARM-DRUG-001?role=patient")
            assert exc.value.code == 404
        finally:
            server.shutdown()
            thread.join()

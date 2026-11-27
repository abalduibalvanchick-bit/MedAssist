import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
import yaml

from src.reference import answer_reference, ollama_generator, route_source, search_reference
from src.solver import load_default_kb

CASES = yaml.safe_load(Path(__file__).with_name("reference_cases.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name,role,query,target", CASES, ids=[c[0] for c in CASES])
def test_retrieval(name, role, query, target):
    results = search_reference(query, role)
    if target is None:
        assert results == []
    else:
        assert target in [row["id"] for row in results]
        for row in results:
            assert row["excerpt"] in row["context"]
            assert role == "professional" or load_default_kb().get(row["id"]).metadata["access_level"] in (role, "patient")


@pytest.mark.parametrize("card", load_default_kb().category("routing"), ids=lambda card: card.id)
def test_route_grounding(card):
    for row, decision in [(None, card.metadata["default"]), *enumerate(card.metadata["decisions"])]:
        source, = route_source(card.id, row, "professional")
        assert source["id"] == card.id and decision["explanation"] in source["context"]
        assert all(action in source["context"] for action in decision.get("actions", []))
        for role in ("student", "nursing", "patient"):
            assert not route_source(card.id, row, role)
    assert not route_source(card.id, -1, "professional")
    assert not route_source(card.id, len(card.metadata["decisions"]), "professional")


def test_generation_http_contract_and_abstention():
    question = "Что означает пульсоксиметрия?"
    replies = []
    class LocalModel(BaseHTTPRequestHandler):
        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert self.path == "/api/generate" and payload["model"] == "test"
            data = json.loads(payload["prompt"].split("\n", 1)[1])
            assert data["question"] == question
            assert set(data) == {"question", "sources"}
            evidence = data["sources"][0]["text"]
            reply = [[{"source": 1, "evidence": evidence}], [], [{"source": 1, "evidence": "Постороннее утверждение."}]]
            body = json.dumps({"response": json.dumps({"claims": reply[len(replies)]})}).encode()
            replies.append(True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)

    with ThreadingHTTPServer(("127.0.0.1", 0), LocalModel) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        generate = ollama_generator("test", endpoint=f"http://127.0.0.1:{server.server_port}/api/generate")
        try:
            assert answer_reference(question, generator=generate)["mode"] == "generated"
            assert answer_reference(question, generator=generate)["status"] == "not_found"
            assert answer_reference(question, generator=generate)["mode"] == "extracts"
        finally:
            server.shutdown()
            thread.join()
    assert answer_reference(question, generator=generate)["mode"] == "extracts"


def test_dense_ranking_http_batches_and_fallback():
    from src.reference_embeddings import OllamaRanker

    requests = []
    class LocalEncoder(BaseHTTPRequestHandler):
        def do_POST(self):
            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert self.path == "/api/embed" and data["model"] == "test"
            texts = data["input"]
            requests.append(texts)
            vectors = [[0, 1] if "CURB-65" in text else [1, 0] for text in texts]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"embeddings": vectors}).encode())

    query = "Из чего состоит шкала CURB-65?"
    with ThreadingHTTPServer(("127.0.0.1", 0), LocalEncoder) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        ranker = OllamaRanker("test", endpoint=f"http://127.0.0.1:{server.server_port}/api/embed")
        try:
            first = search_reference(query, ranker=ranker)
            assert first[0]["retrieval"] == "hybrid_semantic" and first[0]["id"] == "PROT-SCALE-004"
            count = len(requests)
            assert count > 1 and search_reference(query, ranker=ranker) == first
            assert len(requests) == count + 1
            assert search_reference("Рецепт карамельного торта", ranker=ranker) == []
            assert len(requests) == count + 1
        finally:
            server.shutdown()
            thread.join()
    assert search_reference(query, ranker=ranker)[0]["retrieval"] == "hybrid_fallback"


def test_verified_quote_preserves_negation_and_complete_numbers():
    from src.reference import _complete_quote
    source = "Тест не пройден. Значение 120 единиц.\nСледующая строка."
    assert not _complete_quote("пройден.", source)
    assert not _complete_quote("20 единиц.", source)
    assert _complete_quote("Значение 120 единиц. Следующая строка.", source)

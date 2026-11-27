"""Локальный HTTP-сервер MedAssist. Запуск: python -m src.web."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
from functools import lru_cache, partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from ..reference_embeddings import OllamaRanker
from ..reference import answer_reference, can_read_card, ollama_generator
from ..solver import ROLES, apply_answers, load_default_kb, solve
from ..solver.inputs import describe_input
from ..repository import KnowledgeRepository
from ..scenarios import ScenarioRunner
from .scenarios import QUICK_EXAMPLES, scenario_list, scenarios

STATIC = Path(__file__).resolve().parent / "static"
FILES = {"/": "index.html", "/app.js": "app.js", "/decision-map.js": "decision-map.js", "/style.css": "style.css",
         "/OpenSans-Regular.woff2": "OpenSans-Regular.woff2", "/OpenSans-Bold.woff2": "OpenSans-Bold.woff2"}
MAX_BODY = 65536
CASE_MAPS = ("params", "facts", "exam_results")


@lru_cache(maxsize=1)
def catalog():
    kb = load_default_kb()
    fields = {}
    for kind, codes in (
        ("param", kb.schema.parameters), ("fact", kb.schema.facts), ("feature", kb.feature_owner),
        ("symptom", [card.id for card in kb.category("symptom")]),
        ("exam_result", [card.id for card in kb.category("exam")]),
    ):
        fields[kind] = sorted((describe_input(code, kb, kind) for code in codes), key=lambda item: item["label"].casefold())
    fields["exam_result"] = [item for item in fields["exam_result"] if item["options"]]
    return {
        "fields": fields,
        "diseases": [{"id": c.id, "title": c.title} for c in kb.category("disease") + kb.category("emergency")],
        "medications": [{"id": c.id, "title": c.title} for c in kb.category("drug") + kb.category("drugclass")],
        "examples": scenario_list(),
        "quick_examples": QUICK_EXAMPLES,
        "counts": {"cards": len(kb.cards), "rules": len(kb.rules)},
    }


@lru_cache(maxsize=4)
def knowledge_catalog(role):
    kb = load_default_kb()
    return [
        {"id": card.id, "title": card.title, "domain": card.domain,
         "category": kb.schema.categories[card.category].title, "tags": card.tags}
        for card in sorted(kb.cards.values(), key=lambda item: (item.title.casefold(), item.id))
        if can_read_card(card.metadata.get("access_level", "professional"), role)
    ]


@lru_cache(maxsize=1)
def scenario_runner():
    return ScenarioRunner(KnowledgeRepository().load())


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, generator=None, ranker=None, **kwargs):
        self.generator = generator
        self.ranker = ranker
        super().__init__(*args, **kwargs)

    def _reply(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data, status=HTTPStatus.OK):
        self._reply(status, json.dumps(data, ensure_ascii=False, allow_nan=False).encode(), "application/json; charset=utf-8")

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in FILES:
            file = STATIC / FILES[path]
            if file.is_file():
                content_type = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
                return self._reply(HTTPStatus.OK, file.read_bytes(), content_type)
        if path == "/api/catalog":
            return self._json(catalog())
        match = re.fullmatch(r"/api/examples/([a-z0-9_]+)", path)
        if match and (case := scenarios().get(match[1])):
            return self._json(case)

        role = parse_qs(urlsplit(self.path).query).get("role", ["professional"])[0]
        if path == "/api/knowledge" or path.startswith(("/api/knowledge/", "/api/knowledge-demos/", "/api/knowledge-rules/")):
            if role not in ROLES:
                return self._json({"error": "Неизвестный режим просмотра."}, HTTPStatus.BAD_REQUEST)
            can_view_rules = role in ("professional", "student")
            if path == "/api/knowledge":
                professional = role == "professional"
                rules = [{"id": rule.id, "title": rule.title} for rule in load_default_kb().rules] if can_view_rules else []
                return self._json({"cards": knowledge_catalog(role), "rules": rules,
                                   "demos": ScenarioRunner.TITLES if professional else {}})
            rule_match = re.fullmatch(r"/api/knowledge-rules/([A-Z0-9_-]+)", path)
            if rule_match and can_view_rules:
                rule = next((item for item in load_default_kb().rules if item.id == rule_match[1]), None)
                if rule:
                    return self._json({"id": rule.id, "title": rule.title, "content": rule.explanation,
                                       "metadata": {"if": rule.condition, "then": rule.actions,
                                                    "source_cards": rule.source_cards, "priority": rule.priority,
                                                    "phase": rule.phase, "file": rule.source_file}})
            demo = re.fullmatch(r"/api/knowledge-demos/([a-z_]+)", path)
            if demo and role == "professional" and demo[1] in ScenarioRunner.TITLES:
                return self._json({"title": ScenarioRunner.TITLES[demo[1]], "content": scenario_runner().run(demo[1])})
            match = re.fullmatch(r"/api/knowledge/([A-Z0-9_-]+)", path)
            if match:
                kb = load_default_kb()
                card = kb.get(match[1])
                if card and can_read_card(card.metadata.get("access_level", "professional"), role):
                    related = []
                    for relation in card.relations:
                        target = kb.get(relation.get("target"))
                        if target and can_read_card(target.metadata.get("access_level", "professional"), role):
                            related.append({"id": target.id, "title": target.title, "type": relation["type"]})
                    return self._json({"id": card.id, "title": card.title, "content": card.content,
                                       "metadata": card.metadata, "sources": card.metadata.get("sources", []),
                                       "related": related})
        self._json({"error": "Страница не найдена."}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ("/api/solve", "/api/reference"):
            return self._json({"error": "Страница не найдена."}, HTTPStatus.NOT_FOUND)
        if self.headers.get_content_type() != "application/json":
            return self._json({"error": "Ожидается запрос в формате JSON."}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if not 0 < length <= MAX_BODY:
            status = HTTPStatus.REQUEST_ENTITY_TOO_LARGE if length > MAX_BODY else HTTPStatus.BAD_REQUEST
            return self._json({"error": "Недопустимый размер запроса."}, status)
        try:
            def invalid_constant(value):
                raise ValueError(f"Недопустимое число: {value}.")

            data = json.loads(self.rfile.read(length), parse_constant=invalid_constant)
            if not isinstance(data, dict):
                raise ValueError("Ожидается объект JSON.")
            role = data.get("role", "professional")
            if role not in ROLES:
                raise ValueError("Неизвестный режим отображения.")
            if path == "/api/reference":
                question = data.get("question")
                if not isinstance(question, str) or not 3 <= len(question.strip()) <= 500:
                    raise ValueError("Введите вопрос от 3 до 500 символов.")
                route = data.get("route_source")
                if route is not None and (not isinstance(route, dict)
                        or set(route) != {"id", "row"} or not isinstance(route["id"], str)
                        or (route["row"] is not None and type(route["row"]) is not int)):
                    raise ValueError("Укажите карточку маршрута и номер строки.")
                return self._json(answer_reference(question.strip(), role, generator=self.generator, ranker=self.ranker, route=route))

            patient = data.get("patient")
            answers = data.get("answers", {})
            if not isinstance(patient, dict) or not isinstance(answers, dict):
                raise ValueError("Описание и ответы должны быть объектами JSON.")
            if answers and any(patient.get(key) is not None and not isinstance(patient[key], dict) for key in CASE_MAPS):
                raise ValueError("Параметры, факты и результаты обследований должны быть объектами JSON.")
            kb = load_default_kb()
            request = {"patient": patient}
            request, issues = apply_answers(request, answers, kb) if answers else (request, [])
            solution = solve(request, role=role, kb=kb)
            for decision in solution.get("routing", {}).get("decisions", []):
                card = kb.get(decision["id"])
                decision["source_available"] = bool(card and can_read_card(card.metadata.get("access_level", "professional"), role))
            return self._json({"patient": request["patient"], "solution": solution, "answer_issues": issues})
        except (ValueError, RecursionError) as error:
            return self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ollama-model", default=os.environ.get("MEDASSIST_OLLAMA_MODEL"))
    parser.add_argument("--ollama-embed-model", default=os.environ.get("MEDASSIST_OLLAMA_EMBED_MODEL"))
    args = parser.parse_args()
    generator = ollama_generator(args.ollama_model) if args.ollama_model else None
    ranker = OllamaRanker(args.ollama_embed_model) if args.ollama_embed_model else None
    with ThreadingHTTPServer((args.host, args.port), partial(Handler, generator=generator, ranker=ranker)) as server:
        print(f"MedAssist: http://{args.host}:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

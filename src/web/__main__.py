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
from urllib.parse import urlsplit

import yaml

from ..reference import answer_reference, ollama_generator
from ..solver import ROLES, apply_answers, load_default_kb, solve
from ..solver.inputs import describe_input

STATIC = Path(__file__).resolve().parent / "static"
EXAMPLES = STATIC.parents[2] / "examples"
FILES = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css",
         "/OpenSans-Regular.woff2": "OpenSans-Regular.woff2", "/OpenSans-Bold.woff2": "OpenSans-Bold.woff2"}
MAX_BODY = 65536
DEMO_NAMES = {
    "pneumonia": "Кашель и лихорадка", "pneumonia_no_urea": "Кашель и неполные данные",
    "chest_pain_acs": "Боль в груди", "migraine": "Головная боль",
}
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
        "examples": [{"id": ident, "title": name} for ident, name in DEMO_NAMES.items()
                     if (EXAMPLES / f"{ident}.yaml").is_file()],
        "counts": {"cards": len(kb.cards), "rules": len(kb.rules)},
    }


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, generator=None, **kwargs):
        self.generator = generator
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
        if match and match[1] in DEMO_NAMES:
            file = EXAMPLES / f"{match[1]}.yaml"
            if file.is_file():
                content = yaml.safe_load(file.read_text(encoding="utf-8"))
                return self._json({"title": DEMO_NAMES[match[1]], "request": content})
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
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("Ожидается объект JSON.")
            role = data.get("role", "professional")
            if role not in ROLES:
                raise ValueError("Неизвестный режим отображения.")
            if path == "/api/reference":
                question = data.get("question")
                if not isinstance(question, str) or not 3 <= len(question.strip()) <= 500:
                    raise ValueError("Введите вопрос от 3 до 500 символов.")
                return self._json(answer_reference(question.strip(), role, generator=self.generator))

            patient = data.get("patient")
            answers = data.get("answers", {})
            if not isinstance(patient, dict) or not isinstance(answers, dict):
                raise ValueError("Описание и ответы должны быть объектами JSON.")
            if answers and any(key in patient and not isinstance(patient[key], dict) for key in CASE_MAPS):
                raise ValueError("Параметры, факты и результаты обследований должны быть объектами JSON.")
            kb = load_default_kb()
            request = {"patient": patient}
            request, issues = apply_answers(request, answers, kb) if answers else (request, [])
            solution = solve(request, role=role, kb=kb)
            return self._json({"patient": request["patient"], "solution": solution, "answer_issues": issues})
        except (ValueError, RecursionError) as error:
            return self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ollama-model", default=os.environ.get("MEDASSIST_OLLAMA_MODEL"))
    args = parser.parse_args()
    generator = ollama_generator(args.ollama_model) if args.ollama_model else None
    with ThreadingHTTPServer((args.host, args.port), partial(Handler, generator=generator)) as server:
        print(f"MedAssist: http://{args.host}:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

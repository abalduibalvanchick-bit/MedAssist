"""Уточняющий диалог: ответы на вопросы решателя и повторное решение задачи.

Цикл диалога (требование Ф6):

    повторять не более max_dialog_rounds раз (параметр схемы solver):
        1. решить задачу для текущего описания пациента;
        2. собрать поля ввода из уточняющих вопросов, которые ещё не задавались;
        3. если таких нет — завершить;
        4. получить ответы (интерфейс, консоль или тест передаёт функцию ask);
        5. если ни на одно поле не ответили — завершить;
        6. подставить ответы в описание пациента (apply_answers) и вернуться к 1.

Неотвеченное поле больше не запрашивается: пользователь мог не знать значение.
Каждый раунд сохраняется в истории, чтобы было видно, как ответы изменили вывод.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Callable

from .api import solve
from .inputs import describe_input
from .knowledge import KnowledgeBase, load_default_kb

_TRUE = {"true", "1", "да", "д", "yes", "y", "есть", "+"}
_FALSE = {"false", "0", "нет", "н", "no", "n", "-"}


@dataclass
class DialogRound:
    number: int
    asked: list[dict[str, Any]]
    answers: dict[str, Any]
    status: str
    urgency: str


@dataclass
class DialogResult:
    request: dict[str, Any]
    solution: dict[str, Any]
    rounds: list[DialogRound] = field(default_factory=list)
    issues: list[dict[str, str]] = field(default_factory=list)


def pending_inputs(solution: dict[str, Any], asked: set[str] | None = None) -> list[dict[str, Any]]:
    """Поля ввода из вопросов решения без повторов, в порядке важности вопросов."""
    asked = asked or set()
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for question in solution.get("questions") or []:
        for item in question.get("inputs") or []:
            code = item["code"]
            if code in seen or code in asked:
                continue
            seen.add(code)
            result.append(item)
    return result


def _to_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    return None


def _to_number(value: Any) -> float | int | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(str(value).strip().replace(",", "."))
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def _patient(request: dict[str, Any]) -> dict[str, Any]:
    if "patient" not in request or not isinstance(request["patient"], dict):
        request["patient"] = {}
    return request["patient"]


def _add_to_list(patient: dict[str, Any], key: str, code: str) -> None:
    values = patient.get(key) or []
    if isinstance(values, str):
        values = [values]
    if code not in values:
        values = [*values, code]
    patient[key] = values


def _remove_from_list(patient: dict[str, Any], key: str, code: str) -> None:
    values = patient.get(key) or []
    if isinstance(values, list) and code in values:
        patient[key] = [v for v in values if v != code]


def apply_answers(request: dict[str, Any], answers: dict[str, Any],
                  kb: KnowledgeBase | None = None) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Подставляет ответы {код поля: значение} в копию описания пациента.

    Возвращает новое описание и список замечаний (неизвестный код, значение не того типа).
    Исходный запрос не изменяется. Проверку диапазонов выполняет решатель при разборе.
    """
    kb = kb or load_default_kb()
    new_request = copy.deepcopy(request) if isinstance(request, dict) else {}
    patient = _patient(new_request)
    issues: list[dict[str, str]] = []

    def issue(code: str, message: str) -> None:
        issues.append({"severity": "warning", "code": code, "message": message})

    for code, raw in answers.items():
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            continue
        item = describe_input(str(code), kb)
        if item is None:
            issue("UNKNOWN_INPUT", f"Поле «{code}» не найдено в словаре базы знаний; ответ пропущен.")
            continue
        kind = item["kind"]
        if item["type"] == "boolean":
            value = _to_bool(raw)
            if value is None:
                issue("BAD_ANSWER", f"«{item['label']}»: ожидается да/нет, получено {raw!r}.")
                continue
            if kind == "param":
                patient.setdefault("params", {})[code] = value
            elif kind == "fact":
                patient.setdefault("facts", {})[code] = value
            elif kind == "feature":
                _add_to_list(patient, "features" if value else "denied_features", code)
                _remove_from_list(patient, "denied_features" if value else "features", code)
            elif kind == "symptom":
                _add_to_list(patient, "symptoms" if value else "denied_symptoms", code)
                _remove_from_list(patient, "denied_symptoms" if value else "symptoms", code)
        elif item["type"] == "number":
            number = _to_number(raw)
            if number is None:
                issue("BAD_ANSWER", f"«{item['label']}»: ожидается число, получено {raw!r}.")
                continue
            if code == "age":
                patient.pop("age", None)
            patient.setdefault("params", {})[code] = number
        elif item["type"] == "choice":
            options = {o["value"]: o["value"] for o in item["options"]}
            options.update({o["label"].lower(): o["value"] for o in item["options"]})
            choice = options.get(str(raw).strip()) or options.get(str(raw).strip().lower())
            if choice is None and str(raw).strip().isdigit():
                index = int(str(raw).strip()) - 1
                if 0 <= index < len(item["options"]):
                    choice = item["options"][index]["value"]
            if choice is None:
                issue("BAD_ANSWER", f"«{item['label']}»: нет варианта {raw!r}.")
                continue
            patient.setdefault("exam_results", {})[code] = choice
    return new_request, issues


def run_dialog(request: dict[str, Any], ask: Callable[[dict[str, Any]], Any], *, role: str = "professional",
               kb: KnowledgeBase | None = None, max_rounds: int | None = None) -> DialogResult:
    """Ведёт уточняющий диалог. ask(поле) возвращает значение или None (не известно)."""
    kb = kb or load_default_kb()
    rounds_limit = int(max_rounds if max_rounds is not None else kb.schema.solver_setting("max_dialog_rounds", 5))
    current = copy.deepcopy(request)
    asked: set[str] = set()
    result = DialogResult(request=current, solution=solve(current, role=role, kb=kb))
    for number in range(1, rounds_limit + 1):
        solution = result.solution
        if solution.get("status") in ("invalid", "refused"):
            break
        items = pending_inputs(solution, asked)
        if not items:
            break
        answers: dict[str, Any] = {}
        for item in items:
            asked.add(item["code"])
            value = ask(item)
            if value is not None and not (isinstance(value, str) and not value.strip()):
                answers[item["code"]] = value
        if not answers:
            break
        current, issues = apply_answers(current, answers, kb)
        result.issues.extend(issues)
        result.request = current
        result.solution = solve(current, role=role, kb=kb)
        result.rounds.append(DialogRound(number, items, answers, result.solution.get("status", ""),
                                         (result.solution.get("urgency") or {}).get("level", "")))
    return result

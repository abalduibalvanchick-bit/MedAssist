"""Постановка задачи: описание пациента и проверка входных данных.

Вход решателя — словарь (из YAML, JSON или интерфейса):

    patient:
      age: 62
      symptoms: [DIAG-SYMPTOM-002]
      features: [chest_pain.pressing, chest_pain.at_rest]
      denied_symptoms: [DIAG-SYMPTOM-004]
      denied_features: [headache.sudden_onset]
      params: {sbp: 150, symptom_duration_min: 30}
      facts: {smoker: true, pregnant: false}
      diseases: [DIAG-DISEASE-001]            # уже установленные диагнозы
      exam_results: {DIAG-EXAM-002: st_elevation}

Модуль проверяет коды по базе знаний, значения по диапазонам схемы и
противоречия между сообщёнными данными. Логические противоречия
(симптом и есть, и отрицается) проверяются здесь; содержательные
(невозможные сочетания значений) задаются в схеме, раздел input_constraints.
Ошибки не приводят к падению:
они возвращаются списком, а решатель решает, можно ли продолжать.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from ..conditions import PatientFacts, Truth, compare, evaluate
from .explain import justify, justify_false
from .knowledge import KnowledgeBase


@dataclass(frozen=True)
class InputIssue:
    severity: str  # error | warning
    code: str
    message: str


@dataclass
class ParsedCase:
    facts: PatientFacts
    issues: list[InputIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)


def check_input_constraints(facts: PatientFacts, schema) -> list[str]:
    """Проверяет ограничения input_constraints схемы. Возвращает сообщения о нарушениях.

    Ограничение проверяется только тогда, когда сообщены все нужные данные:
    неизвестное значение не считается нарушением (трёхзначная логика).
    """
    messages: list[str] = []
    for item in schema.input_constraints:
        violated = False
        if "compare" in item:
            spec = item["compare"]
            left, right = facts.params.get(spec["left"]), facts.params.get(spec["right"])
            if isinstance(left, (int, float)) and isinstance(right, (int, float)) \
                    and not isinstance(left, bool) and not isinstance(right, bool):
                violated = not compare(float(left), spec["op"], float(right))
        elif "forbid" in item:
            violated = evaluate(item["forbid"], facts, schema) is Truth.TRUE
        if violated:
            values = {k: (f"{v:g}" if isinstance(v, float) else v) for k, v in facts.params.items()}
            try:
                messages.append(str(item["message"]).format(**values))
            except (KeyError, IndexError, ValueError):
                messages.append(str(item["message"]))
    return messages


def derive_facts(facts: PatientFacts, kb: KnowledgeBase) -> list[tuple[str, str]]:
    """Достраивает факты по словарю схемы. Возвращает предупреждения (код, текст).

    derived_from: факт, не сообщённый явно, выводится из измерения (САД 80 →
    гипотензия; САД 120 → гипотензии нет). Если сообщённое значение противоречит
    измерению, используется измерение: решатель не должен пропустить опасное
    состояние из-за устаревшего или ошибочного ответа.
    implies_disease: истинный факт «ранее установленное заболевание» делает это
    заболевание установленным диагнозом.
    """
    schema = kb.schema
    warnings: list[tuple[str, str]] = []
    for name, spec in sorted(schema.facts.items()):
        condition = spec.get("derived_from")
        if not condition:
            continue
        truth = evaluate(condition, facts, schema)
        if truth is Truth.UNKNOWN:
            continue
        value = truth is Truth.TRUE
        because = justify(condition, facts, kb) if value else [f"нет: {line}" for line in justify_false(condition, facts, kb)]
        reported = facts.facts.get(name)
        if reported is not None and reported == value:
            continue
        label = spec.get("label", name)
        if reported is not None:
            warnings.append(("INCONSISTENT_FACT",
                             f"Сообщено «{label}: {'да' if reported else 'нет'}», но по измерению ({'; '.join(because)}) "
                             f"— {'да' if value else 'нет'}; используется значение по измерению."))
        facts.facts[name] = value
        facts.derived.append({"code": name, "kind": "fact", "value": value, "because": because, "source": "schema.facts"})
    for name, spec in sorted(schema.facts.items()):
        disease = spec.get("implies_disease")
        # Установленный диагноз, переданный списком diseases, означает и факт анамнеза.
        if disease and disease in facts.diseases and name not in facts.facts:
            facts.facts[name] = True
            facts.derived.append({"code": name, "kind": "fact", "value": True,
                                  "because": [f"установленный диагноз: {kb.title(disease)}"], "source": "schema.facts"})
            continue
        if disease and facts.facts.get(name) is True and disease not in facts.diseases:
            facts.diseases.add(disease)
            facts.derived.append({"code": disease, "kind": "disease", "value": True,
                                  "because": [spec.get("label", name)], "source": "schema.facts"})
    return warnings


_LIST_KEYS = ("symptoms", "features", "denied_symptoms", "denied_features", "diseases")
_KNOWN_KEYS = set(_LIST_KEYS) | {"age", "params", "facts", "exam_results", "sex", "note"}


def parse_case(data: Any, kb: KnowledgeBase) -> ParsedCase:
    """Строит факты о пациенте из входного словаря и проверяет их."""
    issues: list[InputIssue] = []

    def err(code: str, msg: str) -> None:
        issues.append(InputIssue("error", code, msg))

    def warn(code: str, msg: str) -> None:
        issues.append(InputIssue("warning", code, msg))

    if isinstance(data, dict) and "patient" in data:
        data = data["patient"]
    if not isinstance(data, dict):
        err("BAD_INPUT", "Описание пациента должно быть словарём.")
        return ParsedCase(PatientFacts(), issues)
    for key in sorted(set(data) - _KNOWN_KEYS):
        warn("UNKNOWN_KEY", f"Поле «{key}» не используется решателем и пропущено.")

    lists: dict[str, set[str]] = {}
    for key in _LIST_KEYS:
        value = data.get(key) or []
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            err("BAD_INPUT", f"Поле «{key}» должно быть списком.")
            value = []
        lists[key] = {str(v).strip() for v in value if str(v).strip()}

    facts = PatientFacts()
    schema = kb.schema

    # --- симптомы и признаки
    for key in ("symptoms", "denied_symptoms"):
        for sid in sorted(lists[key]):
            card = kb.get(sid)
            if card is None or card.category != "symptom":
                err("UNKNOWN_SYMPTOM", f"Симптом {sid} отсутствует в базе знаний.")
                continue
            (facts.symptoms if key == "symptoms" else facts.denied_symptoms).add(sid)
    for key in ("features", "denied_features"):
        for code in sorted(lists[key]):
            owner = kb.feature_owner.get(code)
            if owner is None:
                err("UNKNOWN_FEATURE", f"Признак {code} не объявлен ни в одной карточке симптома.")
                continue
            if key == "features":
                facts.features.add(code)
                # Сообщённый признак подразумевает наличие самого симптома.
                if owner not in facts.symptoms and owner not in facts.denied_symptoms:
                    facts.symptoms.add(owner)
            else:
                facts.denied_features.add(code)

    for sid in sorted(facts.symptoms & facts.denied_symptoms):
        err("CONTRADICTION", f"Симптом «{kb.title(sid)}» указан одновременно как имеющийся и отсутствующий.")
    for code in sorted(facts.features & facts.denied_features):
        err("CONTRADICTION", f"Признак «{kb.label('feature', code)}» указан одновременно как имеющийся и отсутствующий.")
    for code in sorted(facts.features):
        owner = kb.feature_owner[code]
        if owner in facts.denied_symptoms:
            err("CONTRADICTION", f"Указан признак «{kb.label('feature', code)}», но симптом «{kb.title(owner)}» отрицается.")

    # --- диагнозы
    for did in sorted(lists["diseases"]):
        card = kb.get(did)
        if card is None or card.category not in ("disease", "emergency"):
            err("UNKNOWN_DISEASE", f"Диагноз {did} отсутствует в базе знаний.")
            continue
        facts.diseases.add(did)

    # --- параметры
    raw_params = data.get("params") or {}
    if not isinstance(raw_params, dict):
        err("BAD_INPUT", "Поле «params» должно быть словарём вида {код: значение}.")
        raw_params = {}
    params = dict(raw_params)
    if data.get("age") is not None:
        params.setdefault("age", data["age"])
    for name, value in sorted(params.items()):
        spec = schema.parameters.get(name)
        if spec is None:
            err("UNKNOWN_PARAM", f"Параметр {name} не описан в схеме базы знаний.")
            continue
        if spec.get("type") == "boolean":
            if not isinstance(value, bool):
                err("BAD_VALUE", f"Параметр «{spec.get('label', name)}» должен быть логическим (true/false).")
                continue
            facts.params[name] = value
            continue
        if isinstance(value, bool):
            err("BAD_VALUE", f"Параметр «{spec.get('label', name)}» должен быть числом.")
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            err("BAD_VALUE", f"Параметр «{spec.get('label', name)}» должен быть числом, получено {value!r}.")
            continue
        if not math.isfinite(number):
            err("BAD_VALUE", f"Параметр «{spec.get('label', name)}» должен быть конечным числом, получено {value!r}.")
            continue
        lo, hi = spec.get("min"), spec.get("max")
        if (lo is not None and number < lo) or (hi is not None and number > hi):
            err("OUT_OF_RANGE", f"{spec.get('label', name)} = {value}: вне допустимого диапазона {lo}–{hi}.")
            continue
        facts.params[name] = int(number) if number.is_integer() else number

    # --- факты
    raw_facts = data.get("facts") or {}
    if not isinstance(raw_facts, dict):
        err("BAD_INPUT", "Поле «facts» должно быть словарём вида {код: true/false}.")
        raw_facts = {}
    for name, value in sorted(raw_facts.items()):
        if name not in schema.facts:
            err("UNKNOWN_FACT", f"Факт {name} не описан в схеме базы знаний.")
            continue
        if not isinstance(value, bool):
            err("BAD_VALUE", f"Факт «{schema.facts[name].get('label', name)}» должен быть true или false.")
            continue
        facts.facts[name] = value

    # --- факты, выводимые из измерений, и ранее установленные диагнозы (словарь схемы)
    for issue_code, message in derive_facts(facts, kb):
        warn(issue_code, message)

    # --- ограничения согласованности из схемы (input_constraints)
    for message in check_input_constraints(facts, schema):
        err("CONTRADICTION", message)

    # --- результаты обследований
    raw_exams = data.get("exam_results") or {}
    if not isinstance(raw_exams, dict):
        err("BAD_INPUT", "Поле «exam_results» должно быть словарём вида {ID обследования: код результата}.")
        raw_exams = {}
    for exam_id, value in sorted(raw_exams.items()):
        card = kb.get(exam_id)
        if card is None or card.category != "exam":
            err("UNKNOWN_EXAM", f"Обследование {exam_id} отсутствует в базе знаний.")
            continue
        allowed = {str(r.get("value")) for r in card.metadata.get("results") or [] if isinstance(r, dict)}
        if str(value) not in allowed:
            err("BAD_VALUE", f"Для «{card.title}» нет результата «{value}»; допустимо: {', '.join(sorted(allowed))}.")
            continue
        facts.exam_results[exam_id] = str(value)

    if not (facts.symptoms or facts.params or facts.facts or facts.diseases or facts.exam_results):
        warn("EMPTY_INPUT", "О пациенте ничего не сообщено.")
    return ParsedCase(facts, issues)

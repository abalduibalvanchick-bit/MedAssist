"""Инварианты решателя на случайных корректных пациентах (свойство-ориентированное тестирование).

Перебрать все сочетания данных невозможно (16 симптомов, десятки признаков, 35 параметров,
34 факта), поэтому вместо отдельных ответов проверяются свойства, которые обязаны выполняться
для любого пациента. Пациенты генерируются с фиксированным зерном — результат воспроизводим.

  I1  срочность не ниже срочности любого распознанного красного флага или неотложного состояния;
  I2  монотонность: новая жалоба (признак) не понижает срочность, не убирает распознанное опасное
      состояние и не уменьшает вес гипотезы — знания только добавляют выводы;
  I3  объяснимость: у каждого опасного состояния, маршрута и предупреждения есть шаг в трассе;
  I4  «нужны данные» всегда сопровождается хотя бы одним вопросом (требование Ф6);
  I5  обследование не находится одновременно в двух списках (рекомендовано / выполнено / отложено);
  I6  отказ (вне области применимости) не содержит диагностических выводов;
  I7  пациенту не показываются гипотезы, обследования, предупреждения и ход вывода;
  I8  маршрут: экстренный маршрут означает экстренную срочность; итоговый маршрут не легче
      маршрута любой карточки и правила; предварительный маршрут сопровождается вопросом.
"""

from __future__ import annotations

import random

import pytest

from src.solver import load_default_kb, solve

KB = load_default_kb()
ORDER = ["elective", "routine", "urgent", "emergency"]
N_PATIENTS = 600


def _valid_patient(rnd: random.Random) -> dict:
    schema = KB.schema
    features = list(KB.feature_owner)
    symptoms = [c.id for c in KB.category("symptom")]
    patient = {"age": rnd.randint(18, 95), "features": rnd.sample(features, rnd.randint(0, 4))}
    owners = {KB.feature_owner[f] for f in patient["features"]}
    patient["symptoms"] = [s for s in rnd.sample(symptoms, rnd.randint(0, 2)) if s not in owners]
    params = {}
    for name in rnd.sample([p for p in schema.parameters if p != "age"], rnd.randint(0, 6)):
        spec = schema.parameters[name]
        params[name] = (rnd.random() < 0.5) if spec.get("type") == "boolean" else \
            round(rnd.uniform(spec.get("min", 0), spec.get("max", 100)), 1)
    if "sbp" in params and "dbp" in params and params["sbp"] <= params["dbp"]:
        del params["dbp"]
    patient["params"] = params
    patient["facts"] = {k: rnd.random() < 0.3 for k in rnd.sample(list(schema.facts), rnd.randint(0, 4))}
    return patient


def _patients():
    rnd = random.Random(2026)
    return [(_valid_patient(rnd), rnd.choice(list(KB.feature_owner))) for _ in range(N_PATIENTS)]


PATIENTS = _patients()


def _ids(items):
    return {x["id"] for x in items}


def test_invariants_hold_for_random_valid_patients():
    violations: list[str] = []
    checked = 0
    for patient, extra_feature in PATIENTS:
        s = solve({"patient": patient}, kb=KB)
        if s["status"] == "invalid":
            continue
        checked += 1
        level = s["urgency"]["level"]
        for item in s["red_flags"] + s["emergencies"]:
            if ORDER.index(KB.card_urgency(item["id"])) > ORDER.index(level):
                violations.append(f"I1 {item['id']} при срочности {level}: {patient}")
        sources = {t["source"] for t in s["trace"]}
        for item in s["red_flags"] + s["emergencies"]:
            if item["id"] not in sources:
                violations.append(f"I3 нет шага трассы для {item['id']}: {patient}")
        for item in s["warnings"] + s["routes"]:
            if item["source"] not in sources:
                violations.append(f"I3 нет шага трассы для {item['source']}: {patient}")
        if s["status"] == "need_more_data" and not s["questions"]:
            violations.append(f"I4 нет вопросов: {patient}")
        a, b, c = _ids(s["exams"]), _ids(s["completed_exams"]), _ids(s["deferred_exams"])
        if a & b or a & c or b & c:
            violations.append(f"I5 обследование в двух списках: {patient}")
        if s["status"] == "refused" and (s["hypotheses"] or s["red_flags"] or s["emergencies"]):
            violations.append(f"I6 отказ с выводами: {patient}")
        routing = s["routing"]
        severity = KB.schema.solver_setting("route_severity", [])
        rank = severity.index(routing["route"]) if routing["route"] in severity else -1
        if routing["route"] == "emergency" and level != "emergency":
            violations.append(f"I8 экстренный маршрут при срочности {level}: {patient}")
        for item in routing["decisions"] + s["routes"]:
            if severity.index(item["route"]) > rank:
                violations.append(f"I8 итоговый маршрут легче {item['route']}: {patient}")
        if routing["provisional"] and not any(q["kind"] == "routing" for q in s["questions"]):
            violations.append(f"I8 предварительный маршрут без вопроса: {patient}")
        lay = solve({"patient": patient}, role="patient", kb=KB)
        if any(key in lay for key in ("hypotheses", "exams", "warnings", "trace", "explanation")):
            violations.append(f"I7 служебные сведения пациенту: {patient}")
        if s["status"] != "refused" and extra_feature not in patient["features"]:
            more = solve({"patient": {**patient, "features": patient["features"] + [extra_feature]}}, kb=KB)
            if more["status"] in ("invalid", "refused"):
                continue
            if ORDER.index(more["urgency"]["level"]) < ORDER.index(level):
                violations.append(f"I2 срочность понизилась после {extra_feature}: {patient}")
            lost = _ids(s["red_flags"] + s["emergencies"]) - _ids(more["red_flags"] + more["emergencies"])
            if lost:
                violations.append(f"I2 пропало {lost} после {extra_feature}: {patient}")
            before = {h["id"]: h["score"] for h in s["hypotheses"]}
            after = {h["id"]: h["score"] for h in more["hypotheses"]}
            if any(after.get(k, 0) < v for k, v in before.items()):
                violations.append(f"I2 вес гипотезы уменьшился после {extra_feature}: {patient}")
    assert checked > N_PATIENTS * 0.8
    assert not violations, f"{len(violations)} нарушений, первые: " + " | ".join(violations[:3])


@pytest.mark.parametrize("symptom", [c.id for c in KB.category("symptom")])
def test_single_complaint_always_gets_a_question_or_conclusion(symptom):
    s = solve({"patient": {"age": 40, "symptoms": [symptom]}}, kb=KB)
    assert s["status"] in ("ok", "need_more_data")
    if s["status"] == "need_more_data":
        assert s["questions"], f"по жалобе {symptom} не задано ни одного вопроса"

"""Человекочитаемое представление решения (консоль, демонстрация)."""

from __future__ import annotations

from typing import Any

_STATUS = {"ok": "решение получено", "need_more_data": "нужны дополнительные данные",
           "refused": "отказ: вне области применимости", "invalid": "некорректные входные данные"}
_ROUTES = {"outpatient": "амбулаторно", "urgent_referral": "срочное направление к специалисту",
           "hospitalization": "госпитализация", "emergency": "экстренная помощь"}


def format_solution(solution: dict[str, Any], *, show_trace: bool = True) -> str:
    out: list[str] = []
    add = out.append
    lay = solution.get("role") == "patient"   # для пациента без служебных идентификаторов

    def ref(item_id: str) -> str:
        return "" if lay else f" [{item_id}]"

    add(f"Статус: {_STATUS.get(solution.get('status'), solution.get('status'))}")
    for issue in solution.get("input_issues") or []:
        add(f"  [{issue['severity']}] {issue['message']}")
    if solution.get("status") == "invalid":
        return "\n".join(out)
    if solution.get("refusal"):
        add(f"Отказ ({solution['refusal']['source']}): {solution['refusal']['text']}")
    urgency = solution.get("urgency") or {}
    if urgency:
        add(f"Срочность: {urgency.get('label', urgency.get('level'))}")
        for reason in urgency.get("reasons") or []:
            add(f"  основание: {reason['reason']}{ref(reason['source'])}")

    def section(title: str, items: list[str]) -> None:
        if items:
            add(f"{title}:")
            out.extend(f"  - {line}" for line in items)

    section("Профили пациента", [p["title"] for p in solution.get("profiles") or []])
    section("Красные флаги", [f"{r['title']}{ref(r['id'])}" for r in solution.get("red_flags") or []])
    section("Неотложные состояния", [f"{e['title']}{ref(e['id'])}" for e in solution.get("emergencies") or []])
    section("Гипотезы", [f"{h['title']} — вес {h['score']} ({', '.join(h['sources'])})" for h in solution.get("hypotheses") or []])
    section("Рабочие диагнозы", [f"{d['title']}{ref(d['id'])}" for d in solution.get("working_diagnoses") or []])
    section("Шкалы", [f"{s['title']}: " + (f"{s['value']:g} балл(ов), " if s.get("value") is not None else f"{s['range'][0]:g}–{s['range'][1]:g}, ")
                      + f"{s['category_label']}" for s in solution.get("scales") or []])
    section("Обследования", [f"{e['title']} ({', '.join(e['roles'])})" for e in solution.get("exams") or []])
    section("Маршрут", [f"{_ROUTES.get(r['route'], r['route'])}" + (f", {r['timeframe']}" if r.get("timeframe") else "") + f" [{r['source']}]"
                        for r in solution.get("routes") or []])
    section("Дальнейшие действия", [f"{p['title']} [{p['id']}]" for p in solution.get("protocols") or []])
    section("Предупреждения", [f"{w['text']} [{w['source']}]" for w in solution.get("warnings") or []])
    questions = []
    for q in solution.get("questions") or []:
        questions.append(q["text"] + (f" ({'; '.join(q['ask'])})" if q.get("ask") else ""))
    section("Уточняющие вопросы", questions)
    for item in solution.get("advice") or []:
        section(f"Когда срочно обратиться к врачу ({item['title']})", item["seek_help_when"])
    if show_trace and solution.get("explanation"):
        add("Ход вывода:")
        out.extend("  " + line for line in solution["explanation"].splitlines())
    for text in solution.get("disclaimer") or []:
        add(f"! {text}")
    stats = solution.get("stats") or {}
    if stats and not lay:
        add(f"Итераций: {stats.get('iterations', '-')}, сработало правил: {stats.get('rules_fired', '-')} из "
            f"{stats.get('rules_total', '-')}, время решения: {stats.get('time_ms')} мс")
    return "\n".join(out)

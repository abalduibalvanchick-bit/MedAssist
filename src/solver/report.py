"""Человекочитаемое представление решения (консоль, демонстрация)."""

from __future__ import annotations

from typing import Any

_STATUS = {"ok": "решение получено", "need_more_data": "нужны дополнительные данные",
           "refused": "отказ: вне области применимости", "invalid": "некорректные входные данные"}
_ROLES = {"confirms": "подтверждение", "supports": "поддержка гипотезы", "excludes": "исключение",
          "stratifies": "оценка тяжести", "monitors": "контроль"}
_ROUTES = {"outpatient": "амбулаторно", "urgent_referral": "срочное направление к специалисту",
           "hospitalization": "госпитализация", "emergency": "экстренная помощь"}


def format_solution(solution: dict[str, Any], *, show_trace: bool = True) -> str:
    out: list[str] = []
    add = out.append
    lay = solution.get("role") == "patient"   # для пациента без служебных идентификаторов

    def ref(item_id: str) -> str:
        return "" if lay else f" [{item_id}]"

    outcome = solution.get("outcome") or {}
    add(outcome.get("title") or f"Статус: {_STATUS.get(solution.get('status'), solution.get('status'))}")
    for key in ("summary", "next_step"):
        if outcome.get(key):
            add(outcome[key])
    for issue in solution.get("input_issues") or []:
        add(f"  [{issue['severity']}] {issue['message']}")
    if solution.get("status") == "invalid":
        return "\n".join(out)
    if solution.get("refusal") and not outcome:
        add(f"Отказ ({solution['refusal']['source']}): {solution['refusal']['text']}")
    urgency = solution.get("urgency") or {}
    if urgency and (not outcome or outcome.get("urgency")):
        add(f"Срочность: {urgency.get('label', urgency.get('level'))}")
        if not lay:
            for reason in urgency.get("reasons") or []:
                add(f"  основание: {reason['reason']}{ref(reason['source'])}")

    def section(title: str, items: list[str]) -> None:
        if items:
            add(f"{title}:")
            out.extend(f"  - {line}" for line in items)

    section("Профили пациента", [p["title"] for p in solution.get("profiles") or []])
    section("Красные флаги", [f"{r['title']}{ref(r['id'])}" for r in solution.get("red_flags") or []])
    if not lay:
        section("Неотложные состояния", [f"{e['title']}{ref(e['id'])}" for e in solution.get("emergencies") or []])
    for h in solution.get("hypotheses", []):
        priority = " (приоритет по срочности)" if h.get("time_critical_priority") else ""
        add(f"Гипотеза: {h['title']} — вес правил {h['score']}, оценка {h.get('rank_score', h['score'])}{priority}")
        for argument in h.get("arguments", []):
            add(f"  {argument['contribution']:+g} {argument['title']}")
    section("Рабочие диагнозы", [f"{d['title']}{ref(d['id'])}" for d in solution.get("working_diagnoses") or []])
    for table in solution.get("differential", []):
        section(table["title"], [
            f"{branch['title']} — {branch['label']}"
            + (f". За: {', '.join(branch['for'])}" if branch["for"] else "")
            + (f". Против: {', '.join(branch['against'])}" if branch["against"] else "")
            + (f". Ключевое обследование: {branch['key_exam']['title']}"
               if branch["key_exam"] and branch["key_exam"]["recommended"] and not branch["key_exam"]["completed"] else "")
            for branch in table["branches"]
        ])
    section("Шкалы", [f"{s['title']}: " + (f"{s['value']:g} балл(ов), " if s.get("value") is not None else f"{s['range'][0]:g}–{s['range'][1]:g}, ")
                      + f"{s['category_label']}" for s in solution.get("scales") or []])
    section("Обследования", [f"{e['title']} — {', '.join(_ROLES.get(r, r) for r in e['roles'])}" for e in solution.get("exams") or []])
    def _results(item: dict[str, Any]) -> str:
        return "; ".join(f"{r['label']} = {r['value']}" for r in item.get("results") or [])

    section("Уже выполнено", [f"{e['title']}: {_results(e)}" for e in solution.get("completed_exams") or []])
    section("После стабилизации (плановое обследование)",
            [f"{e['title']} — {', '.join(_ROLES.get(r, r) for r in e['roles'])}" for e in solution.get("deferred_exams") or []])
    routing = solution.get("routing") or {}
    if routing.get("route"):
        head = routing["label"] + (f", {routing['timeframe']}" if routing.get("timeframe") else "")
        if routing.get("provisional") or outcome.get("provisional"):
            head += " (предварительно: более тяжёлый маршрут не исключён, см. вопросы)"
        add(f"Маршрут: {head}" + ("" if lay else f" [{', '.join(routing.get('sources') or [])}]"))
        for d in routing.get("decisions") or []:
            row = "по умолчанию" if d["row"] is None else f"строка {d['row'] + 1}"
            add(f"  - {d['title']}: {d['label']}" + (f", {d['timeframe']}" if d.get("timeframe") else "") + f" ({row})")
            out.extend(f"      · {a}" for a in d.get("actions") or [])
    for plan in solution.get("protocols", []):
        add(f"Протокол: {plan['title']}{ref(plan['id'])}")
        if plan.get("status") in ("conditional", "not_applicable"):
            add("  " + ("Применимость требует уточнения" if plan["status"] == "conditional" else "Неприменим"))
            add("  " + plan["entry"]["reason"])
        for branch in plan.get("branches", []):
            if branch["truth"] == "true":
                add(f"  Переход: {branch['explanation']}{ref(branch['then'])}")
        for step in plan.get("steps", []):
            label = {"applicable": "применим", "conditional": "уточнить условие", "not_required": "не требуется"}
            add(f"  {step['action']} — {label[step['status']]}")
            for item in step["refs"]:
                if item.get("results"):
                    add(f"    Известный результат: {item['title']} — {_results(item)}")
        for target in plan.get("targets", []):
            status = {"achieved": "достигнут", "not_achieved": "не достигнут", "unknown": "нет данных"}
            add(f"  {target['label']} — {status[target['status']]}")
        for phase in plan.get("phases", []):
            section(phase["window"], phase["steps"])
    for follow in solution.get("follow_up", []):
        section(follow["title"], [f"{row['after']}: {row['interval']} — {row['purpose']}" for row in follow["schedule"]])
    therapy = solution.get("therapy") or {}
    for regime in therapy.get("regimens", []):
        add(f"Схема терапии: {regime['title']}{ref(regime['id'])}")
        for line in regime["lines"]:
            section(f"Линия {line['line']}", [
                f"{option['title']} — {option['label']}"
                + "".join(f". {item['text']}{ref(item['source'])}"
                          for item in option["reasons"] + option["dose_notes"])
                for option in line["options"]
            ])
    section("Взаимодействия", [f"{item['title']}: {item['text']}{ref(item['source'])}"
                              for item in therapy.get("interactions", [])])
    section("Предупреждения", [f"{w['text']} [{w['source']}]" for w in solution.get("warnings") or []])
    questions = []
    for q in solution.get("questions") or []:
        questions.append(q["text"] + (f" ({'; '.join(q['ask'])})" if q.get("ask") else ""))
    section("Уточняющие вопросы", questions)
    for item in solution.get("advice") or []:
        section("Когда срочно обратиться к врачу" if lay else f"Когда срочно обратиться к врачу ({item['title']})",
                item["seek_help_when"])
    if show_trace and solution.get("explanation"):
        add("Ход вывода:")
        out.extend("  " + line for line in solution["explanation"].splitlines())
    for text in solution.get("disclaimer") or []:
        if text != outcome.get("next_step"):
            add(f"! {text}")
    stats = solution.get("stats") or {}
    if stats and not lay:
        add(f"Итераций: {stats.get('iterations', '-')}, сработало правил: {stats.get('rules_fired', '-')} из "
            f"{stats.get('rules_total', '-')}, время решения: {stats.get('time_ms')} мс")
    return "\n".join(out)

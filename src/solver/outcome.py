"""Итог оценки для интерфейсов. Внутренний статус описывает наличие вывода,
даже если этот вывод сам по себе не позволяет определить нужный вид помощи.
"""

from __future__ import annotations

from typing import Any


def summarize_outcome(solution: dict[str, Any], emergency_message: str = "") -> dict[str, Any]:
    """Сформировать видимый итог, границы оценки и следующий шаг."""
    status = solution["status"]
    patient = solution.get("role") == "patient"
    if status == "invalid":
        return {"kind": "invalid", "title": "Проверьте данные", "summary": "",
                "next_step": "Исправьте отмеченные поля и запустите оценку снова."}
    if status == "refused":
        return {"kind": "refused", "title": "Случай вне области применения программы",
                "summary": solution["refusal"]["text"],
                "next_step": "Для оценки этого случая обратитесь к медицинскому специалисту." if patient
                else "Оцените случай вне MedAssist по применимым клиническим рекомендациям."}

    urgency = solution["urgency"]
    routing = solution["routing"]
    emergency = urgency["level"] == "emergency"
    safety_pending = any(q["kind"] == "safety_check" for q in solution["questions"])
    provisional = not emergency and (routing["provisional"] or safety_pending)
    urgency_label = urgency["label"] if urgency["reasons"] else None
    result = {"urgency": urgency_label, "provisional": provisional}

    if emergency:
        return {**result, "kind": "emergency", "title": "Нужна экстренная помощь",
                "summary": "По введённым данным сработали критерии экстренной оценки.",
                "next_step": emergency_message or "Немедленно обратитесь за экстренной медицинской помощью."}

    if routing["route"] or urgency_label:
        if provisional:
            summary = "Для проверки более срочного варианта ещё нужны сведения."
        elif routing["route"]:
            summary = "Маршрут выбран по введённым данным."
        else:
            summary = "Срочность определена. Конкретный маршрут и срок программа пока не определила."
        if routing["route"] and patient and provisional:
            next_step = "Если жалобы усиливаются, обратитесь за медицинской помощью."
        elif routing["route"]:
            next_step = ("Уточните порядок обращения у медицинского специалиста, если срок не указан."
                         if patient and not routing["timeframe"] else "")
        elif urgency["level"] == "urgent":
            next_step = "Обратитесь за медицинской помощью срочно." if patient else "Организуйте срочную клиническую оценку."
        else:
            next_step = "Уточните вид и срок помощи у медицинского специалиста." if patient else "Уточните маршрут при клинической оценке."
        return {**result, "kind": "preliminary" if provisional else "assessed",
                "title": "Предварительная оценка" if provisional else "Итог оценки",
                "summary": summary, "next_step": next_step}

    if patient:
        summary = ("Для проверки тревожных признаков ещё нужны данные." if provisional
                   else "Введённых сведений недостаточно для выбора вида и срока помощи.")
        return {**result, "kind": "incomplete", "title": "Срочность и маршрут пока не определены",
                "summary": summary,
                "next_step": "Если жалобы сохраняются или усиливаются, обратитесь за медицинской помощью."}

    if solution["working_diagnoses"]:
        summary = "В разборе есть рабочие диагнозы. Срок и маршрут по этим данным пока не определены."
    elif solution["hypotheses"]:
        summary = "Получены диагностические гипотезы. Данных для рабочего диагноза и маршрута пока недостаточно."
    else:
        summary = "По введённым данным программа пока не определила срочность и маршрут."
    if provisional:
        summary += " Для проверки опасных состояний ещё нужны данные."
    return {**result, "kind": "incomplete", "title": "Оценка по имеющимся данным", "summary": summary,
            "next_step": "Проверьте доступные уточнения и используйте клиническую оценку для выбора дальнейших действий."}

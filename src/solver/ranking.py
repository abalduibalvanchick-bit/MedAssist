"""Ранжирование уже выдвинутых гипотез по проявлениям из карточки заболевания."""

from .knowledge import KnowledgeBase
from .engine import Conclusions, URGENCY_ORDER, record_step


def rank_hypotheses(memory: Conclusions, kb: KnowledgeBase) -> list[dict]:
    coefficients = kb.schema.solver_setting("presentation_weights", {})
    leading_weight = max((h.score for h in memory.hypotheses.values()), default=0)
    ranked = []
    for hypothesis in memory.hypotheses.values():
        card = kb.get(hypothesis.target)
        arguments = []
        for item in card.metadata.get("presentation", []):
            symptom = item["symptom"]
            if symptom in memory.facts.symptoms:
                direction = "support"
            elif symptom in memory.facts.denied_symptoms:
                direction = "oppose"
            else:
                continue
            # Одно проявление даёт один вклад, даже при нескольких его признаках.
            weight = coefficients.get(direction, {}).get(item["frequency"], 0)
            delta = item["weight"] * weight
            if delta:
                arguments.append({"symptom": symptom, "title": kb.title(symptom),
                                  "frequency": item["frequency"], "weight": item["weight"],
                                  "contribution": delta if direction == "support" else -delta})
        total = hypothesis.score + sum(a["contribution"] for a in arguments)
        priority = bool(card.metadata.get("time_critical") and hypothesis.score == leading_weight)
        ranked.append({"id": card.id, "title": card.title, "score": hypothesis.score,
                       "rank_score": total, "time_critical_priority": priority, "sources": hypothesis.sources, "arguments": arguments})
        record_step(memory, "ranking", card.id, card.title,
                    [f"Вес правил: {hypothesis.score}", *(f"{a['title']}: {a['contribution']:+g}" for a in arguments)],
                    [f"Оценка гипотезы: {total:g}"], memory.iterations + 1)

    def order(item):
        urgency = kb.card_urgency(item["id"])
        priority = URGENCY_ORDER.index(urgency) if urgency in URGENCY_ORDER else 0
        return not item["time_critical_priority"], -item["rank_score"], -priority, item["id"]

    return sorted(ranked, key=order)

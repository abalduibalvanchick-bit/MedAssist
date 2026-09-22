"""Формирование объяснений.

justify() возвращает минимальное обоснование истинного условия: какие именно
сообщённые факты сделали его истинным. Для any берётся первая истинная
ветвь, для all — все ветви, для at_least — истинные альтернативы. Атомы
описываются с фактическими значениями пациента («САД = 190 (≥ 180)»).

render_explanation() строит текст объяснения по трассе вывода.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..conditions import PatientFacts, Truth, evaluate

if TYPE_CHECKING:  # pragma: no cover
    from .engine import Conclusions
    from .knowledge import KnowledgeBase

_OPS = {">": ">", ">=": "≥", "<": "<", "<=": "≤", "==": "=", "!=": "≠"}


def describe_atom(node: dict[str, Any], facts: PatientFacts, kb: "KnowledgeBase") -> str:
    schema = kb.schema
    for atom in schema.condition_atoms:
        if atom in node:
            value = node[atom]
            break
    else:
        return str(node)
    if atom == "param":
        label = kb.label("param", value)
        actual = facts.params.get(value, "нет данных")
        if schema.parameters.get(value, {}).get("type") == "boolean":
            return f"{label}: {'да' if actual is True else 'нет' if actual is False else actual}"
        op = node.get("op", "==")
        target = node.get("value")
        cond = f"{target[0]}–{target[1]}" if op == "between" else f"{_OPS.get(op, op)} {target}"
        return f"{label} = {actual} ({cond})"
    if atom == "fact":
        return kb.label("fact", value)
    if atom == "feature":
        return kb.label("feature", value)
    if atom == "known":
        kind = "param" if value in schema.parameters else "fact"
        return f"сообщено: {kb.label(kind, value)}"
    if atom == "scale":
        actual = facts.scales.get(value, "не вычислена")
        return f"{kb.title(value)} = {actual} ({_OPS.get(node['op'], node['op'])} {node['value']})"
    if atom == "scale_category":
        return f"{kb.title(value)}: категория {facts.scale_categories.get(value, '?')}"
    if atom == "exam_result":
        return f"{kb.title(value)}: {facts.exam_results.get(value, '?')}"
    prefix = {"symptom": "симптом", "disease": "диагноз", "redflag": "красный флаг",
              "emergency": "неотложное состояние", "profile": "профиль"}.get(atom, atom)
    return f"{prefix}: {kb.title(value)}"


def justify(node: Any, facts: PatientFacts, kb: "KnowledgeBase") -> list[str]:
    """Минимальный набор описаний фактов, делающих условие истинным."""
    schema = kb.schema
    if not isinstance(node, dict):
        return []
    if "all" in node:
        return [line for child in node["all"] for line in justify(child, facts, kb)]
    if "any" in node:
        for child in node["any"]:
            if evaluate(child, facts, schema) is Truth.TRUE:
                return justify(child, facts, kb)
        return []
    if "at_least" in node:
        return [line for child in node["at_least"]["of"]
                if evaluate(child, facts, schema) is Truth.TRUE
                for line in justify(child, facts, kb)]
    if "not" in node:
        inner = node["not"]
        if isinstance(inner, dict) and "known" in inner:
            kind = "param" if inner["known"] in schema.parameters else "fact"
            return [f"не сообщено: {kb.label(kind, inner['known'])}"]
        parts = justify_false(inner, facts, kb)
        return [f"нет: {p}" for p in parts] or ["условие-исключение не выполнено"]
    return [describe_atom(node, facts, kb)]


def justify_false(node: Any, facts: PatientFacts, kb: "KnowledgeBase") -> list[str]:
    """Описание фактов, делающих условие ложным (для ветви not)."""
    schema = kb.schema
    if not isinstance(node, dict):
        return []
    if "any" in node:
        return [line for child in node["any"] for line in justify_false(child, facts, kb)]
    if "all" in node:
        for child in node["all"]:
            if evaluate(child, facts, schema) is Truth.FALSE:
                return justify_false(child, facts, kb)
        return []
    if "not" in node:
        return justify(node["not"], facts, kb)
    if "at_least" in node:
        return [line for child in node["at_least"]["of"] for line in justify_false(child, facts, kb)]
    return [describe_atom(node, facts, kb)]


_KIND_TITLES = {"profile": "Профиль", "scale": "Шкала", "redflag": "Красный флаг",
                "emergency": "Неотложное состояние", "rule": "Правило"}


def render_explanation(memory: "Conclusions", kb: "KnowledgeBase") -> str:
    """Текстовое объяснение хода вывода по трассе."""
    lines: list[str] = []
    for step in memory.trace:
        head = f"{step.step}. {_KIND_TITLES.get(step.kind, step.kind)} {step.source_id} «{step.title}»"
        lines.append(head)
        if step.because:
            lines.append("   основание: " + "; ".join(step.because))
        if step.effects:
            lines.append("   вывод: " + "; ".join(step.effects))
    if not lines:
        lines.append("Ни одно правило и ни одно условие карточек не выполнено для сообщённых данных.")
    return "\n".join(lines)

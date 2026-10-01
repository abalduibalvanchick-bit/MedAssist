"""Фармакологические знания, вычисляемые из базы знаний.

Препарат наследует противопоказания своих фармакологических групп (связь
included_in → drugclass). В карточке препарата хранятся только собственные
противопоказания; полный действующий набор возвращает effective_contraindications.
Так одно и то же противопоказание хранится в базе знаний ровно один раз.
"""

from __future__ import annotations

import json
from typing import Any, Iterable

from .models import KnowledgeCard


def _canonical(node: Any) -> Any:
    """Каноническая форма условия: порядок ветвей all/any/at_least не важен."""
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k in ("all", "any") and isinstance(v, list):
                out[k] = sorted((_canonical(x) for x in v), key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
            elif k == "at_least" and isinstance(v, dict):
                out[k] = {"n": v.get("n"), "of": sorted((_canonical(x) for x in v.get("of") or []),
                                                        key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))}
            else:
                out[k] = _canonical(v)
        return out
    if isinstance(node, list):
        return [_canonical(x) for x in node]
    return node


def _key(condition: Any) -> str:
    return json.dumps(_canonical(condition), sort_keys=True, ensure_ascii=False)


def drug_classes(drug: KnowledgeCard, cards: dict[str, KnowledgeCard]) -> list[KnowledgeCard]:
    """Фармакологические группы, к которым относится препарат."""
    result = []
    for relation in drug.relations:
        target = cards.get(str(relation.get("target", "")))
        if relation.get("type") == "included_in" and target is not None and target.category == "drugclass":
            result.append(target)
    return result


def effective_contraindications(drug: KnowledgeCard, cards: dict[str, KnowledgeCard]) -> list[dict[str, Any]]:
    """Собственные противопоказания препарата и унаследованные от групп, без повторов.

    У каждого элемента есть поле source — ID карточки, где противопоказание задано.
    Если условие задано и у препарата, и у группы, действует запись препарата
    (она уточняет групповую, например делает противопоказание абсолютным).
    """
    seen: set[str] = set()
    result: list[dict[str, Any]] = []

    def add(items: Iterable[dict[str, Any]], source: str) -> None:
        for item in items or []:
            if not isinstance(item, dict) or "when" not in item:
                continue
            key = _key(item["when"])
            if key in seen:
                continue
            seen.add(key)
            result.append({**item, "source": source})

    add(drug.metadata.get("contraindications") or [], drug.id)
    for cls in drug_classes(drug, cards):
        # Противопоказание группы может не распространяться на отдельных
        # представителей (поле not_for), например на дигидропиридиновые БКК.
        add([i for i in cls.metadata.get("contraindications") or []
             if drug.id not in (i.get("not_for") or [])], cls.id)
    return result


def duplicated_class_contraindications(drug: KnowledgeCard, cards: dict[str, KnowledgeCard]) -> list[tuple[str, str]]:
    """Противопоказания препарата, дословно повторяющие противопоказания его группы.

    Повтором считается совпадение и условия, и абсолютности. Если у препарата
    противопоказание строже, чем у группы (абсолютное вместо относительного),
    это уточнение, а не повтор: при наследовании побеждает запись препарата.
    """
    inherited: dict[tuple[str, bool], str] = {}
    for cls in drug_classes(drug, cards):
        for item in cls.metadata.get("contraindications") or []:
            if isinstance(item, dict) and "when" in item:
                inherited[(_key(item["when"]), bool(item.get("absolute")))] = cls.id
    duplicates = []
    for item in drug.metadata.get("contraindications") or []:
        if isinstance(item, dict) and "when" in item:
            key = (_key(item["when"]), bool(item.get("absolute")))
            if key in inherited:
                duplicates.append((str(item.get("explanation", "")), inherited[key]))
    return duplicates

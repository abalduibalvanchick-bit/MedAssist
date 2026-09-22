"""Доступ решателя к базе знаний.

Решатель не содержит медицинских фактов: всё, что он знает о предметной
области, он получает через этот модуль из карточек kb/ и правил kb/rules/.
Замена или расширение базы знаний не требует изменения кода решателя.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..models import KnowledgeCard
from ..repository import KnowledgeRepository
from ..schema import Schema, load_schema, find_project_root


@dataclass(frozen=True)
class Rule:
    """Продукционное правило из kb/rules/*.yaml."""

    id: str
    domain: str
    title: str
    condition: dict[str, Any]
    actions: tuple[dict[str, Any], ...]
    source_cards: tuple[str, ...]
    explanation: str
    priority: int
    source_file: str


@dataclass
class KnowledgeBase:
    """Загруженная база знаний с индексами, нужными решателю."""

    schema: Schema
    cards: dict[str, KnowledgeCard]
    rules: list[Rule]
    root: Path
    by_category: dict[str, list[KnowledgeCard]] = field(default_factory=dict)
    feature_owner: dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------ загрузка
    @classmethod
    def load(cls, kb_root: Path | str | None = None) -> "KnowledgeBase":
        root = Path(kb_root) if kb_root else find_project_root() / "kb"
        schema = load_schema(root / "_schema" / "schema.yaml")
        repo = KnowledgeRepository(root).load()
        cards = {c.id: c for c in repo.cards if c.id}
        kb = cls(schema=schema, cards=cards, rules=cls._load_rules(root / "rules", schema), root=root)
        for card in sorted(cards.values(), key=lambda c: c.id):
            kb.by_category.setdefault(card.category, []).append(card)
        for symptom in kb.by_category.get("symptom", []):
            for feature in symptom.metadata.get("features") or []:
                if isinstance(feature, dict) and feature.get("code"):
                    kb.feature_owner[str(feature["code"])] = symptom.id
        return kb

    @staticmethod
    def _load_rules(rules_root: Path, schema: Schema) -> list[Rule]:
        rules: list[Rule] = []
        default_priority = int(schema.raw.get("rules", {}).get("default_priority", 50))
        for path in sorted(rules_root.glob("*.yaml")):
            for raw in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
                rules.append(Rule(
                    id=str(raw["id"]),
                    domain=str(raw["domain"]),
                    title=str(raw["title"]),
                    condition=raw["if"],
                    actions=tuple(raw.get("then") or []),
                    source_cards=tuple(raw.get("source_cards") or []),
                    explanation=str(raw.get("explanation", "")),
                    priority=int(raw.get("priority", default_priority)),
                    source_file=path.name,
                ))
        # Детерминированный порядок: сначала более приоритетные, затем по ID.
        rules.sort(key=lambda r: (-r.priority, r.id))
        return rules

    # ------------------------------------------------------------------ выборки
    def category(self, name: str) -> list[KnowledgeCard]:
        return self.by_category.get(name, [])

    def get(self, card_id: str) -> KnowledgeCard | None:
        return self.cards.get(card_id)

    def title(self, card_id: str) -> str:
        card = self.cards.get(card_id)
        return card.title if card else card_id

    def label(self, kind: str, code: str) -> str:
        """Человекочитаемая подпись параметра, факта, признака или карточки."""
        if kind == "param":
            spec = self.schema.parameters.get(code, {})
            unit = f", {spec['unit']}" if spec.get("unit") else ""
            return f"{spec.get('label', code)}{unit}"
        if kind == "fact":
            return self.schema.facts.get(code, {}).get("label", code)
        if kind == "feature":
            owner = self.cards.get(self.feature_owner.get(code, ""))
            for feature in (owner.metadata.get("features") or []) if owner else []:
                if feature.get("code") == code:
                    return f"{owner.title.lower()}: {feature.get('label', code)}"
            return code
        return self.title(code)

    def labels(self) -> dict[str, str]:
        return {cid: card.title for cid, card in self.cards.items()}

    def card_urgency(self, card_id: str) -> str:
        card = self.cards.get(card_id)
        return card.urgency if card else "routine"


@lru_cache(maxsize=4)
def load_default_kb(kb_root: str | None = None) -> KnowledgeBase:
    """Кэшированная загрузка: база знаний читается один раз за процесс."""
    return KnowledgeBase.load(kb_root)

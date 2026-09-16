"""Построение индексов по карточкам базы знаний."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .models import KnowledgeCard, normalize_text


@dataclass
class KnowledgeIndex:
    """Набор быстрых индексов для поиска и навигации."""

    by_id: dict[str, KnowledgeCard] = field(default_factory=dict)
    by_domain: dict[str, list[KnowledgeCard]] = field(default_factory=lambda: defaultdict(list))
    by_category: dict[str, list[KnowledgeCard]] = field(default_factory=lambda: defaultdict(list))
    by_tag: dict[str, list[KnowledgeCard]] = field(default_factory=lambda: defaultdict(list))
    by_urgency: dict[str, list[KnowledgeCard]] = field(default_factory=lambda: defaultdict(list))
    duplicates: dict[str, list[KnowledgeCard]] = field(default_factory=dict)
    # Входящие связи: target_id -> [(source_id, relation_type)]
    inbound: dict[str, list[tuple[str, str]]] = field(default_factory=lambda: defaultdict(list))


def build_index(cards: list[KnowledgeCard]) -> KnowledgeIndex:
    """Строит индексы по id, домену, категории, тегам и срочности."""

    index = KnowledgeIndex()
    id_occurrences: dict[str, list[KnowledgeCard]] = defaultdict(list)

    for card in cards:
        if card.id:
            id_occurrences[card.id].append(card)
            # Для удобства работы сохраняем первый встретившийся документ.
            index.by_id.setdefault(card.id, card)

        if card.domain:
            index.by_domain[normalize_text(card.domain)].append(card)
        if card.category:
            index.by_category[normalize_text(card.category)].append(card)
        if card.urgency:
            index.by_urgency[normalize_text(card.urgency)].append(card)

        for tag in card.tags:
            index.by_tag[normalize_text(tag)].append(card)

        seen_targets: set[str] = set()
        for relation in card.relations:
            target = str(relation.get("target", "")).strip()
            rel_type = str(relation.get("type", "")).strip() or "related_to"
            if target and card.id:
                index.inbound[target].append((card.id, rel_type))
                seen_targets.add(target)
        # Схема v1: плоский список related тоже считается входящей связью.
        if card.schema_version < 2 and card.id:
            for target in card.related:
                if target not in seen_targets:
                    index.inbound[target].append((card.id, "related"))

    index.duplicates = {
        card_id: repeated_cards
        for card_id, repeated_cards in id_occurrences.items()
        if len(repeated_cards) > 1
    }
    return index

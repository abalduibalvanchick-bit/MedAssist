"""Модуль работы со связями между карточками."""

from __future__ import annotations

from .models import RelatedCard
from .repository import KnowledgeRepository
from .schema import load_schema


class Linker:
    """Разрешает связи related и relations между документами."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository
        self.schema = load_schema()

    def get_related_cards(self, card_id: str) -> list[RelatedCard]:
        """Возвращает документы, на которые ссылается карточка."""

        source = self.repository.get_by_id(card_id)
        if source is None:
            return []

        related: list[RelatedCard] = []
        seen: set[tuple[str, str]] = set()

        # Схема v1: плоский список related. В схеме v2 он вычисляется из relations,
        # поэтому отдельно не разворачивается.
        legacy_related = source.related if source.schema_version < 2 else []
        for target_id in legacy_related:
            key = (target_id, "related")
            if key not in seen:
                related.append(
                    RelatedCard(
                        source_id=source.id,
                        target_id=target_id,
                        relation_type="related",
                        description="Связанный документ из поля related",
                        card=self.repository.get_by_id(target_id),
                    )
                )
                seen.add(key)

        for relation in source.relations:
            target_id = str(relation.get("target", "")).strip()
            relation_type = str(relation.get("type", "related_to")).strip() or "related_to"
            description = str(relation.get("description", "")).strip()
            if not target_id:
                continue
            key = (target_id, relation_type)
            if key not in seen:
                related.append(
                    RelatedCard(
                        source_id=source.id,
                        target_id=target_id,
                        relation_type=relation_type,
                        description=description,
                        card=self.repository.get_by_id(target_id),
                    )
                )
                seen.add(key)

        return related

    def get_inverse_cards(self, card_id: str) -> list[RelatedCard]:
        """Возвращает связи, материализованные из входящих (обратный тип по схеме).

        Автор карточки пишет связь в одном направлении; обратная выводится из
        schema.yaml (relation_types.*.inverse). Для v1-типов используется
        legacy-алиас, если он объявлен.
        """
        source = self.repository.get_by_id(card_id)
        if source is None:
            return []
        outgoing = {(str(r.get("target", "")).strip(), self.schema.normalize_relation_type(str(r.get("type", ""))))
                    for r in source.relations}
        result: list[RelatedCard] = []
        for origin_id, rel_type in self.repository.index.inbound.get(card_id, []):
            canonical = self.schema.normalize_relation_type(rel_type)
            inverse = self.schema.inverse_relation(canonical) or f"inverse_of({canonical})"
            if (origin_id, inverse) in outgoing:
                continue  # автор уже записал обратную связь явно
            result.append(RelatedCard(
                source_id=card_id,
                target_id=origin_id,
                relation_type=inverse,
                description=f"Обратная связь к {canonical} из {origin_id}",
                card=self.repository.get_by_id(origin_id),
            ))
        return result

    def get_all_links(self, card_id: str) -> list[RelatedCard]:
        """Исходящие связи плюс материализованные обратные."""
        return self.get_related_cards(card_id) + self.get_inverse_cards(card_id)

    def get_backlinks(self, target_id: str) -> list[RelatedCard]:
        """Показывает, какие карточки ссылаются на заданный документ."""

        backlinks: list[RelatedCard] = []
        for card in self.repository.all_cards():
            if card.id == target_id:
                continue
            for related in self.get_related_cards(card.id):
                if related.target_id == target_id:
                    backlinks.append(related)
        return backlinks

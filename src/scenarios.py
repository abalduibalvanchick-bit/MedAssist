"""Демонстрационные сценарии MVP MedAssist."""

from __future__ import annotations

from .linker import Linker
from .repository import KnowledgeRepository
from .search_engine import SearchEngine
from .validator import KnowledgeBaseValidator


class ScenarioRunner:
    """Формирует текстовые демонстрации работы базы знаний."""

    TITLES = {
        "chest_pain": "Боль в груди",
        "headache": "Головная боль и высокое АД",
        "dyspnea": "Одышка",
        "hypertension_protocol": "Протокол ведения артериальной гипертензии",
        "hypertension_therapy": "Фармакотерапия артериальной гипертензии",
        "pharm_drug": "Просмотр лекарственного средства",
        "drug_interaction": "Лекарственное взаимодействие",
        "validation": "Проверка базы знаний",
    }

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository
        self.search_engine = SearchEngine(repository)
        self.linker = Linker(repository)
        self.validator = KnowledgeBaseValidator(repository)

    def run(self, name: str) -> str:
        scenarios = {
            "chest_pain": self.chest_pain,
            "headache": self.headache_hypertension,
            "dyspnea": self.dyspnea,
            "validation": self.validation,
            "hypertension_protocol": self.hypertension_protocol,
            "hypertension_therapy": self.hypertension_therapy,
            "pharm_drug": self.pharm_drug,
            "drug_interaction": self.drug_interaction,
            "all": self.all_scenarios,
        }
        scenario = scenarios.get(name)
        if scenario is None:
            return f"Неизвестный сценарий: {name}. Доступно: {', '.join(scenarios)}"
        return scenario()

    def chest_pain(self) -> str:
        return self._scenario_by_query(
            title="Сценарий: боль в груди",
            query="боль в груди",
            focus_id="DIAG-SYMPTOM-002",
        )

    def headache_hypertension(self) -> str:
        return self._scenario_by_query(
            title="Сценарий: головная боль и высокое АД",
            query="головная боль",
            focus_id="DIAG-SYMPTOM-001",
        )

    def dyspnea(self) -> str:
        return self._scenario_by_query(
            title="Сценарий: одышка",
            query="одышка",
            focus_id="DIAG-SYMPTOM-003",
        )

    def hypertension_protocol(self) -> str:
        return self._scenario_by_query(
            title="Сценарий: протокол ведения артериальной гипертензии",
            query="артериальная гипертензия протокол",
            focus_id="PROT-PROTOCOL-001",
        )

    def hypertension_therapy(self) -> str:
        return self._scenario_by_query(
            title="Сценарий: фармакотерапия артериальной гипертензии",
            query="схема лечения артериальной гипертензии",
            focus_id="PHARM-REGIMEN-001",
        )

    def pharm_drug(self) -> str:
        return self._scenario_by_query(
            title="Сценарий: просмотр лекарственного средства",
            query="эналаприл",
            focus_id="PHARM-DRUG-001",
        )

    def drug_interaction(self) -> str:
        return self._scenario_by_query(
            title="Сценарий: лекарственное взаимодействие",
            query="метформин контраст",
            focus_id="PHARM-INTERACTION-001",
        )

    def validation(self) -> str:
        report = self.validator.validate()
        return report.to_markdown()

    def all_scenarios(self) -> str:
        return "\n\n---\n\n".join([
            self.chest_pain(),
            self.headache_hypertension(),
            self.dyspnea(),
            self.hypertension_protocol(),
            self.hypertension_therapy(),
            self.pharm_drug(),
            self.drug_interaction(),
            self.validation(),
        ])

    def _scenario_by_query(self, title: str, query: str, focus_id: str) -> str:
        lines = [f"# {title}", ""]
        lines.append(f"Запрос пользователя: **{query}**")
        lines.append("")

        results = self.search_engine.search(query, limit=5)
        lines.append("## Результаты поиска")
        if not results:
            lines.append("Документы не найдены.")
            return "\n".join(lines)

        for result in results:
            lines.append(f"- {result.card.short_description}; score={result.score}; найдено по: {', '.join(result.matched_by)}")

        focus_card = self.repository.get_by_id(focus_id) or results[0].card
        lines.append("")
        lines.append("## Основная найденная карточка")
        lines.append(f"{focus_card.short_description}")
        lines.append("")
        lines.append("## Связанные документы")
        related = self.linker.get_related_cards(focus_card.id)
        if not related:
            lines.append("Связанные документы не указаны.")
        else:
            for item in related:
                if item.card is None:
                    lines.append(f"- {item.target_id} — связь битая ({item.relation_type})")
                else:
                    lines.append(f"- {item.card.short_description}; тип связи: {item.relation_type}")
        return "\n".join(lines)

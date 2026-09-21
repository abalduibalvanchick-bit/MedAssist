# Модули программной части

| Модуль | Назначение |
|---|---|
| `main.py` | точка запуска |
| `src/schema.py` | загрузка `kb/_schema/schema.yaml`, самопроверка схемы |
| `src/config.py` | пути и константы совместимости со схемой v1 |
| `src/conditions.py` | мини-язык условий: статическая проверка, трёхзначная оценка, трасса, описание |
| `src/models.py` | модель карточки `KnowledgeCard` |
| `src/markdown_parser.py` | разбор Markdown-файла и YAML-блока |
| `src/repository.py` | загрузка карточек из `kb/` |
| `src/indexer.py` | индексы по ID, домену, категории, тегам, срочности; входящие связи |
| `src/linker.py` | исходящие и материализованные обратные связи |
| `src/search_engine.py` | поиск по карточкам |
| `src/validator.py` | структурная и качественная проверка карточек и правил |
| `src/scenarios.py` | демонстрационные сценарии |
| `src/cli.py` | консольный интерфейс |

## Поток данных

```text
kb/_schema/schema.yaml ──► schema.py ──► conditions.py, validator.py, linker.py
kb/**/*.md ──► markdown_parser.py ──► KnowledgeCard ──► repository.py ──► indexer.py
                                                           │
                          search_engine.py / linker.py / validator.py / scenarios.py ──► cli.py
```

<!-- Сгенерировано scripts/generate_docs.py из kb/_schema/schema.yaml. Не редактировать вручную. -->

# Схема базы знаний MedAssist v2
Полное описание структуры базы знаний. Разделы «Метаданные», «Связи» и «Условия» продублированы в отдельных файлах `docs/metadata_schema.md`, `docs/link_types.md`, `docs/conditions.md`.

## Домены
| Код | Префикс ID | Папка | Название |
|---|---|---|---|
| `diag` | `DIAG` | `kb/diag/` | Заболевания, симптомы и диагностика |
| `pharm` | `PHARM` | `kb/pharm/` | Фармакология и терапия |
| `prot` | `PROT` | `kb/prot/` | Клинические протоколы и маршрутизация пациента |
| `glb` | `GLB` | `kb/glb/` | Глобальная предметная область |

## Машиночитаемый слой по категориям
Поля, которые решатель читает напрямую. `required_for_approved` — обязательны для `status: approved`.

### symptom — Симптом / синдром
Обязательны для approved: `features`, `synonyms`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `synonyms` | `list[string]` | да | Синонимы и разговорные формулировки для распознавания |
| `features` | `list[object]` | да | Контролируемые признаки симптома; на них ссылаются атомы feature |

Структура элемента `features`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `code` | `string` | да | Код вида <symptom>.<feature> |
| `label` | `string` | да |  |

### disease — Заболевание
Обязательны для approved: `presentation`, `exams`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `presentation` | `list[object]` | да | Клиническая картина в машиночитаемом виде |
| `red_flags` | `list[id(redflag)]` | нет |  |
| `exams` | `list[object]` | да |  |
| `differentials` | `list[id(disease,emergency)]` | нет |  |
| `applies_when` | `condition` | нет | Ограничение применимости карточки (возраст, профиль) |

Структура элемента `presentation`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `symptom` | `id(symptom)` | да |  |
| `weight` | `enum(weight)` | да | Диагностический вес: 3 — ключевой, 1 — второстепенный |
| `frequency` | `enum(frequency)` | да |  |
| `features` | `list[feature_code]` | нет | Характерные признаки симптома при этом заболевании |

Структура элемента `exams`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `exam` | `id(exam)` | да |  |
| `role` | `enum(exam_role)` | да |  |
| `expected` | `string` | нет | Ожидаемый результат (контролируемое значение или текст) |

### exam — Метод обследования
Обязательны для approved: `results`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `results` | `list[object]` | да | Контролируемые значения результата, на которые ссылается атом exam_result |
| `contraindications` | `list[condition]` | нет |  |
| `turnaround` | `string` | нет | Ориентировочное время получения результата |

Структура элемента `results`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `value` | `string` | да |  |
| `label` | `string` | да |  |
| `indicates` | `list[id(disease,emergency)]` | нет |  |

### difdiag — Дифференциальная диагностика
Обязательны для approved: `leading_symptom`, `branches`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `leading_symptom` | `id(symptom)` | да |  |
| `branches` | `list[object]` | да |  |

Структура элемента `branches`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `target` | `id(disease,emergency,redflag)` | да |  |
| `supporting` | `condition` | да | Признаки в пользу направления |
| `against` | `condition` | нет | Признаки против направления |
| `key_exam` | `id(exam)` | нет |  |
| `prior` | `enum(prior)` | да |  |
| `urgency` | `enum(urgency)` | да |  |

### redflag — Красный флаг
Обязательны для approved: `triggers`, `indicates`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `triggers` | `condition` | да | Формальное условие срабатывания |
| `indicates` | `list[id(emergency,disease)]` | да | На какие состояния указывает |
| `action` | `id(emergency_p,routing)` | нет | Куда передать управление |

### emergency — Неотложное состояние (диагностика)
Обязательны для approved: `criteria`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `criteria` | `condition` | да | Критерии распознавания |
| `emergency_protocol` | `id(emergency_p)` | нет |  |
| `time_critical` | `boolean` | нет |  |

### drug — Лекарственное средство
Обязательны для approved: `contraindications`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `contraindications` | `list[object]` | да |  |
| `interactions` | `list[object]` | нет |  |
| `dose_adjustments` | `list[object]` | нет |  |
| `indications` | `list[id(disease,emergency,symptom)]` | нет |  |

Структура элемента `contraindications`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `when` | `condition` | да |  |
| `absolute` | `boolean` | да |  |
| `explanation` | `string` | да |  |

Структура элемента `interactions`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `with` | `id(drug,drugclass)` | нет |  |
| `severity` | `enum(interaction_severity)` | да |  |
| `card` | `id(interaction)` | нет |  |

Структура элемента `dose_adjustments`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `when` | `condition` | да |  |
| `note` | `string` | да |  |

### drugclass — Фармакологическая группа
Обязательны для approved: `representatives`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `representatives` | `list[string]` | да | МНН основных представителей группы |
| `members` | `list[id(drug)]` | нет | Представители, для которых есть карточки |
| `contraindications` | `list[object]` | нет |  |

Структура элемента `contraindications`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `when` | `condition` | да |  |
| `absolute` | `boolean` | да |  |
| `explanation` | `string` | да |  |

### interaction — Лекарственное взаимодействие
Обязательны для approved: `between`, `severity`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `between` | `list[id(drug,drugclass)]` | да | Участники из базы знаний (один или два) |
| `other_agent` | `string` | нет | Второй участник, не представленный карточкой (например, контрастное вещество) |
| `severity` | `enum(interaction_severity)` | да |  |
| `trigger` | `condition` | нет | Условие, при котором взаимодействие актуально для пациента |
| `management` | `string` | нет |  |

### adr — Нежелательная лекарственная реакция
Обязательны для approved: `caused_by`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `caused_by` | `list[id(drug,drugclass)]` | да |  |
| `risk_factors` | `list[condition]` | нет |  |

### regimen — Терапевтическая схема
Обязательны для approved: `for`, `lines`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `for` | `list[id(disease,emergency)]` | да |  |
| `lines` | `list[object]` | да |  |

Структура элемента `lines`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `line` | `number` | да |  |
| `options` | `list[object]` | да |  |

### dosing — Коррекция доз
Обязательны для approved: `rules`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `rules` | `list[object]` | да |  |

Структура элемента `rules`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `agent` | `id(drug,drugclass)` | да |  |
| `when` | `condition` | да |  |
| `adjustment` | `string` | да |  |

### nonpharm — Нефармакологический метод
Обязательны для approved: `for`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `for` | `list[id(disease,emergency,symptom)]` | да |  |
| `contraindications` | `list[condition]` | нет |  |

### protocol — Клинический протокол
Обязательны для approved: `for`, `entry`, `steps`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `for` | `list[id(disease,emergency)]` | да |  |
| `entry` | `condition` | да | Критерии начала применения протокола |
| `steps` | `list[object]` | да |  |
| `branches` | `list[object]` | нет |  |
| `targets` | `list[object]` | нет |  |

Структура элемента `steps`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `id` | `string` | да |  |
| `action` | `string` | да |  |
| `when` | `condition` | нет |  |
| `refs` | `list[id]` | нет |  |

Структура элемента `branches`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `when` | `condition` | да |  |
| `then` | `id(routing,emergency_p,protocol,regimen,follow_up)` | да |  |
| `explanation` | `string` | да |  |

Структура элемента `targets`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `param` | `parameter` | да |  |
| `op` | `operator` | да |  |
| `value` | `number` | да |  |
| `label` | `string` | да |  |

### emergency_p — Алгоритм неотложной помощи
Обязательны для approved: `criteria`, `phases`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `criteria` | `condition` | да |  |
| `phases` | `list[object]` | да |  |
| `drugs` | `list[object]` | нет |  |
| `stabilization` | `condition` | нет |  |
| `next` | `id(routing)` | нет |  |

Структура элемента `phases`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `window` | `string` | да | Например '0–10 мин' |
| `steps` | `list[string]` | да |  |

Структура элемента `drugs`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `drug` | `id(drug,drugclass)` | да |  |
| `dose` | `string` | да |  |
| `route` | `string` | да |  |
| `when` | `condition` | нет |  |
| `contraindicated_when` | `condition` | нет |  |

### routing — Маршрутизация пациента
Обязательны для approved: `decisions`, `default`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `for` | `list[id(disease,emergency,symptom)]` | да |  |
| `decisions` | `list[object]` | да | Оцениваются по порядку; срабатывает первое истинное условие |
| `default` | `object` | да |  |

Структура элемента `decisions`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `when` | `condition` | да |  |
| `route` | `enum(route)` | да |  |
| `timeframe` | `string` | нет |  |
| `actions` | `list[string]` | да |  |
| `next` | `list[id(protocol,emergency_p,follow_up,routing)]` | нет |  |
| `explanation` | `string` | да |  |

Структура элемента `default`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `route` | `enum(route)` | да |  |
| `actions` | `list[string]` | да |  |
| `explanation` | `string` | да |  |

### scale — Клиническая шкала
Обязательны для approved: `parameters`, `interpretation`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `parameters` | `list[object]` | да |  |
| `interpretation` | `list[object]` | да | Диапазоны включительно; должны покрывать все достижимые суммы без пересечений |
| `missing_policy` | `string` | да | Что делать при отсутствии данных по параметру |

Структура элемента `parameters`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `code` | `string` | да |  |
| `label` | `string` | да |  |
| `options` | `list[object]` | нет | Варианты значения; баллы берутся из первого варианта с истинным условием |
| `points_from` | `parameter` | нет | Баллы равны значению числового параметра (ответ на вопрос опросника) |

Структура элемента `interpretation`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `min` | `number` | да |  |
| `max` | `number` | да | null означает 'и выше' |
| `category` | `string` | да |  |
| `label` | `string` | да |  |
| `action` | `id(routing,protocol,emergency_p,follow_up)` | нет |  |

### screening — Скрининг
Обязательны для approved: `target`, `interval`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `target` | `condition` | да | Кому показан скрининг |
| `methods` | `list[id(exam)]` | нет | Методы обследования; для программ вакцинации может отсутствовать |
| `interval` | `string` | да |  |
| `positive_when` | `condition` | нет |  |
| `on_positive` | `id(routing,protocol)` | нет |  |

### patient_info — Памятка для пациента
Обязательны для approved: `for`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `for` | `list[id(disease,emergency,protocol,drug)]` | да |  |
| `seek_help_when` | `list[string]` | нет |  |

### checklist — Чек-лист врача
Обязательны для approved: `items`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `items` | `list[object]` | да |  |

Структура элемента `items`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `text` | `string` | да |  |
| `required` | `boolean` | да |  |
| `refs` | `list[id]` | нет |  |

### follow_up — Наблюдение пациента
Обязательны для approved: `for`, `schedule`, `monitor`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `for` | `list[id(disease,protocol)]` | да |  |
| `schedule` | `list[object]` | да |  |
| `monitor` | `list[object]` | да |  |
| `deterioration` | `condition` | нет |  |
| `on_deterioration` | `id(routing,emergency_p)` | нет |  |

Структура элемента `schedule`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `after` | `string` | да |  |
| `interval` | `string` | да |  |
| `purpose` | `string` | да |  |

Структура элемента `monitor`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `param` | `parameter` | нет |  |
| `exam` | `id(exam)` | нет |  |
| `target` | `condition` | нет |  |
| `label` | `string` | да |  |

### vaccine — Вакцина
Обязательны для approved: `indications`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `indications` | `condition` | да |  |
| `contraindications` | `list[condition]` | нет |  |
| `schedule` | `string` | нет |  |

### glossary — Глоссарная статья
Обязательны для approved: `term`, `definition`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `term` | `string` | да |  |
| `definition` | `string` | да |  |
| `synonyms` | `list[string]` | нет |  |
| `refers_to` | `list[id]` | нет |  |

### profile — Профиль группы пациентов
Обязательны для approved: `criteria`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `criteria` | `condition` | да | Формальное определение принадлежности к профилю |
| `considerations` | `list[string]` | нет |  |

### disclaimer — Дисклеймер
Обязательны для approved: `text`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `text` | `string` | да |  |
| `applies_to_access_level` | `list[enum(access_level)]` | нет |  |

### lab — Лабораторный показатель
Обязательны для approved: `parameter`, `reference_range`

| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| `parameter` | `parameter` | да |  |
| `reference_range` | `object` | да |  |

Структура элемента `reference_range`:

| Ключ | Тип | Обяз. | Описание |
|---|---|---|---|
| `min` | `number` | да |  |
| `max` | `number` | да |  |

### imaging — Инструментальный метод (справочник)
Машиночитаемый слой не требуется.

### anatomy — Анатомо-физиологический раздел
Машиночитаемый слой не требуется.

### cross — Межпредметный документ
Машиночитаемый слой не требуется.

## Правила (kb/rules/*.yaml)
Обязательные поля: `id`, `domain`, `title`, `if`, `then`, `source_cards`, `explanation`.
Необязательные: `priority`, `evidence_level`, `status`, `tags`, `notes`.

| Действие | Цель / значение | Доп. параметры | Описание |
|---|---|---|---|
| `assert_hypothesis` | `id(disease,emergency)` | `weight` |  |
| `trigger_red_flag` | `id(redflag)` |  |  |
| `set_urgency` | `enum(urgency)` |  |  |
| `recommend_exam` | `id(exam)` | `role` |  |
| `route` | `enum(route)` | `timeframe` |  |
| `apply_protocol` | `id(protocol,emergency_p)` |  |  |
| `request_clarification` | `string` |  | Какие данные запросить у пользователя |
| `refuse` | `string` |  | Отказ с объяснением границы применимости |

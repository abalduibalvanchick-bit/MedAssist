---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: scale — Клиническая шкала. Файл: kb/prot/scales/prot_scale_<краткое_имя>.md
id: PROT-SCALE-NNN
schema_version: 2
title: <Название>
domain: prot
category: scale
body_system: [cardiovascular]  # cardiovascular | respiratory | gastrointestinal | nervous | endocrine | metabolic | urinary | musculoskeletal | immune | reproductive | hematologic | dermatologic | multisystem
tags: [<тег>]
urgency: routine  # routine | urgent | emergency | elective
access_level: professional  # professional | nursing | student | patient
target_specialist: [therapist]  # см. docs/metadata_schema.md, перечисление target_specialist
age_group: [adult]  # neonate | infant | child | adolescent | adult | elderly | all_ages
# evidence_level: Ia  # необязательно: Ia | Ib | IIa | IIb | III | IV
# recommendation_class: I  # необязательно: I | IIa | IIb | III
relations:
  - target: DIAG-DISEASE-001
    type: assesses  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «scale»):
parameters: [{"code": "<текст>", "label": "<текст>", "options": [{"when": {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}, "points": 0, "label": "<текст>"}], "points_from": "sbp"}]  # list[object]; обязательно для approved
interpretation: [{"min": 0, "max": 0, "category": "<текст>", "label": "<текст>", "action": "PROT-ROUTING-001"}]  # list[object]; обязательно для approved; Диапазоны включительно; должны покрывать все достижимые суммы без пересечений
missing_policy: "<текст>"  # string; рекомендуется; Что делать при отсутствии данных по параметру
sources:
  - <Автор(ы). Название. Издание/журнал. Год;том:страницы.>
  - <Вторая конкретная библиографическая ссылка>
clinical_guidelines: [<Краткое название КР, год>]
last_medical_review: YYYY-MM-DD
medical_reviewer: модельная верификация (учебный проект)
author: <Инженер знаний №N>
version: '2.0'
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
status: draft  # draft | medical_review | approved | deprecated; approved — только при заполненном машиночитаемом слое
disclaimer: true
---

# <Название>

> ⚕️ **Дисклеймер**: Информация носит справочный характер и не заменяет консультацию специалиста.

## Назначение шкалы
<заполнить>

## Область применения
<заполнить>

## Параметры оценки
<заполнить>

## Правила расчёта
<заполнить>

## Интерпретация результата
<заполнить>

## Тактическая значимость
<заполнить>

## Ограничения
<заполнить>

## Особенности применения
<заполнить>

## Связанные документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

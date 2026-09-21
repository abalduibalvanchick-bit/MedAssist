---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: regimen — Терапевтическая схема. Файл: kb/pharm/regimens/pharm_regimen_<краткое_имя>.md
id: PHARM-REGIMEN-NNN
schema_version: 2
title: <Название>
domain: pharm
category: regimen
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
    type: treats  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «regimen»):
for: ["DIAG-DISEASE-001"]  # list[id(disease,emergency)]; обязательно для approved
lines: [{"line": 0, "options": [{"agent": "PHARM-DRUG-001", "when": {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}, "note": "<текст>"}]}]  # list[object]; обязательно для approved
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

## Целевая популяция
<заполнить>

## Основные принципы
<заполнить>

## Схема 1-й линии
<заполнить>

## Альтернативные схемы (2-я линия)
<заполнить>

## Комбинированные режимы (если применимо)
<заполнить>

## Мониторинг эффективности
<заполнить>

## Критерии перехода на следующую линию
<заполнить>

## Особенности у особых групп
<заполнить>

## Связанные документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

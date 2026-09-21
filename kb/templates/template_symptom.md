---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: symptom — Симптом / синдром. Файл: kb/diag/symptoms/diag_symptom_<краткое_имя>.md
id: DIAG-SYMPTOM-NNN
schema_version: 2
title: <Название>
domain: diag
category: symptom
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
    type: symptom_of  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «symptom»):
synonyms: ["<текст>"]  # list[string]; обязательно для approved; Синонимы и разговорные формулировки для распознавания
features: [{"code": "<текст>", "label": "<текст>"}]  # list[object]; обязательно для approved; Контролируемые признаки симптома; на них ссылаются атомы feature
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

## Определение
<заполнить>

## Механизм
<заполнить>

## Характеристики
<заполнить>

## Клиническое значение
<заполнить>

## Ассоциированные заболевания
<заполнить>

## 🚩 «Красные флаги»
<заполнить>

## Дифференциально-диагностические критерии
<заполнить>

## Диагностические направления
<заполнить>

## Особенности у отдельных групп
<заполнить>

## Информация для пациента
<заполнить>

## Связанные документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

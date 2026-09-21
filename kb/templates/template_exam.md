---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: exam — Метод обследования. Файл: kb/diag/exams/diag_exam_<краткое_имя>.md
id: DIAG-EXAM-NNN
schema_version: 2
title: <Название>
domain: diag
category: exam
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
    type: diagnoses  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «exam»):
results: [{"value": "<текст>", "label": "<текст>", "indicates": ["DIAG-DISEASE-001"]}]  # list[object]; обязательно для approved; Контролируемые значения результата, на которые ссылается атом exam_result
contraindications: [{"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}]  # list[condition]; необязательно
turnaround: "<текст>"  # string; необязательно; Ориентировочное время получения результата
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

## Назначение метода
<заполнить>

## Показания
<заполнить>

## Диагностическая роль
<заполнить>

## Интерпретация результатов
<заполнить>

## Ограничения
<заполнить>

## Последовательность назначения
<заполнить>

## Связанные заболевания и симптомы
<заполнить>

## Особенности у отдельных групп
<заполнить>

## Связанные документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

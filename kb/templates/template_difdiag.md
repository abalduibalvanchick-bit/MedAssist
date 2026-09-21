---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: difdiag — Дифференциальная диагностика. Файл: kb/diag/differential_diagnosis/diag_difdiag_<краткое_имя>.md
id: DIAG-DIFDIAG-NNN
schema_version: 2
title: <Название>
domain: diag
category: difdiag
body_system: [cardiovascular]  # cardiovascular | respiratory | gastrointestinal | nervous | endocrine | metabolic | urinary | musculoskeletal | immune | reproductive | hematologic | dermatologic | multisystem
tags: [<тег>]
urgency: routine  # routine | urgent | emergency | elective
access_level: professional  # professional | nursing | student | patient
target_specialist: [therapist]  # см. docs/metadata_schema.md, перечисление target_specialist
age_group: [adult]  # neonate | infant | child | adolescent | adult | elderly | all_ages
# evidence_level: Ia  # необязательно: Ia | Ib | IIa | IIb | III | IV
# recommendation_class: I  # необязательно: I | IIa | IIb | III
relations:
  - target: DIAG-REDFLAG-001
    type: has_red_flag  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «difdiag»):
leading_symptom: "DIAG-SYMPTOM-001"  # id(symptom); обязательно для approved
branches: [{"target": "DIAG-DISEASE-001", "supporting": {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}, "against": {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}, "key_exam": "DIAG-EXAM-001", "prior": "high", "urgency": "routine"}]  # list[object]; обязательно для approved
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

## Ведущий симптом
<заполнить>

## Ключевые вопросы при сборе анамнеза
<заполнить>

## Ключевые данные объективного осмотра
<заполнить>

## Дифференциально-диагностическая таблица
<заполнить>

## 🚩 «Красные флаги»
<заполнить>

## Приоритетные диагностические направления
<заполнить>

## Связанные документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

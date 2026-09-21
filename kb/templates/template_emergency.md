---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: emergency — Неотложное состояние (диагностика). Файл: kb/diag/emergencies/diag_emergency_<краткое_имя>.md
id: DIAG-EMERGENCY-NNN
schema_version: 2
title: <Название>
domain: diag
category: emergency
body_system: [cardiovascular]  # cardiovascular | respiratory | gastrointestinal | nervous | endocrine | metabolic | urinary | musculoskeletal | immune | reproductive | hematologic | dermatologic | multisystem
tags: [<тег>]
urgency: routine  # routine | urgent | emergency | elective
access_level: professional  # professional | nursing | student | patient
target_specialist: [therapist]  # см. docs/metadata_schema.md, перечисление target_specialist
age_group: [adult]  # neonate | infant | child | adolescent | adult | elderly | all_ages
# evidence_level: Ia  # необязательно: Ia | Ib | IIa | IIb | III | IV
# recommendation_class: I  # необязательно: I | IIa | IIb | III
relations:
  - target: DIAG-SYMPTOM-001
    type: has_symptom  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «emergency»):
criteria: {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}  # condition; обязательно для approved; Критерии распознавания
emergency_protocol: "PROT-EMERGENCY_P-001"  # id(emergency_p); необязательно
time_critical: true  # boolean; необязательно
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

## Клиническая картина
<заполнить>

## Диагностические критерии
<заполнить>

## Ключевые обследования
<заполнить>

## 🚩 Признаки критического течения
<заполнить>

## Дифференциальная диагностика
<заполнить>

## Тактическая значимость
<заполнить>

## Информация для пациента
<заполнить>

## Связанные документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: redflag — Красный флаг. Файл: kb/diag/red_flags/diag_redflag_<краткое_имя>.md
id: DIAG-REDFLAG-NNN
schema_version: 2
title: <Название>
domain: diag
category: redflag
body_system: [cardiovascular]  # cardiovascular | respiratory | gastrointestinal | nervous | endocrine | metabolic | urinary | musculoskeletal | immune | reproductive | hematologic | dermatologic | multisystem
tags: [<тег>]
urgency: routine  # routine | urgent | emergency | elective
access_level: professional  # professional | nursing | student | patient
target_specialist: [therapist]  # см. docs/metadata_schema.md, перечисление target_specialist
age_group: [adult]  # neonate | infant | child | adolescent | adult | elderly | all_ages
# evidence_level: Ia  # необязательно: Ia | Ib | IIa | IIb | III | IV
# recommendation_class: I  # необязательно: I | IIa | IIb | III
relations:
  - target: DIAG-EXAM-001
    type: diagnosed_by  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «redflag»):
triggers: {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}  # condition; обязательно для approved; Формальное условие срабатывания
indicates: ["DIAG-EMERGENCY-001"]  # list[id(emergency,disease)]; обязательно для approved; На какие состояния указывает
action: "PROT-EMERGENCY_P-001"  # id(emergency_p,routing); необязательно; Куда передать управление
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

## Клиническое значение
<заполнить>

## Когда возникает
<заполнить>

## Возможные ассоциированные состояния
<заполнить>

## Необходимые действия
<заполнить>

## Срочность
<заполнить>

## Связанные обследования
<заполнить>

## Связанные документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

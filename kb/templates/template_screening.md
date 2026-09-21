---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: screening — Скрининг. Файл: kb/prot/screening/prot_screening_<краткое_имя>.md
id: PROT-SCREENING-NNN
schema_version: 2
title: <Название>
domain: prot
category: screening
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
    type: uses_exam  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «screening»):
target: {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}  # condition; обязательно для approved; Кому показан скрининг
methods: ["DIAG-EXAM-001"]  # list[id(exam)]; необязательно; Методы обследования; для программ вакцинации может отсутствовать
interval: "<текст>"  # string; обязательно для approved
positive_when: {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}  # condition; необязательно
on_positive: "PROT-ROUTING-001"  # id(routing,protocol); необязательно
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

## Целевая группа
<заполнить>

## Показания к скринингу
<заполнить>

## Методы скрининга
<заполнить>

## Частота проведения
<заполнить>

## Интерпретация результатов
<заполнить>

## Дальнейшие действия
<заполнить>

## Ограничения
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

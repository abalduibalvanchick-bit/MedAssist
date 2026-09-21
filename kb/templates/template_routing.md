---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: routing — Маршрутизация пациента. Файл: kb/prot/routing/prot_routing_<краткое_имя>.md
id: PROT-ROUTING-NNN
schema_version: 2
title: <Название>
domain: prot
category: routing
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
# Машиночитаемый слой (docs/schema.md, раздел «routing»):
for: ["DIAG-DISEASE-001"]  # list[id(disease,emergency,symptom)]; рекомендуется
decisions: [{"when": {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}, "route": "outpatient", "timeframe": "<текст>", "actions": ["<текст>"], "next": ["PROT-PROTOCOL-001"], "explanation": "<текст>"}]  # list[object]; обязательно для approved; Оцениваются по порядку; срабатывает первое истинное условие
default: {"route": "outpatient", "actions": ["<текст>"], "explanation": "<текст>"}  # object; обязательно для approved
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

## Входные условия
<заполнить>

## Общий принцип маршрутизации
<заполнить>

## Категории маршрута
<заполнить>

## Направление к специалистам
<заполнить>

## Связь с клиническим протоколом
<заполнить>

## Связь с неотложными алгоритмами
<заполнить>

## Комментарии и ограничения
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

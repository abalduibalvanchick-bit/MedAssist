---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: follow_up — Наблюдение пациента. Файл: kb/prot/follow_up/prot_follow_up_<краткое_имя>.md
id: PROT-FOLLOW_UP-NNN
schema_version: 2
title: <Название>
domain: prot
category: follow_up
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
# Машиночитаемый слой (docs/schema.md, раздел «follow_up»):
for: ["DIAG-DISEASE-001"]  # list[id(disease,protocol)]; обязательно для approved
schedule: [{"after": "<текст>", "interval": "<текст>", "purpose": "<текст>"}]  # list[object]; обязательно для approved
monitor: [{"param": "sbp", "exam": "DIAG-EXAM-001", "target": {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}, "label": "<текст>"}]  # list[object]; обязательно для approved
deterioration: {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}  # condition; необязательно
on_deterioration: "PROT-ROUTING-001"  # id(routing,emergency_p); необязательно
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

## Цель наблюдения
<заполнить>

## Кого наблюдаем
<заполнить>

## Частота наблюдения
<заполнить>

## Контрольные параметры
<заполнить>

## Методы контроля
<заполнить>

## Критерии эффективности лечения
<заполнить>

## Критерии ухудшения
<заполнить>

## Действия при ухудшении
<заполнить>

## Коррекция терапии
<заполнить>

## Переход на другой уровень наблюдения
<заполнить>

## Связь с протоколом
<заполнить>

## Ограничения
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

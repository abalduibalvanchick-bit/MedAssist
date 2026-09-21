---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: drugclass — Фармакологическая группа. Файл: kb/pharm/drug_classes/pharm_drugclass_<краткое_имя>.md
id: PHARM-DRUGCLASS-NNN
schema_version: 2
title: <Название>
domain: pharm
category: drugclass
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
# Машиночитаемый слой (docs/schema.md, раздел «drugclass»):
representatives: ["<текст>"]  # list[string]; обязательно для approved; МНН основных представителей группы
members: ["PHARM-DRUG-001"]  # list[id(drug)]; необязательно; Представители, для которых есть карточки
contraindications: [{"when": {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}, "absolute": true, "explanation": "<текст>"}]  # list[object]; необязательно
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

## Общая характеристика
<заполнить>

## Механизм действия (общий для группы)
<заполнить>

## Представители группы
<заполнить>

## Сравнительная характеристика
<заполнить>

## Общие показания
<заполнить>

## Общие противопоказания
<заполнить>

## Общие побочные эффекты
<заполнить>

## Клинически значимые взаимодействия
<заполнить>

## Особенности выбора
<заполнить>

## Связанные документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

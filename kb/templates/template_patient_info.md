---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: patient_info — Памятка для пациента. Файл: kb/prot/patient_info/prot_patient_info_<краткое_имя>.md
id: PROT-PATIENT_INFO-NNN
schema_version: 2
title: <Название>
domain: prot
category: patient_info
body_system: [cardiovascular]  # cardiovascular | respiratory | gastrointestinal | nervous | endocrine | metabolic | urinary | musculoskeletal | immune | reproductive | hematologic | dermatologic | multisystem
tags: [<тег>]
urgency: routine  # routine | urgent | emergency | elective
access_level: professional  # professional | nursing | student | patient
target_specialist: [therapist]  # см. docs/metadata_schema.md, перечисление target_specialist
age_group: [adult]  # neonate | infant | child | adolescent | adult | elderly | all_ages
# evidence_level: Ia  # необязательно: Ia | Ib | IIa | IIb | III | IV
# recommendation_class: I  # необязательно: I | IIa | IIb | III
relations:
  - target: PROT-ROUTING-001
    type: has_routing  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «patient_info»):
for: ["DIAG-DISEASE-001"]  # list[id(disease,emergency,protocol,drug)]; обязательно для approved
seek_help_when: ["<текст>"]  # list[string]; необязательно
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

## Что это за состояние
<заполнить>

## Основные симптомы
<заполнить>

## Что делать сейчас
<заполнить>

## Когда нужно срочно обратиться к врачу
<заполнить>

## Что нельзя делать
<заполнить>

## Общие рекомендации
<заполнить>

## Контроль и наблюдение
<заполнить>

## Связанные медицинские документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

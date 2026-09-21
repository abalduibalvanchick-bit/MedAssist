---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: interaction — Лекарственное взаимодействие. Файл: kb/pharm/interactions/pharm_interaction_<краткое_имя>.md
id: PHARM-INTERACTION-NNN
schema_version: 2
title: <Название>
domain: pharm
category: interaction
body_system: [cardiovascular]  # cardiovascular | respiratory | gastrointestinal | nervous | endocrine | metabolic | urinary | musculoskeletal | immune | reproductive | hematologic | dermatologic | multisystem
tags: [<тег>]
urgency: routine  # routine | urgent | emergency | elective
access_level: professional  # professional | nursing | student | patient
target_specialist: [therapist]  # см. docs/metadata_schema.md, перечисление target_specialist
age_group: [adult]  # neonate | infant | child | adolescent | adult | elderly | all_ages
# evidence_level: Ia  # необязательно: Ia | Ib | IIa | IIb | III | IV
# recommendation_class: I  # необязательно: I | IIa | IIb | III
relations:
  - target: PHARM-DRUG-001
    type: interaction_for  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «interaction»):
between: ["PHARM-DRUG-001"]  # list[id(drug,drugclass)]; обязательно для approved; Участники из базы знаний (один или два)
other_agent: "<текст>"  # string; необязательно; Второй участник, не представленный карточкой (например, контрастное вещество)
severity: "critical"  # enum(interaction_severity); обязательно для approved
trigger: {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}  # condition; необязательно; Условие, при котором взаимодействие актуально для пациента
management: "<текст>"  # string; необязательно
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

## Участники взаимодействия
<заполнить>

## Тип взаимодействия
<заполнить>

## Механизм
<заполнить>

## Клинический эффект
<заполнить>

## Клинические проявления
<заполнить>

## Рекомендации
<заполнить>

## Доказательная база
<заполнить>

## Связанные взаимодействия
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

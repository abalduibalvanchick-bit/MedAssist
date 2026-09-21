---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: disease — Заболевание. Файл: kb/diag/diseases/diag_disease_<краткое_имя>.md
id: DIAG-DISEASE-NNN
schema_version: 2
title: <Название>
domain: diag
category: disease
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
# Машиночитаемый слой (docs/schema.md, раздел «disease»):
presentation: [{"symptom": "DIAG-SYMPTOM-001", "weight": 1, "frequency": "very_common", "features": ["<текст>"]}]  # list[object]; обязательно для approved; Клиническая картина в машиночитаемом виде
red_flags: ["DIAG-REDFLAG-001"]  # list[id(redflag)]; необязательно
exams: [{"exam": "DIAG-EXAM-001", "role": "confirms", "expected": "<текст>"}]  # list[object]; обязательно для approved
differentials: ["DIAG-DISEASE-001"]  # list[id(disease,emergency)]; необязательно
applies_when: {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}  # condition; необязательно; Ограничение применимости карточки (возраст, профиль)
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

## Эпидемиология
<заполнить>

## Этиология и патогенез
<заполнить>

## Классификация
<заполнить>

## Клиническая картина
<заполнить>

## 🚩 «Красные флаги»
<заполнить>

## Диагностика
<заполнить>

## Дифференциальная диагностика
<заполнить>

## Лечение (обзор)
<заполнить>

## Прогноз
<заполнить>

## Профилактика
<заполнить>

## Особенности у отдельных групп
<заполнить>

## Информация для пациента
<заполнить>

## Связанные документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

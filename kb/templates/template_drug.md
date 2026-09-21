---
# Сгенерировано scripts/generate_templates.py из kb/_schema/schema.yaml. Не редактировать вручную.
# Категория: drug — Лекарственное средство. Файл: kb/pharm/drugs/pharm_drug_<краткое_имя>.md
id: PHARM-DRUG-NNN
schema_version: 2
title: <Название>
domain: pharm
category: drug
body_system: [cardiovascular]  # cardiovascular | respiratory | gastrointestinal | nervous | endocrine | metabolic | urinary | musculoskeletal | immune | reproductive | hematologic | dermatologic | multisystem
tags: [<тег>]
urgency: routine  # routine | urgent | emergency | elective
access_level: professional  # professional | nursing | student | patient
target_specialist: [therapist]  # см. docs/metadata_schema.md, перечисление target_specialist
age_group: [adult]  # neonate | infant | child | adolescent | adult | elderly | all_ages
# evidence_level: Ia  # необязательно: Ia | Ib | IIa | IIb | III | IV
# recommendation_class: I  # необязательно: I | IIa | IIb | III
relations:
  - target: PROT-PATIENT_INFO-001
    type: has_patient_info  # типы и допустимые категории: docs/link_types.md
    description: <смысл связи>
# Машиночитаемый слой (docs/schema.md, раздел «drug»):
contraindications: [{"when": {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}, "absolute": true, "explanation": "<текст>"}]  # list[object]; обязательно для approved
interactions: [{"with": "PHARM-DRUG-001", "severity": "critical", "card": "PHARM-INTERACTION-001"}]  # list[object]; необязательно
dose_adjustments: [{"when": {"all": [{"symptom": "DIAG-SYMPTOM-002"}, {"param": "sbp", "op": ">=", "value": 180}]}, "note": "<текст>"}]  # list[object]; необязательно
indications: ["DIAG-DISEASE-001"]  # list[id(disease,emergency,symptom)]; необязательно
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

## Общие сведения
<заполнить>

## Механизм действия
<заполнить>

## Фармакокинетика
<заполнить>

## Показания
<заполнить>

## Дозирование
<заполнить>

## Противопоказания
<заполнить>

## Побочные эффекты
<заполнить>

## Лекарственные взаимодействия
<заполнить>

## Взаимодействие с пищей / алкоголем
<заполнить>

## Беременность и лактация
<заполнить>

## Мониторинг терапии
<заполнить>

## Передозировка
<заполнить>

## Сравнение с аналогами в группе
<заполнить>

## Информация для пациента
<заполнить>

## Связанные документы
<заполнить>

## Источники
<генерируется из поля sources: python scripts/sync_body_sources.py>

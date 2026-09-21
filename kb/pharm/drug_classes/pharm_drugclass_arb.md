---
id: PHARM-DRUGCLASS-002
schema_version: 2
title: Блокаторы рецепторов ангиотензина II (БРА)
domain: pharm
category: drugclass
atc_code: C09CA
body_system:
- cardiovascular
tags:
- arb
- antihypertensive
- cardiology
- support
urgency: routine
access_level: professional
target_specialist:
- therapist
- cardiologist
age_group:
- adult
- elderly
evidence_level: Ia
relations:
- target: DIAG-DISEASE-001
  type: treats
  description: Группа используется при АГ.
- target: PHARM-REGIMEN-001
  type: included_in
  description: Группа входит в варианты схемы лечения АГ.
sources:
- Клинические рекомендации «Артериальная гипертензия у взрослых», 2024
- 2023 ESH Guidelines
clinical_guidelines:
- АГ у взрослых, 2024
- 2023 ESH Guidelines
last_medical_review: '2026-04-09'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №2
version: '2.0'
date_created: '2026-04-09'
date_updated: '2026-09-16'
status: medical_review
disclaimer: true
# Машиночитаемый слой (schema v2) не заполнен. Для status: approved требуются поля: members. См. docs/schema.md, раздел «drugclass».
---

# Блокаторы рецепторов ангиотензина II (БРА)

> Служебная интеграционная карточка для связности фармакологического контура.

## Назначение
Карточка фиксирует фармакологическую группу, которая используется в схеме терапии артериальной гипертензии как альтернатива ингибиторам АПФ.

## Связанные документы
- [[DIAG-DISEASE-001]] Артериальная гипертензия.
- [[PHARM-REGIMEN-001]] Схема лечения артериальной гипертензии.

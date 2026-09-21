---
id: PHARM-DRUGCLASS-010
schema_version: 2
title: Нестероидные противовоспалительные препараты (НПВС)
domain: pharm
category: drugclass
atc_code: M01A
body_system:
- musculoskeletal
- gastrointestinal
tags:
- nsaid
- pain
- gi_bleeding
- support
urgency: urgent
access_level: professional
target_specialist:
- therapist
- gastroenterologist
- all_specialties
age_group:
- adult
- elderly
evidence_level: Ia
relations:
- target: PHARM-ADR-001
  type: causes_adr
  description: НПВС могут повышать риск желудочно-кишечного кровотечения.
sources:
- Клинические рекомендации по НПВС-гастропатии
clinical_guidelines:
- Клинические рекомендации по НПВС-гастропатии
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

# Нестероидные противовоспалительные препараты (НПВС)

> Служебная интеграционная карточка для связи с нежелательной лекарственной реакцией.

## Назначение
Карточка используется для демонстрации связи фармакологической группы с серьёзной нежелательной реакцией.

## Связанные документы
- [[PHARM-ADR-001]] Желудочно-кишечное кровотечение, связанное с приёмом НПВС.

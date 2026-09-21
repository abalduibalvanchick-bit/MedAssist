---
id: PROT-EMERGENCY_P-006
schema_version: 2
title: 'Алгоритм неотложной помощи: Мигренозный статус'
domain: prot
category: emergency_p
body_system:
- nervous
tags:
- emergency
- status_migrainosus
urgency: emergency
access_level: professional
target_specialist:
- neurologist
- emergency_physician
age_group:
- adult
relations:
- target: DIAG-DISEASE-005
  type: emergency_protocol_for
  description: перенесено из поля related (схема v1)
- target: PROT-PROTOCOL-006
  type: emergency_protocol_for
  description: перенесено из поля related (схема v1)
- target: PHARM-REGIMEN-006
  type: recommends
  description: перенесено из поля related (схема v1)
sources:
- AHS Guidelines for Migraine
clinical_guidelines:
- AHS Migraine Guidelines
last_medical_review: '2026-05-06'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.0'
date_created: '2026-05-02'
date_updated: '2026-09-16'
status: medical_review
disclaimer: true
# Машиночитаемый слой (schema v2) не заполнен. Для status: approved требуются поля: criteria, phases. См. docs/schema.md, раздел «emergency_p».
---

# Алгоритм неотложной помощи: Мигренозный статус

> 🚨 Мигренозный статус – приступ мигрени длительностью >72 часов, не купируемый обычными препаратами.

## Критерии
- Головная боль >72 часов с характеристиками мигрени.
- Отсутствие эффекта от триптанов и НПВС.
- Исключены другие причины (субарахноидальное кровоизлияние, менингит, опухоль).

## Действия
1. Госпитализация в неврологическое отделение.
2. Инфузионная терапия: физиологический раствор 500–1000 мл.
3. Противорвотные: метоклопрамид 10 мг в/в (или домперидон внутрь).
4. Нестероидные противовоспалительные: кеторолак 30 мг в/в.
5. Триптаны: суматриптан 6 мг п/к (если не вводился ранее).
6. Кортикостероиды: дексаметазон 8–16 мг в/в (для прерывания статуса).
7. Альтернативы: дигидроэрготамин 0.5–1 мг в/в (противопоказания – ИБС, беременность, гипертензия).
8. Мониторинг АД, пульса, неврологического статуса.

## Ошибки
- Применение опиоидов (не эффективны, вызывают привыкание).
- Отсутствие внутривенной регидратации.

## Дальнейшее наблюдение
- После купирования – профилактическая терапия (PHARM-REGIMEN-006).
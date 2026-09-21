---
id: PROT-PROTOCOL-006
schema_version: 2
title: 'Клинический протокол: Мигрень'
domain: prot
category: protocol
body_system:
- nervous
tags:
- protocol
- migraine
- headache
urgency: urgent
access_level: professional
target_specialist:
- neurologist
- therapist
age_group:
- adult
- child
- all_ages
evidence_level: IIa
recommendation_class: I
relations:
- target: DIAG-DISEASE-005
  type: protocol_for
  description: Протокол ведения пациентов с мигренью.
- target: PHARM-REGIMEN-006
  type: recommends
  description: Схема лечения мигрени.
- target: PROT-PATIENT_INFO-006
  type: has_patient_info
  description: Памятка пациенту.
- target: PROT-EMERGENCY_P-006
  type: has_emergency_protocol
  description: При мигренозном статусе – экстренная госпитализация.
- target: PROT-SCALE-006
  type: assessed_by
  description: перенесено из поля related (схема v1)
- target: PROT-ROUTING-006
  type: has_routing
  description: перенесено из поля related (схема v1)
- target: PROT-FOLLOW_UP-006
  type: has_follow_up
  description: перенесено из поля related (схема v1)
- target: PROT-CHECKLIST-006
  type: has_checklist
  description: перенесено из поля related (схема v1)
- target: PROT-SCREENING-006
  type: has_screening
  description: перенесено из поля related (схема v1)
sources:
- Клинические рекомендации «Мигрень», 2024
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
# Машиночитаемый слой (schema v2) не заполнен. Для status: approved требуются поля: for, entry, steps. См. docs/schema.md, раздел «protocol».
---

# Клинический протокол: Мигрень

> ⚕️ Документ предназначен для медицинских специалистов.

## Назначение протокола
Диагностика, лечение и профилактика мигрени (эпизодической и хронической). Включает купирование острого приступа, профилактическую терапию, обучение пациента.

## Область применения
- Эпизодическая и хроническая мигрень
- Взрослые и дети (с 12 лет)

## Входные условия
- [[DIAG-DISEASE-005]] – установленный диагноз мигрени (по критериям ICHD-3).
- Отсутствие «красных флагов», требующих исключения вторичных причин.

## Критерии начала применения
- Плановая коррекция терапии или оценка эффективности.
- Острое лечение приступа (вне зависимости от протокола).

## Алгоритм ведения
1. Подтверждение диагноза, исключение симптоматической головной боли (неврологический осмотр, при необходимости нейровизуализация).
2. Оценка тяжести, частоты приступов (количество дней с мигренью в месяц).
3. Назначение острого лечения (PHARM-REGIMEN-006) – пациентам с приступами умеренной/тяжёлой степени.
4. Оценка необходимости профилактической терапии (≥4 дней/мес или инвалидизация).
5. Выбор профилактического препарата (бета-блокаторы, топирамат, амитриптилин).
6. Обучение пациента (дневник, триггеры, не злоупотреблять анальгетиками).
7. Контроль эффективности через 1–3 месяца.

## Ключевые решения
- **Нечастые лёгкие приступы** → только купирование (НПВС, при неэффективности – триптаны).
- **Частые (≥4 дней/мес) или инвалидизирующие** → назначить профилактику.
- **Мигренозный статус (приступ >72 часов)** → госпитализация, переход к PROT-EMERGENCY_P-006.

## Критерии срочности
- **Routine**: плановый визит.
- **Urgent**: рефрактерные приступы, не купируемые триптанами.
- **Emergency**: мигренозный статус.

## Связанные документы
- [[PHARM-REGIMEN-006]] – лечение
- [[PROT-PATIENT_INFO-006]] – памятка
- [[PROT-EMERGENCY_P-006]] – неотложная помощь

## Ограничения
- Не适用于 вторичные головные боли.

## Источники
1. Клинические рекомендации «Мигрень», 2024.
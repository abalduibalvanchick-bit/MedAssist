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
for:
- DIAG-DISEASE-005
entry:
  any:
  - disease: DIAG-DISEASE-005
  - fact: known_migraine
steps:
- id: exclude_secondary
  action: неврологический осмотр, исключение красных флагов вторичной головной боли
  refs:
  - DIAG-EXAM-009
  - DIAG-REDFLAG-002
- id: severity
  action: оценка дезадаптации по MIDAS и числа дней с головной болью
  refs:
  - PROT-SCALE-006
- id: acute
  action: 'купирование приступа: НПВС или триптаны'
  refs:
  - PHARM-REGIMEN-006
  - PHARM-DRUGCLASS-010
  - PHARM-DRUGCLASS-022
- id: prophylaxis
  action: профилактическая терапия при 4 и более днях мигрени в месяц или выраженной дезадаптации
  when:
    any:
    - param: migraine_days_per_month
      op: '>='
      value: 4
    - scale: PROT-SCALE-006
      op: '>='
      value: 11
  refs:
  - PHARM-REGIMEN-006
- id: triggers
  action: дневник головной боли, контроль триггеров, профилактика лекарственного абузуса
  refs:
  - PHARM-NONPHARM-006
- id: follow_up
  action: оценка эффекта профилактики через 2–3 месяца
  refs:
  - PROT-FOLLOW_UP-006
branches:
- when:
    redflag: DIAG-REDFLAG-002
  then: PROT-ROUTING-006
  explanation: вторичная головная боль — экстренный маршрут
- when:
    emergency: DIAG-EMERGENCY-006
  then: PROT-EMERGENCY_P-006
  explanation: мигренозный статус
- when:
    scale: PROT-SCALE-006
    op: '>='
    value: 11
  then: PROT-ROUTING-006
  explanation: умеренная или тяжёлая дезадаптация
targets:
- param: migraine_days_per_month
  op: <
  value: 4
  label: менее 4 дней мигрени в месяц
sources:
- Клинические рекомендации «Мигрень». Минздрав РФ, 2024.
- 'Ailani J. et al. The American Headache Society Consensus Statement: Update on integrating new migraine treatments into clinical practice. Headache. 2021;61(7):1021–1039.'
clinical_guidelines:
- КР «Мигрень», Минздрав РФ, 2024
- AHS Consensus Statement on migraine treatment, 2021
last_medical_review: '2026-05-06'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.1'
date_created: '2026-05-02'
date_updated: '2026-09-16'
status: approved
disclaimer: true
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
1. Клинические рекомендации «Мигрень». Минздрав РФ, 2024.
2. Ailani J. et al. The American Headache Society Consensus Statement: Update on integrating new migraine treatments into clinical practice. Headache. 2021;61(7):1021–1039.

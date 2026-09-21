---
id: PROT-CHECKLIST-001
schema_version: 2
title: 'Чек-лист врача: первичный приём при артериальной гипертензии'
domain: prot
category: checklist
body_system:
- cardiovascular
tags:
- checklist
- hypertension
- primary_visit
urgency: routine
access_level: professional
target_specialist:
- therapist
- cardiologist
age_group:
- adult
relations:
- target: PROT-PROTOCOL-001
  type: checklist_for
  description: Чек-лист используется при первичном применении протокола.
- target: DIAG-DISEASE-001
  type: checklist_for
  description: Чек-лист относится к первичному приёму пациента с АГ.
- target: DIAG-EXAM-001
  type: uses_exam
  description: В чек-листе предусмотрено измерение артериального давления.
items:
- text: головная боль
  required: true
- text: головокружение
  required: true
- text: боль в груди
  required: true
- text: одышка
  required: true
- text: факторы риска (курение, ожирение, стресс)
  required: true
- text: измерение артериального давления
  required: true
  refs:
  - DIAG-EXAM-001
- text: частота сердечных сокращений
  required: true
- text: оценка общего состояния
  required: true
- text: неврологический статус
  required: true
- text: наличие поражения органов-мишеней
  required: true
- text: сопутствующие заболевания
  required: true
- text: общий сердечно-сосудистый риск
  required: true
- text: подтверждение диагноза
  required: true
  refs:
  - DIAG-DISEASE-001
- text: необходимость дополнительных обследований
  required: true
- text: определить план лечения
  required: true
  refs:
  - PROT-PROTOCOL-001
- text: определить маршрут пациента
  required: true
- text: дать рекомендации пациенту
  required: true
- text: назначить контрольный визит
  required: true
- text: объяснить пациенту план действий
  required: true
sources:
- Клинические рекомендации по артериальной гипертензии
- Mancia G. et al. 2023 ESH Guidelines for the management of arterial hypertension. J Hypertens. 2023;41:1874–2071.
- Клинические рекомендации «Артериальная гипертензия у взрослых». Минздрав РФ, 2024.
clinical_guidelines:
- Клинические рекомендации по артериальной гипертензии, 2024
last_medical_review: '2026-04-09'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.2'
date_created: '2026-04-09'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Чек-лист врача: первичный приём при артериальной гипертензии

> Документ предназначен для стандартизации действий врача на первичном приёме.

## Жалобы и анамнез
- [ ] головная боль
- [ ] головокружение
- [ ] боль в груди
- [ ] одышка
- [ ] факторы риска (курение, ожирение, стресс)

## Объективное обследование
- [ ] [[DIAG-EXAM-001]] измерение артериального давления
- [ ] частота сердечных сокращений
- [ ] оценка общего состояния
- [ ] неврологический статус

## Оценка риска
- [ ] наличие поражения органов-мишеней
- [ ] сопутствующие заболевания
- [ ] общий сердечно-сосудистый риск

## Диагностические решения
- [ ] подтверждение диагноза [[DIAG-DISEASE-001]]
- [ ] необходимость дополнительных обследований

## Тактика ведения
- [ ] определить план лечения [[PROT-PROTOCOL-001]]
- [ ] определить маршрут пациента
- [ ] дать рекомендации пациенту

## Завершение приёма
- [ ] назначить контрольный визит
- [ ] объяснить пациенту план действий

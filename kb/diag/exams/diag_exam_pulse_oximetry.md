---
id: DIAG-EXAM-010
schema_version: 2
title: Пульсоксиметрия
domain: diag
category: exam
body_system:
- respiratory
- cardiovascular
tags:
- spo2
- pulse_oximetry
- hypoxemia
- exam
urgency: urgent
access_level: professional
target_specialist:
- therapist
- pulmonologist
- emergency_physician
- nursing
age_group:
- all_ages
evidence_level: IIa
recommendation_class: I
relations:
- target: DIAG-EMERGENCY-003
  type: diagnoses
  description: выявляет гипоксемию при острой дыхательной недостаточности
- target: DIAG-EMERGENCY-005
  type: diagnoses
  description: критерий тяжести обострения астмы
- target: DIAG-DISEASE-003
  type: diagnoses
  description: оценка тяжести пневмонии
- target: DIAG-SYMPTOM-003
  type: diagnoses
  description: базовое исследование при одышке
results:
- value: normal
  label: SpO₂ 95 % и выше
- value: mild_hypoxemia
  label: SpO₂ 90–94 %
- value: severe_hypoxemia
  label: SpO₂ менее 90 %
  indicates:
  - DIAG-EMERGENCY-003
turnaround: немедленно
sources:
- British Thoracic Society Guideline for oxygen use in healthcare and emergency settings. Thorax. 2017;72(Suppl 1).
- Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
- Global Initiative for Asthma. Global Strategy for Asthma Management and Prevention, 2025 update.
clinical_guidelines:
- КР «Внебольничная пневмония у взрослых», Минздрав РФ, 2024
- GINA 2025
last_medical_review: '2026-09-16'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.0'
date_created: '2026-09-16'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Пульсоксиметрия

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов.

## Определение
Неинвазивное измерение насыщения гемоглобина артериальной крови кислородом (SpO₂) и частоты пульса с помощью пульсоксиметра.

## Назначение метода
Быстрое выявление гипоксемии и оценка тяжести дыхательных и сердечно-сосудистых состояний; мониторинг в динамике.

## Показания
- одышка любого генеза;
- подозрение на пневмонию, обострение астмы, острую дыхательную недостаточность;
- мониторинг при неотложных состояниях.

## Диагностическая роль
SpO₂ менее 90 % указывает на выраженную гипоксемию и острую дыхательную недостаточность. SpO₂ менее 92 % при обострении астмы и менее 93 % при пневмонии — критерии тяжёлого течения и показание к госпитализации.

## Интерпретация результатов
| Результат | Значение |
|---|---|
| 95 % и выше | Норма |
| 90–94 % | Умеренная гипоксемия, требуется оценка тяжести |
| Менее 90 % | Выраженная гипоксемия, экстренная ситуация |

## Ограничения
Искажение показаний при низкой перфузии, выраженной анемии, отравлении угарным газом, лаке на ногтях, движении пациента. Не отражает уровень углекислого газа.

## Последовательность назначения
Выполняется одновременно с измерением ЧСС, ЧДД и АД при первичной оценке.

## Связанные документы
- [[DIAG-SYMPTOM-003]] Одышка
- [[DIAG-EMERGENCY-003]] Острая дыхательная недостаточность

## Источники
1. British Thoracic Society Guideline for oxygen use in healthcare and emergency settings. Thorax. 2017;72(Suppl 1).
2. Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
3. Global Initiative for Asthma. Global Strategy for Asthma Management and Prevention, 2025 update.

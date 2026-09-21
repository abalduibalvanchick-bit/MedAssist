---
id: DIAG-EXAM-004
schema_version: 2
title: Рентгенография органов грудной клетки
domain: diag
category: exam
body_system:
- respiratory
- cardiovascular
tags:
- xray
- chest_xray
- exam
- pneumonia
- dyspnea
urgency: routine
access_level: professional
target_specialist:
- therapist
- pulmonologist
- radiologist
- emergency_physician
age_group:
- adult
- elderly
- all_ages
recommendation_class: I
relations:
- target: DIAG-DISEASE-003
  type: diagnoses
  description: помогает выявить инфильтративные изменения при пневмонии
- target: DIAG-SYMPTOM-003
  type: diagnoses
  description: используется при оценке лёгочных причин одышки
- target: DIAG-DIFDIAG-003
  type: exam_used_in
  description: помогает дифференцировать лёгочные причины одышки
- target: DIAG-SYMPTOM-004
  type: diagnoses
  description: перенесено из поля related (схема v1)
results:
- value: normal
  label: без очаговых и инфильтративных изменений
- value: infiltrate
  label: очагово-инфильтративные изменения
  indicates:
  - DIAG-DISEASE-003
- value: pleural_effusion
  label: плевральный выпот
- value: pneumothorax
  label: пневмоторакс
- value: pulmonary_edema
  label: признаки отёка лёгких
contraindications:
- fact: pregnant
turnaround: 30–60 минут
sources:
- Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
- Global Initiative for Asthma. Global Strategy for Asthma Management and Prevention, 2025 update.
clinical_guidelines:
- КР «Внебольничная пневмония у взрослых», Минздрав РФ, 2024
- GINA 2025
last_medical_review: '2026-04-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.1'
date_created: '2026-04-30'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Рентгенография органов грудной клетки

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не является руководством по самолечению и не заменяет клиническое решение врача.

## Определение
Рентгенография органов грудной клетки — инструментальный метод визуализации, позволяющий оценить лёгкие, плевральные полости, средостение и косвенные признаки некоторых сердечно-сосудистых изменений.

## Назначение метода
Метод применяется при подозрении на пневмонию, плевральный выпот, пневмоторакс, некоторые причины одышки и боли в груди.

## Показания
- кашель с лихорадкой;
- [[DIAG-SYMPTOM-003]] одышка;
- подозрение на [[DIAG-DISEASE-003]] пневмонию;
- боль в груди с дыхательной симптоматикой;
- оценка осложнений по назначению врача.

## Диагностическая роль
Рентгенография помогает выявить инфильтрацию лёгочной ткани, плевральный выпот, ателектаз, пневмоторакс и другие изменения. Результат требует интерпретации врачом с учётом симптомов и осмотра.

## Интерпретация результатов
| Находка | Возможное значение |
|---|---|
| Инфильтративные изменения | Возможная пневмония |
| Плевральный выпот | Воспалительная, сердечная, опухолевая или другая причина |
| Пневмоторакс | Неотложное состояние при соответствующей клинике |
| Отсутствие изменений | Не всегда исключает раннюю патологию |

## Ограничения
Метод имеет ограниченную чувствительность на ранних стадиях некоторых заболеваний и не заменяет клиническую оценку. При необходимости врач назначает дополнительные методы.

## Связанные документы
- [[DIAG-DISEASE-003]] — пневмония.
- [[DIAG-SYMPTOM-003]] — одышка.
- [[DIAG-DIFDIAG-003]] — дифференциальная диагностика одышки.

## Источники
1. Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
2. Global Initiative for Asthma. Global Strategy for Asthma Management and Prevention, 2025 update.

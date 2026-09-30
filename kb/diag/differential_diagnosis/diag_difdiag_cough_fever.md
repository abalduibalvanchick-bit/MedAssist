---
id: DIAG-DIFDIAG-004
schema_version: 2
title: Дифференциальная диагностика кашля с лихорадкой
domain: diag
category: difdiag
body_system:
- respiratory
tags:
- cough
- fever
- differential
- pneumonia
urgency: urgent
access_level: professional
target_specialist:
- therapist
age_group:
- adult
- elderly
relations:
- target: DIAG-SYMPTOM-008
  type: differential_for
  description: ведущий симптом
- target: DIAG-DISEASE-003
  type: considers
  description: основная рассматриваемая причина
- target: DIAG-DISEASE-004
  type: considers
  description: кашлевой вариант и обострение астмы
- target: DIAG-EMERGENCY-003
  type: considers
  description: осложнение — дыхательная недостаточность
- target: DIAG-EXAM-004
  type: uses_exam
  description: выведено из машиночитаемого слоя (branches)
- target: DIAG-EXAM-010
  type: uses_exam
  description: выведено из машиночитаемого слоя (branches)
- target: DIAG-REDFLAG-003
  type: considers
  description: выведено из машиночитаемого слоя (branches)
- target: DIAG-EXAM-008
  type: uses_exam
  description: выведено из машиночитаемого слоя (branches)
leading_symptom: DIAG-SYMPTOM-008
branches:
- target: DIAG-DISEASE-003
  supporting:
    all:
    - symptom: DIAG-SYMPTOM-004
    - any:
      - feature: cough.productive
      - feature: cough.purulent_sputum
      - feature: cough.rusty_sputum
  against:
    feature: cough.chronic
  key_exam: DIAG-EXAM-004
  prior: high
  urgency: urgent
- target: DIAG-EMERGENCY-003
  supporting:
    any:
    - param: spo2
      op: <
      value: 90
    - param: rr
      op: '>='
      value: 30
  key_exam: DIAG-EXAM-010
  prior: low
  urgency: emergency
- target: DIAG-REDFLAG-003
  supporting:
    feature: dyspnea.cyanosis
  key_exam: DIAG-EXAM-010
  prior: low
  urgency: emergency
- target: DIAG-DISEASE-004
  supporting:
    any:
    - feature: cough.nocturnal
    - symptom: DIAG-SYMPTOM-009
  against:
    symptom: DIAG-SYMPTOM-004
  key_exam: DIAG-EXAM-008
  prior: medium
  urgency: routine
sources:
- Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
- Metlay J.P. et al. Diagnosis and Treatment of Adults with Community-acquired Pneumonia. An Official Clinical Practice Guideline of the ATS and IDSA. Am J Respir Crit Care Med. 2019;200(7):e45–e67.
clinical_guidelines:
- КР «Внебольничная пневмония у взрослых», Минздрав РФ, 2024
last_medical_review: '2026-09-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.0'
date_created: '2026-09-30'
date_updated: '2026-09-30'
status: approved
disclaimer: true
---

# Дифференциальная диагностика кашля с лихорадкой

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не заменяет консультацию врача.

## Ведущий симптом
Острый кашель (менее 3 недель) в сочетании с лихорадкой.

## Ключевые вопросы при сборе анамнеза
- длительность кашля и лихорадки, характер мокроты;
- одышка, боль в груди при дыхании;
- свистящее дыхание, связь с аллергенами, астма в анамнезе;
- сопутствующие заболевания, иммунодефицит, недавний приём антибиотиков.

## Ключевые данные объективного осмотра
Температура, частота дыхания, SpO₂, АД, уровень сознания; локальные влажные хрипы и притупление перкуторного звука при пневмонии, диффузные сухие свистящие хрипы при астме.

## Дифференциально-диагностическая таблица
| Состояние | За | Против | Ключевое исследование |
|---|---|---|---|
| Внебольничная пневмония | лихорадка + продуктивный кашель, локальные хрипы | хронический кашель | рентгенография |
| Острая дыхательная недостаточность | SpO₂ < 90 %, ЧДД ≥ 30 | — | пульсоксиметрия |
| Бронхиальная астма | ночной кашель, свистящее дыхание | лихорадка | спирометрия |

## 🚩 «Красные флаги»
- SpO₂ менее 90 %, ЧДД 30 и более;
- спутанность сознания;
- гипотензия;
- цианоз.

## Приоритетные диагностические направления
Пульсоксиметрия и оценка по CURB-65 — сразу; рентгенография органов грудной клетки, общий анализ крови, мочевина.

## Связанные документы
- [[DIAG-SYMPTOM-008]] Кашель — ведущий симптом
- [[DIAG-DISEASE-003]] Пневмония — основная рассматриваемая причина
- [[DIAG-DISEASE-004]] Бронхиальная астма — кашлевой вариант и обострение астмы
- [[DIAG-EMERGENCY-003]] Острая дыхательная недостаточность — осложнение — дыхательная недостаточность

## Источники
1. Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
2. Metlay J.P. et al. Diagnosis and Treatment of Adults with Community-acquired Pneumonia. An Official Clinical Practice Guideline of the ATS and IDSA. Am J Respir Crit Care Med. 2019;200(7):e45–e67.

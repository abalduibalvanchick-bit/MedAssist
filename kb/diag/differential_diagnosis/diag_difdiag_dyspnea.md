---
id: DIAG-DIFDIAG-003
schema_version: 2
title: Дифференциальная диагностика одышки
domain: diag
category: difdiag
body_system:
- respiratory
- cardiovascular
- multisystem
tags:
- difdiag
- dyspnea
- respiratory
- cardiology
urgency: urgent
access_level: professional
target_specialist:
- therapist
- pulmonologist
- cardiologist
- emergency_physician
age_group:
- adult
- elderly
- all_ages
evidence_level: IV
recommendation_class: I
relations:
- target: DIAG-SYMPTOM-003
  type: differential_for
  description: ведущий симптом
- target: DIAG-DISEASE-003
  type: considers
  description: инфекционно-лёгочная причина
- target: DIAG-DISEASE-004
  type: considers
  description: бронхообструктивная причина
- target: DIAG-EMERGENCY-003
  type: considers
  description: неотложное состояние при тяжёлой одышке
- target: DIAG-EXAM-004
  type: uses_exam
  description: помогает оценить лёгочные причины
- target: DIAG-REDFLAG-003
  type: considers
  description: перенесено из поля related (схема v1)
- target: DIAG-EXAM-002
  type: uses_exam
  description: перенесено из поля related (схема v1)
- target: DIAG-EXAM-010
  type: uses_exam
  description: выведено из машиночитаемого слоя (branches)
- target: DIAG-EMERGENCY-005
  type: considers
  description: выведено из машиночитаемого слоя (branches)
- target: DIAG-EMERGENCY-001
  type: considers
  description: выведено из машиночитаемого слоя (branches)
- target: DIAG-EXAM-008
  type: uses_exam
  description: выведено из машиночитаемого слоя (branches)
leading_symptom: DIAG-SYMPTOM-003
branches:
- target: DIAG-EMERGENCY-003
  supporting:
    any:
    - param: spo2
      op: <
      value: 90
    - param: rr
      op: '>='
      value: 30
    - feature: dyspnea.cyanosis
  key_exam: DIAG-EXAM-010
  prior: medium
  urgency: emergency
- target: DIAG-EMERGENCY-005
  supporting:
    any:
    - feature: wheezing.silent_chest
    - feature: wheezing.reliever_unresponsive
  key_exam: DIAG-EXAM-010
  prior: low
  urgency: emergency
- target: DIAG-EMERGENCY-001
  supporting:
    symptom: DIAG-SYMPTOM-002
  key_exam: DIAG-EXAM-002
  prior: medium
  urgency: emergency
- target: DIAG-DISEASE-004
  supporting:
    all:
    - symptom: DIAG-SYMPTOM-009
    - any:
      - feature: dyspnea.episodic
      - feature: wheezing.after_trigger
  against:
    symptom: DIAG-SYMPTOM-004
  key_exam: DIAG-EXAM-008
  prior: high
  urgency: routine
- target: DIAG-DISEASE-003
  supporting:
    all:
    - symptom: DIAG-SYMPTOM-004
    - symptom: DIAG-SYMPTOM-008
  key_exam: DIAG-EXAM-004
  prior: high
  urgency: urgent
sources:
- Клинические рекомендации по внебольничной пневмонии у взрослых, действующая редакция.
- GINA Global Strategy for Asthma Management and Prevention, действующая редакция.
- Руководства по пульмонологии и внутренним болезням.
- Техническое задание к БЗ MedAssist, раздел 3.1.
clinical_guidelines:
- Клинические рекомендации по внебольничной пневмонии у взрослых
- GINA Global Strategy for Asthma Management and Prevention
last_medical_review: '2026-04-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.1'
date_created: '2026-04-30'
date_updated: '2026-09-16'
status: medical_review
disclaimer: true
---

# Дифференциальная диагностика: одышка

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не является руководством по самолечению и не заменяет клиническое решение врача.

## Ведущий симптом
[[DIAG-SYMPTOM-003]] Одышка.

## Ключевые вопросы при сборе анамнеза
1. Когда возникла одышка и как быстро нарастала? — помогает отделить острое состояние от хронического.
2. Есть ли кашель, лихорадка, боль в груди? — ориентирует на инфекционную, плевральную или кардиальную причину.
3. Есть ли свистящее дыхание и приступообразность? — указывает на бронхообструкцию.
4. Возникает ли одышка в положении лёжа или ночью? — может указывать на кардиальную причину.
5. Есть ли цианоз, спутанность сознания, невозможность говорить? — признаки срочности.

## Ключевые данные объективного осмотра
- частота дыхания;
- сатурация при наличии пульсоксиметра;
- аускультация лёгких;
- частота пульса и АД;
- признаки цианоза и нарушения сознания.

## Дифференциально-диагностическая таблица
| Направление | Поддерживающие признаки | Документ БЗ |
|---|---|---|
| Пневмония | лихорадка, кашель, хрипы, изменения на рентгенографии | [[DIAG-DISEASE-003]] |
| Бронхиальная астма | приступы, свистящее дыхание, триггеры | [[DIAG-DISEASE-004]] |
| Острая дыхательная недостаточность | выраженная одышка, цианоз, нарушение сознания | [[DIAG-EMERGENCY-003]] |
| Кардиальная причина | боль в груди, отёки, одышка при нагрузке/лёжа | [[DIAG-EXAM-002]] |

## 🚩 «Красные флаги»
- [[DIAG-REDFLAG-003]] выраженная одышка и цианоз;
- одышка в покое;
- боль в груди;
- спутанность сознания;
- внезапное начало;
- быстрое ухудшение.

## Приоритетные диагностические направления
- оценка жизненных показателей;
- [[DIAG-EXAM-004]] рентгенография органов грудной клетки при лёгочной симптоматике;
- [[DIAG-EXAM-002]] ЭКГ при подозрении на кардиальную причину;
- лабораторные исследования по клинической ситуации.

## Связанные документы
- [[DIAG-SYMPTOM-003]] — одышка.
- [[DIAG-DISEASE-003]] — пневмония.
- [[DIAG-DISEASE-004]] — бронхиальная астма.
- [[DIAG-EMERGENCY-003]] — острая дыхательная недостаточность.
- [[DIAG-REDFLAG-003]] — выраженная одышка и цианоз.

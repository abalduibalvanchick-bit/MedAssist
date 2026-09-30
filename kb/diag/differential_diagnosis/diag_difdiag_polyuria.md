---
id: DIAG-DIFDIAG-005
schema_version: 2
title: Дифференциальная диагностика полиурии и жажды
domain: diag
category: difdiag
body_system:
- endocrine
tags:
- polyuria
- polydipsia
- differential
- diabetes
urgency: urgent
access_level: professional
target_specialist:
- therapist
age_group:
- adult
- elderly
relations:
- target: DIAG-SYMPTOM-006
  type: differential_for
  description: ведущий симптом
- target: DIAG-DISEASE-006
  type: considers
  description: основная рассматриваемая причина
- target: DIAG-EMERGENCY-004
  type: considers
  description: гиперосмолярное состояние
- target: DIAG-REDFLAG-004
  type: considers
  description: диабетический кетоацидоз
- target: DIAG-EXAM-014
  type: uses_exam
  description: выведено из машиночитаемого слоя (branches)
- target: DIAG-EXAM-005
  type: uses_exam
  description: выведено из машиночитаемого слоя (branches)
leading_symptom: DIAG-SYMPTOM-006
branches:
- target: DIAG-REDFLAG-004
  supporting:
    any:
    - param: ketones_positive
    - exam_result: DIAG-EXAM-014
      value: high
    - feature: nausea_vomiting.repeated
  key_exam: DIAG-EXAM-014
  prior: low
  urgency: emergency
- target: DIAG-EMERGENCY-004
  supporting:
    any:
    - param: glucose
      op: '>='
      value: 33.3
    - fact: confusion
  key_exam: DIAG-EXAM-005
  prior: low
  urgency: emergency
- target: DIAG-DISEASE-006
  supporting:
    any:
    - param: glucose
      op: '>='
      value: 11.1
    - param: hba1c
      op: '>='
      value: 6.5
    - symptom: DIAG-SYMPTOM-007
  key_exam: DIAG-EXAM-005
  prior: high
  urgency: routine
sources:
- American Diabetes Association Professional Practice Committee. Standards of Care in Diabetes — 2025. Diabetes Care. 2025;48(Suppl 1).
- 'Umpierrez G.E. et al. Hyperglycemic crises in adults with diabetes: a consensus report. Diabetes Care. 2024;47:1257–1275.'
clinical_guidelines:
- ADA Standards of Care in Diabetes — 2025
- ADA/EASD consensus report on hyperglycemic crises, 2024
last_medical_review: '2026-09-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.0'
date_created: '2026-09-30'
date_updated: '2026-09-30'
status: approved
disclaimer: true
---

# Дифференциальная диагностика полиурии и жажды

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не заменяет консультацию врача.

## Ведущий симптом
Полиурия (учащённое и обильное мочеиспускание), как правило в сочетании с жаждой.

## Ключевые вопросы при сборе анамнеза
- давность симптомов, похудание, слабость;
- тошнота, рвота, боль в животе;
- известный сахарный диабет и принимаемые препараты (в том числе иНГЛТ-2, диуретики);
- изменение сознания.

## Ключевые данные объективного осмотра
Признаки обезвоживания (сухость слизистых, тахикардия, гипотензия), дыхание Куссмауля, запах ацетона, уровень сознания.

## Дифференциально-диагностическая таблица
| Состояние | За | Ключевое исследование |
|---|---|---|
| Сахарный диабет 2 типа | гликемия ≥ 11,1 ммоль/л или HbA1c ≥ 6,5 %, жажда | глюкоза плазмы, HbA1c |
| Диабетический кетоацидоз | кетоны, рвота, боль в животе | кетоны крови |
| Гиперосмолярное состояние | гликемия ≥ 33,3 ммоль/л, спутанность сознания | глюкоза, осмоляльность |

## 🚩 «Красные флаги»
- спутанность или угнетение сознания;
- многократная рвота, боль в животе;
- гликемия более 13,9 ммоль/л с кетонами;
- выраженное обезвоживание, гипотензия.

## Приоритетные диагностические направления
Глюкоза крови экспресс-методом; при гипергликемии — кетоны, электролиты, креатинин; в плановом порядке — HbA1c.

## Связанные документы
- [[DIAG-SYMPTOM-006]] Полиурия (частое мочеиспускание) — ведущий симптом
- [[DIAG-DISEASE-006]] Сахарный диабет 2 типа — основная рассматриваемая причина
- [[DIAG-EMERGENCY-004]] Гиперосмолярное гипергликемическое состояние (ГГС) — гиперосмолярное состояние
- [[DIAG-REDFLAG-004]] Диабетический кетоацидоз (ДКА) — диабетический кетоацидоз

## Источники
1. American Diabetes Association Professional Practice Committee. Standards of Care in Diabetes — 2025. Diabetes Care. 2025;48(Suppl 1).
2. Umpierrez G.E. et al. Hyperglycemic crises in adults with diabetes: a consensus report. Diabetes Care. 2024;47:1257–1275.

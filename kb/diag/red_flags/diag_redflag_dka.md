---
id: DIAG-REDFLAG-004
schema_version: 2
title: Диабетический кетоацидоз (ДКА)
domain: diag
category: redflag
body_system:
- endocrine
- multisystem
tags:
- dka
- ketoacidosis
- diabetes
- emergency
urgency: emergency
access_level: professional
target_specialist:
- endocrinologist
- emergency_physician
- icu
age_group:
- adult
- elderly
evidence_level: IIa
recommendation_class: I
relations:
- target: DIAG-DISEASE-006
  type: red_flag_for
  description: редкое, но возможное осложнение СД2 при тяжёлой декомпенсации
- target: DIAG-EMERGENCY-004
  type: red_flag_for
  description: может перейти в гиперосмолярное состояние или сочетаться с ним
- target: DIAG-SYMPTOM-006
  type: red_flag_for
  description: перенесено из поля related (схема v1)
- target: DIAG-SYMPTOM-007
  type: red_flag_for
  description: перенесено из поля related (схема v1)
- target: DIAG-EXAM-005
  type: diagnosed_by
  description: перенесено из поля related (схема v1)
triggers:
  all:
  - param: glucose
    op: '>'
    value: 13.9
  - any:
    - param: ketones_positive
    - all:
      - symptom: DIAG-SYMPTOM-005
      - feature: abdominal_pain.vomiting
    - fact: confusion
indicates:
- DIAG-DISEASE-006
action: PROT-EMERGENCY_P-002
sources:
- Алгоритмы специализированной медицинской помощи больным сахарным диабетом / Под ред. И.И. Дедова, М.В. Шестаковой, А.Ю. Майорова. — 11-й выпуск. — М., 2023.
- Dhatariya K.K. et al. Diabetic ketoacidosis. Nat Rev Dis Primers. 2020;6:40.
- 'American Diabetes Association. Standards of Care in Diabetes — 2025. Section 16: Diabetes Care in the Hospital (hyperglycemic crises).'
clinical_guidelines:
- Алгоритмы специализированной медицинской помощи больным сахарным диабетом, 11-й выпуск, 2023
last_medical_review: '2026-05-06'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.1'
date_created: '2026-05-02'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Диабетический кетоацидоз (ДКА)

> ⚕️ **Дисклеймер**: Информация носит справочный характер. Красный флаг указывает на необходимость срочной клинической оценки.

## Определение
Диабетический кетоацидоз – острое, жизнеугрожающее осложнение диабета, характеризующееся гипергликемией > 13.9 ммоль/л, метаболическим ацидозом (pH < 7.3) и наличием кетоновых тел в крови/моче. Характерен для СД1, но может встречаться и при СД2 в состоянии тяжёлого стресса (инфекция, инфаркт, панкреатит, отмена терапии).

## Клиническое значение
ДКА при СД2 возникает реже, чем при СД1, но требует неотложной госпитализации и интенсивной терапии из-за риска отёка мозга, полиорганной недостаточности и летального исхода.

## Когда возникает
- Интеркуррентные заболевания (пневмония, сепсис, ИМ).
- Нарушение режима лечения (пропуск инсулина или сахароснижающих препаратов).
- Тяжёлый стресс, травма.
- Злоупотребление алкоголем.

## Возможные ассоциированные состояния
- [[DIAG-DISEASE-006]] Сахарный диабет 2 типа
- [[DIAG-EMERGENCY-004]] Гиперосмолярное гипергликемическое состояние (может сочетаться)

## Необходимые действия
- Срочная госпитализация (ОРИТ).
- Инфузионная терапия, инсулин в/в, коррекция электролитов.
- Мониторинг pH, кетонов, электролитов, глюкозы.

## Срочность
- **Уровень срочности**: emergency
- **К кому направлять**: скорая помощь → приёмное отделение → реанимация

## Связанные обследования
- Глюкоза, кетоны крови/мочи, газовый состав крови, электролиты, креатинин, ОАК.

## Связанные документы
- [[DIAG-DISEASE-006]] Сахарный диабет 2 типа
- [[DIAG-EMERGENCY-004]] Гиперосмолярное гипергликемическое состояние

## Источники
1. Алгоритмы специализированной медицинской помощи больным сахарным диабетом / Под ред. И.И. Дедова, М.В. Шестаковой, А.Ю. Майорова. — 11-й выпуск. — М., 2023.
2. Dhatariya K.K. et al. Diabetic ketoacidosis. Nat Rev Dis Primers. 2020;6:40.
3. American Diabetes Association. Standards of Care in Diabetes — 2025. Section 16: Diabetes Care in the Hospital (hyperglycemic crises).

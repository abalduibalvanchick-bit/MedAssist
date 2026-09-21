---
id: DIAG-REDFLAG-003
schema_version: 2
title: Выраженная одышка и цианоз
domain: diag
category: redflag
body_system:
- respiratory
- cardiovascular
- multisystem
tags:
- redflag
- dyspnea
- cyanosis
- emergency
urgency: emergency
access_level: professional
target_specialist:
- therapist
- pulmonologist
- emergency_physician
- icu
age_group:
- adult
- elderly
- all_ages
evidence_level: IIa
recommendation_class: I
relations:
- target: DIAG-SYMPTOM-003
  type: red_flag_for
  description: опасный вариант одышки
- target: DIAG-EMERGENCY-003
  type: red_flag_for
  description: может указывать на дыхательную недостаточность
- target: DIAG-DIFDIAG-003
  type: red_flag_for
  description: учитывается в дифференциальной диагностике одышки
- target: DIAG-DISEASE-003
  type: red_flag_for
  description: перенесено из поля related (схема v1)
- target: DIAG-DISEASE-004
  type: red_flag_for
  description: перенесено из поля related (схема v1)
sources:
- Клинические рекомендации по внебольничной пневмонии у взрослых, действующая редакция.
- GINA Global Strategy for Asthma Management and Prevention, действующая редакция.
- Руководства по пульмонологии и внутренним болезням.
- Техническое задание к БЗ MedAssist, раздел 3.1.
clinical_guidelines:
- Клинические рекомендации по неотложным состояниям в пульмонологии
last_medical_review: '2026-04-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.0'
date_created: '2026-04-30'
date_updated: '2026-09-16'
status: medical_review
disclaimer: true
# Машиночитаемый слой (schema v2) не заполнен. Для status: approved требуются поля: triggers, indicates. См. docs/schema.md, раздел «redflag».
---

# Выраженная одышка и цианоз

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Неотложные состояния требуют немедленной клинической оценки и передачи управления к утверждённым алгоритмам помощи.

## Определение
Выраженная одышка и цианоз — сочетание затруднённого дыхания с синюшной окраской губ, кожи или слизистых, указывающее на возможное нарушение оксигенации.

## Клиническое значение
Красный флаг отражает риск острой дыхательной недостаточности, тяжёлой бронхообструкции, пневмонии тяжёлого течения, ТЭЛА, пневмоторакса, сердечной недостаточности или другого опасного состояния.

## Когда возникает
- при тяжёлой пневмонии;
- при тяжёлом приступе бронхиальной астмы;
- при острой дыхательной недостаточности;
- при кардиальных и сосудистых причинах одышки.

## Возможные ассоциированные состояния
- [[DIAG-EMERGENCY-003]] Острая дыхательная недостаточность.
- [[DIAG-DISEASE-003]] Пневмония.
- [[DIAG-DISEASE-004]] Бронхиальная астма.

## Необходимые действия
- срочная оценка жизненных показателей;
- оценка дыхания, сознания, цвета кожных покровов;
- пульсоксиметрия при наличии;
- вызов экстренной помощи или срочная маршрутизация по клинической ситуации.

## Срочность
Уровень срочности: **emergency**.

## Связанные обследования
- [[DIAG-EXAM-004]] Рентгенография органов грудной клетки.
- [[DIAG-EXAM-002]] Электрокардиография при подозрении на кардиальную причину.

## Связанные документы
- [[DIAG-SYMPTOM-003]] — одышка.
- [[DIAG-EMERGENCY-003]] — острая дыхательная недостаточность.
- [[DIAG-DIFDIAG-003]] — дифференциальная диагностика одышки.

---
id: DIAG-EMERGENCY-003
schema_version: 2
title: Острая дыхательная недостаточность
domain: diag
category: emergency
body_system:
- respiratory
- cardiovascular
- multisystem
tags:
- emergency
- respiratory_failure
- dyspnea
- cyanosis
urgency: emergency
access_level: professional
target_specialist:
- pulmonologist
- emergency_physician
- icu
- therapist
age_group:
- adult
- elderly
- all_ages
evidence_level: IIa
recommendation_class: I
relations:
- target: DIAG-SYMPTOM-003
  type: has_symptom
  description: выраженная одышка является ключевым проявлением
- target: DIAG-REDFLAG-003
  type: has_red_flag
  description: цианоз и тяжёлая одышка являются красным флагом
- target: DIAG-EXAM-004
  type: diagnosed_by
  description: помогает искать лёгочную причину
- target: DIAG-DISEASE-003
  type: complicates
  description: перенесено из поля related (схема v1)
- target: DIAG-DISEASE-004
  type: complicates
  description: перенесено из поля related (схема v1)
- target: DIAG-DIFDIAG-003
  type: considered_in
  description: перенесено из поля related (схема v1)
- target: DIAG-EXAM-010
  type: diagnosed_by
  description: выявление гипоксемии
criteria:
  any:
  - param: spo2
    op: <
    value: 90
  - param: rr
    op: '>='
    value: 30
  - redflag: DIAG-REDFLAG-003
  - exam_result: DIAG-EXAM-010
    value: severe_hypoxemia
time_critical: true
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

# Острая дыхательная недостаточность

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Неотложные состояния требуют немедленной клинической оценки и передачи управления к утверждённым алгоритмам помощи.

## Определение
Острая дыхательная недостаточность — состояние, при котором дыхательная система не обеспечивает адекватный газообмен, что приводит к гипоксемии и/или гиперкапнии.

## Клиническая картина
### Основные проявления
- выраженная [[DIAG-SYMPTOM-003]] одышка;
- учащённое или затруднённое дыхание;
- цианоз;
- тревога, возбуждение или угнетение сознания;
- участие вспомогательной мускулатуры в дыхании.

### Данные осмотра
- изменение частоты дыхания;
- снижение сатурации при наличии пульсоксиметрии;
- патологические дыхательные шумы;
- признаки истощения дыхательных усилий.

## Диагностические критерии
Подозрение формируется при сочетании выраженной дыхательной симптоматики, признаков гипоксии и ухудшения общего состояния. Окончательная оценка требует клинического осмотра и инструментально-лабораторных данных.

## Ключевые обследования
- оценка дыхания, сознания и гемодинамики;
- пульсоксиметрия при наличии;
- [[DIAG-EXAM-004]] рентгенография органов грудной клетки по показаниям;
- [[DIAG-EXAM-002]] ЭКГ при подозрении на кардиальную причину.

## 🚩 Признаки критического течения
- цианоз;
- спутанность сознания;
- невозможность говорить;
- признаки истощения дыхания;
- быстрое ухудшение.

## Дифференциальная диагностика
Проводится с тяжёлой пневмонией, приступом бронхиальной астмы, ТЭЛА, пневмотораксом, сердечной недостаточностью и другими причинами острой одышки.

## Тактическая значимость
Состояние требует срочной оценки и маршрутизации по алгоритмам неотложной помощи.

## Информация для пациента
При выраженной одышке, посинении губ, нарушении сознания или невозможности говорить необходимо срочно вызвать скорую помощь.

## Связанные документы
- [[DIAG-SYMPTOM-003]] — одышка.
- [[DIAG-REDFLAG-003]] — выраженная одышка и цианоз.
- [[DIAG-DISEASE-003]] — пневмония.
- [[DIAG-DISEASE-004]] — бронхиальная астма.
- [[DIAG-DIFDIAG-003]] — дифференциальная диагностика одышки.

## Источники
1. Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
2. Global Initiative for Asthma. Global Strategy for Asthma Management and Prevention, 2025 update.

---
id: DIAG-DISEASE-004
schema_version: 2
title: Бронхиальная астма
domain: diag
category: disease
icd_10: J45
body_system:
- respiratory
tags:
- asthma
- respiratory
- dyspnea
- wheezing
- chronic
urgency: routine
access_level: professional
target_specialist:
- therapist
- pulmonologist
- allergist
age_group:
- adult
- child
- adolescent
- all_ages
evidence_level: IIa
recommendation_class: I
relations:
- target: DIAG-SYMPTOM-003
  type: has_symptom
  description: одышка является одним из типичных проявлений
- target: DIAG-DIFDIAG-003
  type: considered_in
  description: требуется отличать от других причин одышки
- target: DIAG-REDFLAG-003
  type: has_red_flag
  description: тяжёлый приступ может сопровождаться дыхательной недостаточностью
- target: DIAG-EXAM-010
  type: diagnosed_by
  description: оценка тяжести обострения
- target: DIAG-DISEASE-003
  type: differentiates_from
  description: одышка и кашель при инфекционном процессе
- target: DIAG-SYMPTOM-008
  type: has_symptom
  description: выведено из машиночитаемого слоя (presentation)
presentation:
- symptom: DIAG-SYMPTOM-009
  weight: 3
  frequency: very_common
  features:
  - wheezing.expiratory
  - wheezing.diffuse
  - wheezing.after_trigger
- symptom: DIAG-SYMPTOM-003
  weight: 3
  frequency: very_common
  features:
  - dyspnea.episodic
  - dyspnea.nocturnal_attacks
- symptom: DIAG-SYMPTOM-008
  weight: 2
  frequency: common
  features:
  - cough.dry
  - cough.nocturnal
red_flags:
- DIAG-REDFLAG-006
- DIAG-REDFLAG-003
exams:
- exam: DIAG-EXAM-008
  role: confirms
  expected: reversible_obstruction
- exam: DIAG-EXAM-010
  role: stratifies
  expected: SpO₂ менее 92 % — тяжёлое обострение
differentials:
- DIAG-DISEASE-003
applies_when:
  not:
    profile: GLB-PROFILE-004
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

# Бронхиальная астма

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не является руководством по самолечению и не заменяет клиническое решение врача.

## Определение
Бронхиальная астма — хроническое воспалительное заболевание дыхательных путей, проявляющееся вариабельными респираторными симптомами и обратимой бронхиальной обструкцией. МКБ-10: J45.

## Эпидемиология
- встречается у детей и взрослых;
- течение может быть интермиттирующим или персистирующим;
- выраженность симптомов зависит от триггеров, контроля заболевания и сопутствующих факторов.

## Этиология и патогенез
В основе лежит хроническое воспаление дыхательных путей, гиперреактивность бронхов и бронхоконстрикция. Симптомы могут провоцироваться аллергенами, физической нагрузкой, инфекциями, холодным воздухом, дымом и раздражающими веществами.

## Клиническая картина
- приступы [[DIAG-SYMPTOM-003]] одышки;
- свистящее дыхание;
- чувство стеснения в груди;
- кашель, особенно ночью или ранним утром;
- вариабельность симптомов во времени.

## 🚩 «Красные флаги»
- одышка в покое, невозможность говорить фразами;
- выраженная слабость, сонливость, спутанность сознания;
- цианоз;
- отсутствие эффекта от обычной помощи;
- признаки дыхательной недостаточности.

## Диагностика
- сбор анамнеза, выявление вариабельности симптомов и триггеров;
- оценка функции внешнего дыхания по назначению врача;
- оценка аллергологического анамнеза;
- исключение других причин одышки.

## Дифференциальная диагностика
Проводится с ХОБЛ, пневмонией, сердечной недостаточностью, тревожными расстройствами, ТЭЛА и другими причинами одышки.

## Лечение (обзор)
В базе знаний лечение описывается только как справочный контекст. Конкретные препараты, дозы и ступень терапии выбирает врач на основе клинических рекомендаций и контроля заболевания.

## Прогноз
При контролируемом течении возможно сохранение нормальной активности. Неконтролируемая астма повышает риск обострений и неотложных состояний.

## Профилактика
- контроль триггеров;
- обучение пациента правильной технике ингаляции;
- регулярная оценка контроля заболевания;
- план действий при ухудшении по назначению врача.

## Информация для пациента
При выраженной одышке, посинении губ, невозможности говорить или резком ухудшении состояния нужно срочно обращаться за медицинской помощью.

## Связанные документы
- [[DIAG-SYMPTOM-003]] — одышка.
- [[DIAG-DIFDIAG-003]] — дифференциальная диагностика одышки.
- [[DIAG-REDFLAG-003]] — выраженная одышка и цианоз.

## Источники
1. Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
2. Global Initiative for Asthma. Global Strategy for Asthma Management and Prevention, 2025 update.

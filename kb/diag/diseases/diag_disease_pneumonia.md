---
id: DIAG-DISEASE-003
schema_version: 2
title: Пневмония
domain: diag
category: disease
icd_10: J12-J18
body_system:
- respiratory
tags:
- pneumonia
- respiratory
- infection
- fever
- dyspnea
urgency: urgent
access_level: professional
target_specialist:
- therapist
- pulmonologist
- emergency_physician
age_group:
- adult
- elderly
- all_ages
evidence_level: IIa
recommendation_class: I
relations:
- target: DIAG-SYMPTOM-003
  type: has_symptom
  description: одышка может быть проявлением пневмонии
- target: DIAG-SYMPTOM-004
  type: has_symptom
  description: лихорадка является частым инфекционным проявлением
- target: DIAG-EXAM-003
  type: diagnosed_by
  description: ОАК помогает оценить воспалительную реакцию
- target: DIAG-EXAM-004
  type: diagnosed_by
  description: рентгенография помогает выявить инфильтративные изменения
- target: DIAG-DIFDIAG-003
  type: considered_in
  description: перенесено из поля related (схема v1)
- target: DIAG-REDFLAG-003
  type: has_red_flag
  description: перенесено из поля related (схема v1)
- target: DIAG-EXAM-010
  type: diagnosed_by
  description: оценка тяжести по сатурации
- target: DIAG-SYMPTOM-002
  type: has_symptom
  description: выведено из машиночитаемого слоя (presentation)
presentation:
- symptom: DIAG-SYMPTOM-008
  weight: 3
  frequency: very_common
  features:
  - cough.productive
  - cough.purulent_sputum
  - cough.acute
- symptom: DIAG-SYMPTOM-004
  weight: 3
  frequency: very_common
  features:
  - fever.chills
  - fever.acute
- symptom: DIAG-SYMPTOM-003
  weight: 2
  frequency: common
  features:
  - dyspnea.progressive
- symptom: DIAG-SYMPTOM-002
  weight: 1
  frequency: uncommon
  features:
  - chest_pain.pleuritic
red_flags:
- DIAG-REDFLAG-003
exams:
- exam: DIAG-EXAM-004
  role: confirms
  expected: infiltrate
- exam: DIAG-EXAM-003
  role: supports
  expected: leukocytosis
- exam: DIAG-EXAM-010
  role: stratifies
  expected: SpO₂ менее 93 % — тяжёлое течение
differentials:
- DIAG-DISEASE-004
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

# Пневмония

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не является руководством по самолечению и не заменяет клиническое решение врача.

## Определение
Пневмония — острое инфекционно-воспалительное заболевание лёгочной ткани, обычно сопровождающееся респираторными симптомами и признаками воспалительной реакции. МКБ-10: J12–J18.

## Эпидемиология
- **Распространённость**: частая причина обращений за медицинской помощью и госпитализаций среди инфекций нижних дыхательных путей.
- **Группы риска**: пожилые пациенты, лица с хроническими заболеваниями, иммунокомпрометированные пациенты.
- **Факторы риска**: возраст, курение, ХОБЛ, сердечно-сосудистые заболевания, нарушение глотания, иммунодефицит.

## Этиология и патогенез
Пневмония развивается при проникновении инфекционного агента в нижние дыхательные пути и формировании воспалительного процесса в альвеолярной ткани. Клиническая картина зависит от возбудителя, возраста пациента, иммунного статуса и сопутствующих заболеваний.

## Классификация
- внебольничная;
- госпитальная;
- аспирационная;
- у иммунокомпрометированных пациентов.

## Клиническая картина
### Основные проявления
- кашель;
- [[DIAG-SYMPTOM-004]] лихорадка;
- [[DIAG-SYMPTOM-003]] одышка;
- боль в груди при дыхании;
- слабость, потливость.

### Данные осмотра
- учащение дыхания;
- локальные хрипы или ослабление дыхания;
- признаки гипоксемии при тяжёлом течении.

## 🚩 «Красные флаги»
- выраженная одышка, цианоз, спутанность сознания;
- низкое артериальное давление;
- быстрое ухудшение состояния;
- пожилой возраст и выраженная коморбидность.

## Диагностика
- клиническая оценка жалоб и осмотра;
- [[DIAG-EXAM-003]] общий анализ крови;
- [[DIAG-EXAM-004]] рентгенография органов грудной клетки;
- дополнительные лабораторные и микробиологические исследования по показаниям.

## Дифференциальная диагностика
Проводится с бронхитом, бронхиальной астмой, ТЭЛА, сердечной недостаточностью, туберкулёзом и другими причинами кашля, лихорадки и одышки.

## Лечение (обзор)
В БЗ MedAssist данный раздел носит обзорный характер. Выбор терапии, необходимость антибактериального лечения, место лечения и объём обследования определяет врач с учётом тяжести состояния и клинических рекомендаций.

## Прогноз
Зависит от возраста, сопутствующих заболеваний, тяжести состояния и своевременности медицинской помощи.

## Профилактика
- вакцинация по показаниям;
- отказ от курения;
- контроль хронических заболеваний;
- своевременное обращение при ухудшении состояния.

## Информация для пациента
При высокой температуре, одышке, боли в груди, спутанности сознания или выраженной слабости необходимо обратиться за медицинской помощью.

## Связанные документы
- [[DIAG-SYMPTOM-003]] — одышка.
- [[DIAG-SYMPTOM-004]] — лихорадка.
- [[DIAG-EXAM-003]] — общий анализ крови.
- [[DIAG-EXAM-004]] — рентгенография органов грудной клетки.

## Источники
1. Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
2. Global Initiative for Asthma. Global Strategy for Asthma Management and Prevention, 2025 update.

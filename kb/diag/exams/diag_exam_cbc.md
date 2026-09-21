---
id: DIAG-EXAM-003
schema_version: 2
title: Общий анализ крови
domain: diag
category: exam
body_system:
- hematologic
- multisystem
tags:
- cbc
- exam
- blood_test
- infection
- inflammation
urgency: routine
access_level: professional
target_specialist:
- therapist
- pulmonologist
- gastroenterologist
- emergency_physician
- nursing
age_group:
- adult
- elderly
- all_ages
recommendation_class: I
relations:
- target: DIAG-SYMPTOM-004
  type: diagnoses
  description: используется при лихорадке для оценки воспалительной реакции
- target: DIAG-DISEASE-003
  type: diagnoses
  description: помогает оценить инфекционно-воспалительные изменения
- target: DIAG-SYMPTOM-005
  type: diagnoses
  description: может использоваться при боли в животе для оценки воспаления
results:
- value: normal
  label: показатели в пределах референсных значений
- value: leukocytosis
  label: лейкоцитоз
  indicates:
  - DIAG-DISEASE-003
- value: leukopenia
  label: лейкопения
- value: anemia
  label: анемия
- value: thrombocytopenia
  label: тромбоцитопения
turnaround: 1–2 часа
sources:
- Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
- Metlay J.P. et al. Diagnosis and Treatment of Adults with Community-acquired Pneumonia. An Official Clinical Practice Guideline of the ATS and IDSA. Am J Respir Crit Care Med. 2019;200(7):e45–e67.
clinical_guidelines:
- КР «Внебольничная пневмония у взрослых», Минздрав РФ, 2024
- ATS/IDSA Community-acquired Pneumonia Guideline, 2019
last_medical_review: '2026-04-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.1'
date_created: '2026-04-30'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Общий анализ крови

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не является руководством по самолечению и не заменяет клиническое решение врача.

## Определение
Общий анализ крови (ОАК) — базовое лабораторное исследование, оценивающее клеточный состав крови и некоторые косвенные признаки воспаления, анемии, инфекции и других состояний.

## Назначение метода
ОАК используется как скрининговое и уточняющее исследование при широком спектре симптомов: лихорадке, слабости, одышке, боли, подозрении на инфекционный или воспалительный процесс.

## Показания
- [[DIAG-SYMPTOM-004]] лихорадка;
- подозрение на [[DIAG-DISEASE-003]] пневмонию;
- боль в животе при подозрении на воспалительный процесс;
- слабость, бледность, признаки анемии;
- контроль динамики по назначению врача.

## Диагностическая роль
ОАК не устанавливает диагноз самостоятельно, но помогает оценить выраженность воспалительной реакции, наличие анемии, тромбоцитопении, лейкоцитоза или лейкопении и определить необходимость дальнейшего обследования.

## Интерпретация результатов
| Результат / находка | Возможное значение |
|---|---|
| Лейкоцитоз | Возможный инфекционный или воспалительный процесс |
| Лейкопения | Возможна вирусная инфекция, лекарственное влияние или другие причины |
| Анемия | Возможная кровопотеря, дефицитные состояния или хроническое заболевание |
| Тромбоцитопения/тромбоцитоз | Требует интерпретации в клиническом контексте |

## Ограничения
Изменения в ОАК неспецифичны и требуют сопоставления с симптомами, осмотром и другими обследованиями.

## Связанные документы
- [[DIAG-SYMPTOM-004]] — лихорадка.
- [[DIAG-DISEASE-003]] — пневмония.
- [[DIAG-SYMPTOM-005]] — боль в животе.

## Источники
1. Клинические рекомендации «Внебольничная пневмония у взрослых». Минздрав РФ, 2024.
2. Metlay J.P. et al. Diagnosis and Treatment of Adults with Community-acquired Pneumonia. An Official Clinical Practice Guideline of the ATS and IDSA. Am J Respir Crit Care Med. 2019;200(7):e45–e67.

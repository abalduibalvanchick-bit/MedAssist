---
id: DIAG-SYMPTOM-015
schema_version: 2
title: Нарушение зрения
domain: diag
category: symptom
icd_10: H53
body_system:
- nervous
tags:
- vision
- aura
- symptom
urgency: urgent
access_level: professional
target_specialist:
- therapist
- neurologist
- ophthalmologist
age_group:
- adult
- elderly
synonyms:
- нарушение зрения
- пелена перед глазами
- мушки перед глазами
- двоится в глазах
- ослеп на один глаз
- мерцание перед глазами
- затуманенное зрение
- зигзаги перед глазами
relations:
- target: DIAG-DISEASE-005
  type: symptom_of
  description: зрительная аура при мигрени
- target: DIAG-EMERGENCY-002
  type: symptom_of
  description: внезапная потеря зрения или двоение при инсульте
- target: DIAG-DISEASE-001
  type: symptom_of
  description: нарушение зрения при гипертоническом кризе
- target: DIAG-DISEASE-006
  type: symptom_of
  description: затуманивание зрения при гипергликемии
- target: DIAG-EXAM-009
  type: diagnosed_by
  description: выявление сопутствующей очаговой симптоматики
features:
- code: visual_disturbance.aura
  label: мерцающие зигзаги или пятна, проходят за 5–60 минут
- code: visual_disturbance.sudden_loss
  label: внезапная потеря зрения на один или оба глаза
- code: visual_disturbance.diplopia
  label: двоение
- code: visual_disturbance.blurred
  label: затуманивание, пелена
sources:
- Headache Classification Committee of the International Headache Society. The International Classification of Headache Disorders, 3rd edition (ICHD-3). Cephalalgia. 2018;38:1–211.
- 'Powers W.J. et al. Guidelines for the Early Management of Patients With Acute Ischemic Stroke: 2019 Update. Stroke. 2019;50:e344–e418.'
clinical_guidelines:
- ICHD-3, 2018
- AHA/ASA Early Management of Acute Ischemic Stroke, 2019
last_medical_review: '2026-09-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.0'
date_created: '2026-09-30'
date_updated: '2026-09-30'
status: approved
disclaimer: true
---

# Нарушение зрения

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не заменяет консультацию врача.

## Определение
Жалоба на остро или постепенно возникшее ухудшение зрения, появление зрительных феноменов или двоения.

## Механизм
Преходящая дисфункция зрительной коры при мигренозной ауре; ишемия сетчатки, зрительных путей или ствола мозга при сосудистых событиях; отёк диска зрительного нерва и ретинопатия при гипертоническом кризе; изменение преломления хрусталика при гипергликемии.

## Характеристики
- **Начало**: внезапное или постепенное.
- **Тип**: мерцающие зигзаги, потеря поля зрения, двоение, пелена.
- **Длительность**: минуты (аура, транзиторная ишемия) или стойкое.
- **Сопутствующие проявления**: головная боль, очаговые неврологические симптомы, высокое АД.

## Клиническое значение
Мерцающие зигзаги, развивающиеся постепенно и проходящие за 5–60 минут с последующей головной болью, характерны для мигрени с аурой. Внезапная потеря зрения или двоение — экстренное состояние (инсульт, транзиторная ишемическая атака, окклюзия артерии сетчатки).

## Ассоциированные заболевания
- [[DIAG-DISEASE-005]] Мигрень
- [[DIAG-EMERGENCY-002]] Острое нарушение мозгового кровообращения
- [[DIAG-DISEASE-001]] Артериальная гипертензия
- [[DIAG-DISEASE-006]] Сахарный диабет 2 типа

## 🚩 «Красные флаги»
- внезапная потеря зрения;
- двоение;
- нарушение зрения при АД 180/120 мм рт. ст. и выше;
- впервые возникшая аура после 40 лет.

## Дифференциально-диагностические критерии
Постепенное распространение позитивных феноменов (мерцание) — аура; внезапное выпадение (негативные феномены) — ишемия.

## Диагностические направления
Измерение АД, неврологический осмотр; при внезапной потере зрения — экстренная нейровизуализация и осмотр офтальмолога.

## Особенности у отдельных групп
У пациентов с диабетом — ежегодный осмотр глазного дна.

## Информация для пациента
Если зрение пропало внезапно или появилось двоение — вызовите скорую помощь.

## Связанные документы
- [[DIAG-DISEASE-005]] Мигрень — зрительная аура при мигрени
- [[DIAG-EMERGENCY-002]] Острое нарушение мозгового кровообращения — внезапная потеря зрения или двоение при инсульте
- [[DIAG-DISEASE-001]] Артериальная гипертензия — нарушение зрения при гипертоническом кризе
- [[DIAG-DISEASE-006]] Сахарный диабет 2 типа — затуманивание зрения при гипергликемии
- [[DIAG-EXAM-009]] Неврологический осмотр — выявление сопутствующей очаговой симптоматики

## Источники
1. Headache Classification Committee of the International Headache Society. The International Classification of Headache Disorders, 3rd edition (ICHD-3). Cephalalgia. 2018;38:1–211.
2. Powers W.J. et al. Guidelines for the Early Management of Patients With Acute Ischemic Stroke: 2019 Update. Stroke. 2019;50:e344–e418.

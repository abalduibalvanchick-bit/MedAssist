---
id: DIAG-SYMPTOM-012
schema_version: 2
title: Сердцебиение
domain: diag
category: symptom
icd_10: R00.2
body_system:
- cardiovascular
tags:
- palpitations
- arrhythmia
- symptom
urgency: urgent
access_level: professional
target_specialist:
- therapist
- cardiologist
age_group:
- adult
- elderly
synonyms:
- сердцебиение
- сердце колотится
- перебои в сердце
- сердце выпрыгивает
- учащённое сердцебиение
- аритмия
- сердце замирает
relations:
- target: DIAG-DISEASE-002
  type: symptom_of
  description: нарушения ритма при ишемической болезни сердца
- target: DIAG-DISEASE-001
  type: symptom_of
  description: тахикардия и нарушения ритма при АГ
- target: DIAG-EXAM-002
  type: diagnosed_by
  description: регистрация ритма
- target: DIAG-EXAM-013
  type: diagnosed_by
  description: исключение нарушений калиевого обмена
features:
- code: palpitations.irregular
  label: нерегулярный ритм, перебои
- code: palpitations.sudden_onset
  label: внезапное начало и окончание приступа
- code: palpitations.with_syncope
  label: с обмороком или предобморочным состоянием
- code: palpitations.exertional
  label: возникает при физической нагрузке
sources:
- 'Raviele A. et al. Management of patients with palpitations: a position paper from the European Heart Rhythm Association. Europace. 2011;13:920–934.'
- Brugada J. et al. 2019 ESC Guidelines for the management of patients with supraventricular tachycardia. Eur Heart J. 2020;41:655–720.
clinical_guidelines:
- 2019 ESC Guidelines for the management of patients with supraventricular tachycardia
last_medical_review: '2026-09-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.0'
date_created: '2026-09-30'
date_updated: '2026-09-30'
status: approved
disclaimer: true
---

# Сердцебиение

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не заменяет консультацию врача.

## Определение
Ощущение собственного сердцебиения: учащённого, усиленного или нерегулярного.

## Механизм
Тахиаритмии, экстрасистолия, синусовая тахикардия при лихорадке, анемии, гипогликемии, тиреотоксикозе; действие препаратов (β2-агонисты), кофеин, тревога.

## Характеристики
- **Ритм**: регулярный или нерегулярный.
- **Начало**: постепенное или внезапное.
- **Провокация**: нагрузка, покой, ингаляции бронхолитиков.
- **Сопутствующие проявления**: боль в груди, одышка, головокружение, обморок.

## Клиническое значение
Сердцебиение с обмороком, болью в груди или одышкой — признак гемодинамически значимой аритмии и требует экстренной оценки. Изолированные кратковременные эпизоды у молодых без заболеваний сердца обычно доброкачественны.

## Ассоциированные заболевания
- [[DIAG-DISEASE-002]] Ишемическая болезнь сердца
- [[DIAG-DISEASE-001]] Артериальная гипертензия

## 🚩 «Красные флаги»
- сердцебиение с обмороком или предобмороком;
- сердцебиение с болью в груди или одышкой;
- возникновение при нагрузке;
- внезапная смерть родственников в молодом возрасте.

## Дифференциально-диагностические критерии
Нерегулярный ритм — фибрилляция предсердий или экстрасистолия; внезапное начало и окончание — пароксизмальная тахикардия; постепенное нарастание — синусовая тахикардия.

## Диагностические направления
ЭКГ во время симптомов, калий сыворотки; суточное мониторирование ЭКГ — в плановом порядке.

## Особенности у отдельных групп
У пациентов с астмой — учитывать связь с ингаляциями β2-агонистов.

## Информация для пациента
Если сердцебиение сопровождается потерей сознания, болью в груди или нехваткой воздуха — вызовите скорую помощь.

## Связанные документы
- [[DIAG-DISEASE-002]] Ишемическая болезнь сердца — нарушения ритма при ишемической болезни сердца
- [[DIAG-DISEASE-001]] Артериальная гипертензия — тахикардия и нарушения ритма при АГ
- [[DIAG-EXAM-002]] Электрокардиография — регистрация ритма
- [[DIAG-EXAM-013]] Калий сыворотки — исключение нарушений калиевого обмена

## Источники
1. Raviele A. et al. Management of patients with palpitations: a position paper from the European Heart Rhythm Association. Europace. 2011;13:920–934.
2. Brugada J. et al. 2019 ESC Guidelines for the management of patients with supraventricular tachycardia. Eur Heart J. 2020;41:655–720.

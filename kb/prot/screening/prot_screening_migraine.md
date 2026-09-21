---
id: PROT-SCREENING-006
schema_version: 2
title: 'Скрининг: Выявление пациентов с мигренью'
domain: prot
category: screening
body_system:
- nervous
tags:
- screening
- migraine
- headache
urgency: routine
access_level: professional
target_specialist:
- therapist
- general_practitioner
age_group:
- adult
relations:
- target: DIAG-DISEASE-005
  type: screening_for
  description: Скрининг на мигрень среди пациентов с головной болью.
- target: PROT-PROTOCOL-006
  type: screening_for
  description: При подозрении – дообследование.
- target: PROT-ROUTING-006
  type: next_step
  description: Направление к неврологу при положительном скрининге.
- target: DIAG-EXAM-009
  type: uses_exam
  description: выведено из машиночитаемого слоя (methods)
target:
  feature: headache.recurrent_attacks
methods:
- DIAG-EXAM-009
interval: при обращении с повторяющейся головной болью
positive_when:
  at_least:
    n: 2
    of:
    - feature: headache.photophobia
    - feature: headache.nausea
    - feature: headache.worse_with_activity
on_positive: PROT-PROTOCOL-006
sources:
- AHS Guidelines for Migraine
- 'Lipton R.B. et al. A self-administered screener for migraine in primary care: the ID Migraine validation study. Neurology. 2003;61:375–382.'
clinical_guidelines:
- AHS Migraine Guidelines
last_medical_review: '2026-05-06'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.1'
date_created: '2026-05-02'
date_updated: '2026-09-16'
status: medical_review
disclaimer: true
---

# Скрининг: Выявление пациентов с мигренью

> Документ описывает алгоритм первичного выявления лиц с вероятной мигренью.

## Целевая группа
- Пациенты с рецидивирующей головной болью (длительность ≥3 месяцев).
- Жалобы на пульсирующую, одностороннюю боль, со свето- и звукобоязнью.

## Показания к скринингу
- Обращение по поводу головной боли (особенно с тошнотой/рвотой).
- Частые пропуски работы/учебы из-за головной боли.

## Методы скрининга
- Опросник ID-Migraine (3 вопроса):  
  1. Беспокоили ли вас за последние 3 месяца головные боли, которые ограничивали активность?  
  2. Были ли у вас тошнота или боль в животе?  
  3. Беспокоила ли вас светобоязнь во время головной боли?  
  – При ≥2 ответов "да" – высокая вероятность мигрени (чувствительность 90%).
- Визуальная аналоговая шкала (ВБШ) для оценки тяжести.

## Интерпретация
- **ID-Migraine ≥2** и отсутствие "красных флагов" → предположительная мигрень → направить к неврологу для уточнения диагноза (PROT-ROUTING-006).
- **Подозрение на вторичную головную боль** (острое начало, неврологический дефицит, лихорадка) → экстренная маршрутизация.

## Дальнейшие действия
- При подтверждении мигрени → ведение по PROT-PROTOCOL-006.
- При отсутствии критериев мигрени → дифференциальный диагноз (головная боль напряжения, кластерная головная боль, вторичные причины).

## Ограничения
- Скрининг не заменяет полноценную диагностику.
- Не適用 при красных флагах.

## Источники
1. AHS Guidelines for Migraine.
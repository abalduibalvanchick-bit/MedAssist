---
id: PROT-PROTOCOL-001
schema_version: 2
title: 'Клинический протокол: Артериальная гипертензия'
domain: prot
category: protocol
body_system:
- cardiovascular
tags:
- protocol
- hypertension
urgency: routine
access_level: professional
target_specialist:
- therapist
- cardiologist
age_group:
- adult
evidence_level: IIa
recommendation_class: I
relations:
- target: DIAG-DISEASE-001
  type: protocol_for
  description: Клинический протокол предназначен для ведения пациента с артериальной гипертензией.
- target: PHARM-REGIMEN-001
  type: recommends
  description: Протокол использует терапевтическую схему из фармакологического контура.
- target: PROT-SCALE-001
  type: assessed_by
  description: Протокол использует шкалу сердечно-сосудистого риска.
- target: PROT-ROUTING-001
  type: has_routing
  description: Протокол связан с маршрутизацией пациента.
- target: PROT-EMERGENCY_P-001
  type: has_emergency_protocol
  description: При осложнённом течении выполняется переход к алгоритму неотложной помощи.
- target: PROT-PATIENT_INFO-001
  type: has_patient_info
  description: К протоколу привязана пациентская памятка.
- target: PROT-FOLLOW_UP-001
  type: has_follow_up
  description: Протокол связан с дальнейшим наблюдением пациента.
- target: PROT-CHECKLIST-001
  type: has_checklist
  description: Протокол поддерживается чек-листом первичного приёма.
- target: PROT-SCREENING-001
  type: has_screening
  description: Протокол связан со скринингом артериальной гипертензии.
for:
- DIAG-DISEASE-001
entry:
  any:
  - disease: DIAG-DISEASE-001
  - fact: known_hypertension
  - param: sbp
    op: '>='
    value: 140
  - param: dbp
    op: '>='
    value: 90
steps:
- id: confirm
  action: подтвердить диагноз повторными офисными измерениями, СМАД или домашним мониторированием АД
  refs:
  - DIAG-EXAM-001
- id: risk
  action: оценить сердечно-сосудистый риск
  refs:
  - PROT-SCALE-001
- id: target_organs
  action: 'обследовать органы-мишени: ЭКГ, креатинин и СКФ, альбуминурия, глюкоза, липиды'
  refs:
  - DIAG-EXAM-002
  - DIAG-EXAM-005
- id: lifestyle
  action: 'модификация образа жизни: соль менее 5 г/сут, диета DASH, физическая активность, отказ от курения'
  refs:
  - PHARM-NONPHARM-001
- id: therapy
  action: начать антигипертензивную терапию, предпочтительно фиксированной комбинацией иАПФ или БРА с БКК или диуретиком
  when:
    any:
    - param: sbp
      op: '>='
      value: 140
    - param: dbp
      op: '>='
      value: 90
  refs:
  - PHARM-REGIMEN-001
- id: follow_up
  action: оценить эффект через 1–3 месяца
  refs:
  - PROT-FOLLOW_UP-001
branches:
- when:
    redflag: DIAG-REDFLAG-001
  then: PROT-EMERGENCY_P-001
  explanation: осложнённый гипертонический криз
- when:
    profile: GLB-PROFILE-002
  then: PROT-ROUTING-001
  explanation: при беременности иАПФ и БРА противопоказаны, ведение совместно с акушером-гинекологом
- when:
    scale_category: PROT-SCALE-001
    value: high
  then: PROT-ROUTING-001
  explanation: высокий сердечно-сосудистый риск
targets:
- param: sbp
  op: <
  value: 130
  label: целевое САД менее 130 мм рт. ст. у большинства пациентов при хорошей переносимости
- param: dbp
  op: <
  value: 80
  label: целевое ДАД менее 80 мм рт. ст.
sources:
- Клинические рекомендации «Артериальная гипертензия у взрослых». Минздрав РФ, 2024.
- Mancia G. et al. 2023 ESH Guidelines for the management of arterial hypertension. J Hypertens. 2023;41:1874–2071.
clinical_guidelines:
- КР «Артериальная гипертензия у взрослых», Минздрав РФ, 2024
- 2023 ESH Guidelines for the management of arterial hypertension
last_medical_review: '2026-04-09'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.1'
date_created: '2026-04-09'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Клинический протокол: Артериальная гипертензия

> ⚕️ Документ предназначен для медицинских специалистов.

## Назначение протокола
Описание алгоритма ведения пациента с артериальной гипертензией на амбулаторном этапе.  
Используется шкала оценки риска: [[PROT-SCALE-001]]

## Область применения
- Артериальная гипертензия
- Взрослые пациенты
- Амбулаторная практика

## Входные условия
- [[DIAG-DISEASE-001]]
- Повышенное артериальное давление
- Подтверждение при повторных измерениях

## Критерии начала применения
- САД ≥ 140 мм рт. ст.
- и/или ДАД ≥ 90 мм рт. ст.

## Алгоритм ведения пациента
1. Подтвердить диагноз повторными измерениями артериального давления.
2. Оценить факторы риска и наличие поражения органов-мишеней.
3. Определить степень сердечно-сосудистого риска.
4. Выбрать немедикаментозную и/или медикаментозную тактику.
5. Организовать дальнейшее наблюдение пациента.

## Ключевые решения и развилки
- Низкий риск → немедикаментозная терапия и наблюдение.
- Средний/высокий риск → медикаментозная терапия.
- Тяжёлое состояние или признаки осложнённого криза → срочная маршрутизация.

## Критерии срочности
- **Routine**: стабильное повышение давления без признаков осложнений.
- **Urgent**: выраженная симптоматика без явных признаков жизнеугрожающего состояния.
- **Emergency**: гипертонический криз.

## Связанные маршруты пациента
- [[PROT-ROUTING-001]]

## Связанные шкалы
- [[PROT-SCALE-001]]

## Неотложные состояния и действия
- [[PROT-EMERGENCY_P-001]]

## Рекомендации по терапии
- [[PHARM-REGIMEN-001]]
- [[PHARM-DRUG-001]]
- [[PHARM-DRUG-002]]

## Памятка пациенту
- [[PROT-PATIENT_INFO-001]]

## Дальнейшее наблюдение
- [[PROT-FOLLOW_UP-001]]

## Особенности у отдельных групп
- Пожилые: осторожное снижение давления.
- Коморбидные пациенты: индивидуализация терапии.

## Ограничения применения
- Не применяется при экстренных состояниях без очной оценки врача.

## Источники
1. Клинические рекомендации «Артериальная гипертензия у взрослых». Минздрав РФ, 2024.
2. Mancia G. et al. 2023 ESH Guidelines for the management of arterial hypertension. J Hypertens. 2023;41:1874–2071.

---
id: PROT-PROTOCOL-003
schema_version: 2
title: 'Клинический протокол: Ишемическая болезнь сердца (хроническая)'
domain: prot
category: protocol
body_system:
- cardiovascular
tags:
- protocol
- ihd
- coronary
urgency: routine
access_level: professional
target_specialist:
- cardiologist
- therapist
age_group:
- adult
- elderly
evidence_level: Ia
recommendation_class: I
relations:
- target: DIAG-DISEASE-002
  type: protocol_for
  description: Протокол для ведения пациентов с хронической ИБС.
- target: PHARM-REGIMEN-003
  type: recommends
  description: Использует схему лечения ИБС.
- target: PROT-SCALE-003
  type: assessed_by
  description: Оценка функционального класса стенокардии, риска.
- target: PROT-ROUTING-003
  type: has_routing
  description: Маршрутизация пациента.
- target: PROT-EMERGENCY_P-003
  type: has_emergency_protocol
  description: При нестабильной стенокардии или ОКС переход к неотложному алгоритму.
- target: PROT-PATIENT_INFO-003
  type: has_patient_info
  description: Памятка пациенту.
- target: PROT-FOLLOW_UP-003
  type: has_follow_up
  description: Дальнейшее наблюдение.
- target: PROT-CHECKLIST-003
  type: has_checklist
  description: Чек-лист первичного приёма.
- target: PROT-SCREENING-003
  type: has_screening
  description: Скрининг ИБС.
for:
- DIAG-DISEASE-002
entry:
  any:
  - disease: DIAG-DISEASE-002
  - fact: known_ihd
  - all:
    - feature: chest_pain.exertional
    - feature: chest_pain.relieved_by_rest
steps:
- id: ecg
  action: ЭКГ в покое
  refs:
  - DIAG-EXAM-002
- id: exclude_acs
  action: при впервые возникшей или прогрессирующей боли исключить ОКС
  when:
    feature: chest_pain.new_onset
  refs:
  - DIAG-EXAM-007
- id: classify
  action: определить функциональный класс стенокардии и риск
  refs:
  - PROT-SCALE-003
- id: prevention
  action: антиагрегант и статин высокой интенсивности
  refs:
  - PHARM-REGIMEN-003
  - PHARM-DRUGCLASS-011
  - PHARM-DRUGCLASS-012
- id: antianginal
  action: антиангинальная терапия, препараты первой линии — β-адреноблокаторы или БКК
  refs:
  - PHARM-DRUGCLASS-020
  - PHARM-DRUGCLASS-003
- id: lifestyle
  action: отказ от курения, физическая реабилитация, контроль факторов риска
  refs:
  - PHARM-NONPHARM-003
- id: follow_up
  action: наблюдение 1 раз в 6–12 месяцев
  refs:
  - PROT-FOLLOW_UP-003
branches:
- when:
    redflag: DIAG-REDFLAG-005
  then: PROT-EMERGENCY_P-003
  explanation: нестабильная стенокардия
- when:
    any:
    - scale_category: PROT-SCALE-003
      value: moderate
    - scale_category: PROT-SCALE-003
      value: high
  then: PROT-ROUTING-003
  explanation: умеренный или высокий риск — консультация кардиолога
targets:
- param: hr
  op: <
  value: 70
  label: ЧСС покоя менее 70 уд/мин на фоне антиангинальной терапии
- param: sbp
  op: <
  value: 130
  label: САД менее 130 мм рт. ст.
sources:
- Клинические рекомендации «Стабильная ишемическая болезнь сердца». Минздрав РФ, 2024.
- Vrints C. et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45:3415–3537.
clinical_guidelines:
- КР «Стабильная ишемическая болезнь сердца», Минздрав РФ, 2024
- 2024 ESC Guidelines for the management of chronic coronary syndromes
last_medical_review: '2026-05-06'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.1'
date_created: '2026-05-02'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Клинический протокол: Ишемическая болезнь сердца (хроническая)

> ⚕️ Документ предназначен для медицинских специалистов.

## Назначение протокола
Ведение пациентов с хронической ишемической болезнью сердца (стабильная стенокардия, постинфарктный кардиосклероз). Обеспечивает диагностику, оценку риска, оптимальную фармакотерапию и реваскуляризацию.

## Область применения
- Хроническая ИБС (CCS)
- Взрослые пациенты
- Амбулаторная и стационарная практика

## Входные условия
- [[DIAG-DISEASE-002]] подтверждённая ИБС (ангиографически, по данным неинвазивной визуализации, типичной стенокардии)
- Стабильное течение (отсутствие изменений симптомов в течение 2–4 недель)

## Критерии начала применения
- Установленный диагноз ИБС
- Необходимость оптимизации терапии или планового наблюдения
- Отсутствие нестабильной стенокардии – при появлении перейти к [[PROT-EMERGENCY_P-003]]

## Алгоритм ведения пациента
1. **Оценка симптомов и риска**: функциональный класс стенокардии (CCS класс), шкала риска (PROT-SCALE-003).
2. **Инструментальная диагностика** по показаниям (ЭКГ, ЭхоКГ, нагрузочные тесты, КТ-коронарография).
3. **Медикаментозная терапия** согласно [[PHARM-REGIMEN-003]]: антиангинальные препараты, статины, антитромбоцитарные средства.
4. **Модификация образа жизни** (диета, физическая активность, отказ от курения) – [[PHARM-NONPHARM-003]].
5. **Решение о реваскуляризации** (при рефрактерной симптоматике, высоком риске).
6. **Плановое наблюдение** по PROT-FOLLOW-UP-003.

## Ключевые решения и развилки
- Низкий риск, отсутствие рефрактерной стенокардии → продолжать медикаментозную терапию, контроль каждые 6–12 мес.
- Средний/высокий риск или рефрактерная стенокардия (III–IV ФК) → направить на коронарографию, рассмотреть реваскуляризацию (стентирование/АКШ).
- Появление нестабильной стенокардии или подозрение на ОКС → экстренная маршрутизация и переход к PROT-EMERGENCY_P-003.

## Критерии срочности
- **Routine**: стабильная стенокардия I–II ФК, плановый визит.
- **Urgent**: прогрессирование стенокардии (преход с I–II на III ФК за короткое время), возобновление симптомов после реваскуляризации.
- **Emergency**: острая боль в груди > 20 мин, гемодинамическая нестабильность, подозрение на ОКС.

## Связанные маршруты пациента
- [[PROT-ROUTING-003]] (маршрутизация)

## Связанные шкалы
- [[PROT-SCALE-003]] (функциональный класс, риск)

## Неотложные состояния и действия
- [[PROT-EMERGENCY_P-003]] – при нестабильной стенокардии/ОКС

## Рекомендации по терапии
- [[PHARM-REGIMEN-003]]
- [[PHARM-DRUG-002]] (амлодипин)
- [[PHARM-DRUGCLASS-020]] (β-блокаторы)
- [[PHARM-DRUGCLASS-011]] (антитромбоцитарные)
- [[PHARM-DRUGCLASS-012]] (статины)

## Памятка пациенту
- [[PROT-PATIENT_INFO-003]]

## Дальнейшее наблюдение
- [[PROT-FOLLOW_UP-003]]

## Особенности у отдельных групп
- Пожилые: чаще атипичные симптомы, высокий риск побочных эффектов ( старт с низких доз β-блокаторов, контроль АД).
- Пациенты с сахарным диабетом: более агрессивная липидснижающая терапия, предпочтение ингибиторам SGLT2.
- Хроническая болезнь почек: коррекция доз статинов (не требуется для аторвастатина, розувастатина – снижать дозу при СКФ < 30).

## Ограничения применения
- Не применяется при острых состояниях (ОКС).
- Не заменяет индивидуального подхода и врачебного осмотра.

## Источники
1. Клинические рекомендации «Стабильная ишемическая болезнь сердца». Минздрав РФ, 2024.
2. Vrints C. et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45:3415–3537.

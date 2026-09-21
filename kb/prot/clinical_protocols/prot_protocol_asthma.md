---
id: PROT-PROTOCOL-005
schema_version: 2
title: 'Клинический протокол: Бронхиальная астма'
domain: prot
category: protocol
body_system:
- respiratory
tags:
- protocol
- asthma
- management
urgency: urgent
access_level: professional
target_specialist:
- pulmonologist
- therapist
- allergist
age_group:
- adult
- child
- all_ages
evidence_level: Ia
recommendation_class: I
relations:
- target: DIAG-DISEASE-004
  type: protocol_for
  description: Протокол для ведения пациентов с бронхиальной астмой.
- target: PHARM-REGIMEN-005
  type: recommends
  description: Использует ступенчатую схему лечения.
- target: PROT-SCALE-005
  type: assessed_by
  description: Оценка контроля симптомов (ACT).
- target: PROT-ROUTING-005
  type: has_routing
  description: Маршрутизация в зависимости от тяжести.
- target: PROT-EMERGENCY_P-005
  type: has_emergency_protocol
  description: При тяжёлом обострении – переход к неотложному алгоритму.
- target: PROT-PATIENT_INFO-005
  type: has_patient_info
  description: Памятка пациенту.
- target: PROT-FOLLOW_UP-005
  type: has_follow_up
  description: Дальнейшее наблюдение.
- target: PROT-CHECKLIST-005
  type: has_checklist
  description: Чек-лист первичного приёма.
- target: PROT-SCREENING-005
  type: has_screening
  description: Скрининг аллергии и вакцинация.
for:
- DIAG-DISEASE-004
entry:
  any:
  - disease: DIAG-DISEASE-004
  - fact: known_asthma
  - exam_result: DIAG-EXAM-008
    value: reversible_obstruction
steps:
- id: spirometry
  action: спирометрия с бронходилатационным тестом
  refs:
  - DIAG-EXAM-008
- id: control
  action: оценка контроля по ACT
  refs:
  - PROT-SCALE-005
- id: therapy
  action: 'ступенчатая терапия: низкие дозы ИГКС-формотерола по потребности или базисно'
  refs:
  - PHARM-REGIMEN-005
  - PHARM-DRUGCLASS-018
- id: technique
  action: проверка техники ингаляции и приверженности на каждом визите
- id: triggers
  action: устранение триггеров, отказ от курения, вакцинация
  refs:
  - PHARM-NONPHARM-005
- id: follow_up
  action: контроль через 1–3 месяца после изменения терапии
  refs:
  - PROT-FOLLOW_UP-005
branches:
- when:
    redflag: DIAG-REDFLAG-006
  then: PROT-EMERGENCY_P-005
  explanation: тяжёлое обострение
- when:
    scale_category: PROT-SCALE-005
    value: uncontrolled
  then: PROT-ROUTING-005
  explanation: астма не контролируется
targets:
- param: pef_percent
  op: '>='
  value: 80
  label: ПСВ 80 % от лучшего и выше
sources:
- GINA Global Strategy for Asthma Management and Prevention, 2025
- Клинические рекомендации «Бронхиальная астма», 2024
clinical_guidelines:
- GINA 2025
last_medical_review: '2026-05-06'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.1'
date_created: '2026-05-02'
date_updated: '2026-09-16'
status: medical_review
disclaimer: true
---

# Клинический протокол: Бронхиальная астма

> ⚕️ Документ предназначен для медицинских специалистов.

## Назначение протокола
Ведение пациентов с бронхиальной астмой: диагностика, оценка контроля, ступенчатая терапия, профилактика обострений, обучение пациента.

## Область применения
- Бронхиальная астма (все фенотипы)
- Взрослые и дети (с 6 лет)
- Амбулаторная и стационарная практика

## Входные условия
- [[DIAG-DISEASE-004]] – подтверждённый диагноз астмы (на основании симптомов, спирометрии с обратимостью).

## Критерии начала применения
- Установленный диагноз, независимо от тяжести.
- Плановая оценка контроля или изменение терапии.

## Алгоритм ведения пациента
1. **Подтверждение диагноза**: оценка симптомов, спирометрия (обратимость), при необходимости – бронхопровокационный тест.
2. **Оценка контроля** (PROT-SCALE-005): ACT, частота использования SABA, ночные пробуждения, обострения.
3. **Оценка факторов риска** (курение, аллергены, ожирение, ГЭРБ, ринит).
4. **Выбор ступени терапии** по GINA (см. PHARM-REGIMEN-005).
5. **Обучение пациента** (техника ингаляции, план действий, избегание триггеров).
6. **Назначение базисной терапии** (ИГКС ± LABA, по ступени).
7. **Терапия облегчения** (SABA или ИГКС/формотерол по требованию).
8. **Контроль через 1–3 месяца**, коррекция ступени (шаг вверх/вниз).

## Ключевые решения и развилки
- **Хороший контроль** → продолжать текущую ступень, рассмотреть шаг вниз через 3 месяца.
- **Частичный или отсутствие контроля** → проверить приверженность, технику, триггеры; при их отсутствии – шаг вверх (повышение дозы ИГКС, добавление LABA, тиотропии, биологических препаратов).
- **Тяжёлое обострение** (ПСВ < 50%, невозможность говорить) → экстренная помощь (PROT-EMERGENCY_P-005).

## Критерии срочности
- **Routine**: плановый визит, стабильное течение.
- **Urgent**: учащение симптомов, снижение ПСВ, потребность в SABA чаще 3–4 раз/сут, обострение средней тяжести.
- **Emergency**: тяжёлое обострение, астматический статус.

## Связанные маршруты пациента
- [[PROT-ROUTING-005]]

## Связанные шкалы
- [[PROT-SCALE-005]] (ACT, ACQ)

## Неотложные состояния и действия
- [[PROT-EMERGENCY_P-005]] – Тяжёлое обострение астмы / астматический статус

## Рекомендации по терапии
- [[PHARM-REGIMEN-005]] (ступенчатая схема)
- [[PHARM-DRUGCLASS-017]] (SABA)
- [[PHARM-DRUGCLASS-018]] (ИГКС)
- [[PHARM-DRUGCLASS-019]] (LAMA – тиотропия)
- [[PHARM-NONPHARM-005]] (немедикаментозное)

## Памятка пациенту
- [[PROT-PATIENT_INFO-005]]

## Дальнейшее наблюдение
- [[PROT-FOLLOW_UP-005]]

## Особенности у отдельных групп
- **Дети 6–11 лет**: предпочтительны ИГКС низких доз, избегать высоких доз.
- **Беременные**: ИГКС (будесонид) безопасны, LABA и антилейкотриены – по показаниям.
- **Пожилые**: чаще атипичные симптомы, учитывать коморбидность (ХОБЛ, сердечно-сосудистые заболевания).

## Ограничения применения
- Не適用 для купирования жизнеугрожающих состояний без врачебного контроля.
- Не заменяет индивидуальный подход.

## Источники
1. GINA Global Strategy for Asthma Management and Prevention, 2025.
2. Клинические рекомендации «Бронхиальная астма», 2024.
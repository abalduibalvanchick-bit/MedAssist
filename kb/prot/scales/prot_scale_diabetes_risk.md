---
id: PROT-SCALE-002
schema_version: 2
title: 'Клиническая шкала: Оценка риска осложнений при сахарном диабете 2 типа'
domain: prot
category: scale
body_system:
- endocrine
- cardiovascular
tags:
- scale
- risk_assessment
- diabetes
urgency: routine
access_level: professional
target_specialist:
- therapist
- endocrinologist
age_group:
- adult
evidence_level: IIa
recommendation_class: I
relations:
- target: PROT-PROTOCOL-002
  type: assesses
  description: Шкала используется в клиническом протоколе для стратификации риска.
- target: PROT-ROUTING-002
  type: next_step
  description: Результат шкалы влияет на маршрутизацию и частоту наблюдения.
- target: DIAG-DISEASE-006
  type: assesses
  description: Шкала оценивает риск у пациентов с СД2.
- target: PHARM-REGIMEN-002
  type: recommends
  description: Результат шкалы помогает выбрать интенсивность терапии.
parameters:
- code: age
  label: Возраст
  options:
  - when:
      param: age
      op: <
      value: 55
    points: 0
  - when:
      param: age
      op: between
      value:
      - 55
      - 64
    points: 1
  - when:
      param: age
      op: '>='
      value: 65
    points: 2
- code: duration
  label: Длительность диабета
  options:
  - when:
      param: diabetes_duration_years
      op: <
      value: 5
    points: 0
  - when:
      all:
      - param: diabetes_duration_years
        op: '>='
        value: 5
      - param: diabetes_duration_years
        op: <
        value: 10
    points: 1
  - when:
      param: diabetes_duration_years
      op: '>='
      value: 10
    points: 2
- code: bmi
  label: Индекс массы тела
  options:
  - when:
      param: bmi
      op: <
      value: 25
    points: 0
  - when:
      all:
      - param: bmi
        op: '>='
        value: 25
      - param: bmi
        op: <
        value: 30
    points: 1
  - when:
      param: bmi
      op: '>='
      value: 30
    points: 2
- code: hba1c
  label: HbA1c
  options:
  - when:
      param: hba1c
      op: <
      value: 7
    points: 0
  - when:
      all:
      - param: hba1c
        op: '>='
        value: 7
      - param: hba1c
        op: <
        value: 8
    points: 1
  - when:
      param: hba1c
      op: '>='
      value: 8
    points: 2
- code: sbp
  label: Систолическое АД
  options:
  - when:
      param: sbp
      op: <
      value: 130
    points: 0
  - when:
      param: sbp
      op: between
      value:
      - 130
      - 139
    points: 1
  - when:
      param: sbp
      op: '>='
      value: 140
    points: 2
- code: smoking
  label: Курение
  options:
  - when:
      fact: smoker
    points: 1
  - when:
      not:
        fact: smoker
    points: 0
- code: albuminuria
  label: Альбуминурия
  options:
  - when:
      param: microalbuminuria
    points: 2
  - when:
      param: microalbuminuria
      op: ==
      value: false
    points: 0
- code: egfr
  label: СКФ
  options:
  - when:
      param: egfr
      op: '>='
      value: 60
    points: 0
  - when:
      all:
      - param: egfr
        op: '>='
        value: 45
      - param: egfr
        op: <
        value: 60
    points: 1
  - when:
      param: egfr
      op: <
      value: 45
    points: 2
- code: cv_event
  label: Сердечно-сосудистое событие в анамнезе
  options:
  - when:
      fact: prior_cv_event
    points: 3
  - when:
      not:
        fact: prior_cv_event
    points: 0
interpretation:
- min: 0
  max: 4
  category: low
  label: низкий риск
  action: PROT-FOLLOW_UP-002
- min: 5
  max: 9
  category: moderate
  label: умеренный риск
  action: PROT-PROTOCOL-002
- min: 10
  max: 14
  category: high
  label: высокий риск
  action: PROT-PROTOCOL-002
- min: 15
  max: null
  category: very_high
  label: очень высокий риск
  action: PROT-ROUTING-002
missing_policy: skip
sources:
- American Diabetes Association Professional Practice Committee. Standards of Care in Diabetes — 2025. Diabetes Care. 2025;48(Suppl 1).
- Marx N. et al. 2023 ESC Guidelines for the management of cardiovascular disease in patients with diabetes. Eur Heart J. 2023;44:4043–4140.
clinical_guidelines:
- ADA Standards of Care in Diabetes — 2025
- 2023 ESC Guidelines on cardiovascular disease in diabetes
last_medical_review: '2026-05-02'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.1'
date_created: '2026-05-02'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Клиническая шкала: Оценка риска осложнений при сахарном диабете 2 типа

> ⚕️ Шкала используется для формализованной оценки риска сердечно-сосудистых осложнений и определения тактики ведения.

## Назначение шкалы
Оценка сердечно-сосудистого риска у пациентов с сахарным диабетом 2 типа для выбора целевого уровня HbA1c, назначения дополнительных препаратов (ингибиторы SGLT2, агонисты ГПП-1), определения частоты наблюдения.

## Область применения
- Сахарный диабет 2 типа
- Амбулаторная практика, стационар
- Первичный приём и динамическое наблюдение

## Параметры оценки – модифицированная шкала (упрощённая, для учебных целей)

| Параметр | Значения | Баллы |
|----------|----------|-------|
| Возраст | < 55 лет – 0 | |
| | 55–64 года – 1 | |
| | ≥ 65 лет – 2 | |
| Длительность диабета | < 5 лет – 0 | |
| | 5–9 лет – 1 | |
| | ≥ 10 лет – 2 | |
| ИМТ | < 25 – 0 | |
| | 25–29.9 – 1 | |
| | ≥ 30 – 2 | |
| HbA1c | < 7% – 0 | |
| | 7–7.9% – 1 | |
| | ≥ 8% – 2 | |
| АД (систолическое) | < 130 – 0 | |
| | 130–139 – 1 | |
| | ≥ 140 – 2 | |
| Курение | нет – 0 | |
| | да – 1 | |
| Микроальбуминурия | нет – 0 | |
| | да – 2 | |
| СКФ (мл/мин/1.73 м²) | ≥ 90 – 0 | |
| | 60–89 – 0 | |
| | 45–59 – 1 | |
| | < 45 – 2 | |
| Сердечно-сосудистое событие в анамнезе (ИМ, инсульт, реваскуляризация) | нет – 0 | |
| | да – 3 | |

## Правила расчёта
1. Суммируются баллы по всем доступным параметрам.
2. При отсутствии данных параметр не учитывается (но для полноты желательно оценить).
3. Суммарный балл определяет категорию риска.

## Интерпретация результата

| Сумма баллов | Категория риска | Клиническое значение |
|--------------|------------------|----------------------|
| 0–4 | низкий | Целевой HbA1c < 7.0%. Осмотр 1 раз в 3–6 мес. |
| 5–9 | умеренный | Целевой HbA1c < 7.0% (индивидуализированно). Рассмотреть добавление ингибитора SGLT2/агониста ГПП-1 при высоком риске. Осмотр 1 раз в 3 мес. |
| 10–14 | высокий | Целевой HbA1c < 7.0–7.5% (индивидуализированно). Рекомендованы ингибиторы SGLT2 или агонисты ГПП-1 для снижения кардиоваскулярного риска. Осмотр каждые 1–3 мес. |
| ≥ 15 | очень высокий | Целевой HbA1c индивидуализирован (до 8.0% у пожилых/хрупких). Обязательны ингибиторы SGLT2/агонисты ГПП-1 (при отсутствии противопоказаний). Частое наблюдение, возможно направление к кардиологу/нефрологу. |

## Тактическая значимость
- **Низкий риск** → стандартное ведение по [[PROT-PROTOCOL-002]].
- **Умеренный риск** → протокол + рассмотреть кардиопротективные препараты (SGLT2, ГПП-1).
- **Высокий/очень высокий риск** → активная тактика, направление к кардиологу/нефрологу, более жёсткий контроль АД и липидов, возможно изменение маршрута согласно [[PROT-ROUTING-002]].

## Ограничения
- Шкала является упрощённой моделью; не заменяет клиническое решение врача.
- Для точной оценки риска используются калькуляторы (SCORE2-Diabetes, UKPDS risk engine) – в реальной практике.
- Не учитывает этнические особенности.

## Особенности применения
- **Пожилые**: пороговые значения повышаются, целевой HbA1c может быть выше (7.5–8.5%).
- **Пациенты с ХБП, ХСН**: даже при умеренном риске показаны ингибиторы SGLT2.
- **Беременные**: данная шкала неприменима.

## Связанные документы
- [[PROT-PROTOCOL-002]] – клинический протокол
- [[PROT-ROUTING-002]] – маршрутизация пациента
- [[PHARM-REGIMEN-002]] – схема лечения

## Источники
1. American Diabetes Association Professional Practice Committee. Standards of Care in Diabetes — 2025. Diabetes Care. 2025;48(Suppl 1).
2. Marx N. et al. 2023 ESC Guidelines for the management of cardiovascular disease in patients with diabetes. Eur Heart J. 2023;44:4043–4140.

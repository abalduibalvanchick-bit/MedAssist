---
id: PROT-SCALE-001
schema_version: 2
title: 'Клиническая шкала: Оценка сердечно-сосудистого риска при артериальной гипертензии'
domain: prot
category: scale
body_system:
- cardiovascular
tags:
- scale
- risk_assessment
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
- target: PROT-PROTOCOL-001
  type: assesses
  description: Шкала используется в общем протоколе ведения.
- target: PROT-ROUTING-001
  type: next_step
  description: Результат шкалы влияет на маршрут пациента.
- target: DIAG-DISEASE-001
  type: assesses
  description: Шкала оценивает риск при артериальной гипертензии.
- target: PHARM-REGIMEN-001
  type: recommends
  description: Категория риска может влиять на выбор режима терапии.
- target: PROT-FOLLOW_UP-001
  type: assesses
  description: выведено из машиночитаемого слоя (interpretation)
parameters:
- code: sbp
  label: Систолическое АД
  options:
  - when:
      param: sbp
      op: <
      value: 140
    points: 0
    label: менее 140
  - when:
      param: sbp
      op: between
      value:
      - 140
      - 159
    points: 1
    label: 140–159
  - when:
      param: sbp
      op: '>='
      value: 160
    points: 2
    label: 160 и выше
- code: smoking
  label: Курение
  options:
  - when:
      fact: smoker
    points: 1
    label: да
  - when:
      not:
        fact: smoker
    points: 0
    label: нет
- code: diabetes
  label: Сахарный диабет
  options:
  - when:
      any:
      - disease: DIAG-DISEASE-006
      - fact: known_diabetes
    points: 1
    label: да
  - when:
      not:
        any:
        - disease: DIAG-DISEASE-006
        - fact: known_diabetes
    points: 0
    label: нет
- code: age
  label: Возраст
  options:
  - when:
      param: age
      op: <
      value: 60
    points: 0
    label: менее 60 лет
  - when:
      param: age
      op: '>='
      value: 60
    points: 1
    label: 60 лет и старше
interpretation:
- min: 0
  max: 1
  category: low
  label: низкий риск
  action: PROT-FOLLOW_UP-001
- min: 2
  max: 3
  category: moderate
  label: умеренный риск
  action: PROT-PROTOCOL-001
- min: 4
  max: null
  category: high
  label: высокий риск
  action: PROT-ROUTING-001
missing_policy: skip
sources:
- Клинические рекомендации «Артериальная гипертензия у взрослых». Минздрав РФ, 2024.
- Mancia G. et al. 2023 ESH Guidelines for the management of arterial hypertension. J Hypertens. 2023;41:1874–2071.
- SCORE2 working group and ESC Cardiovascular risk collaboration. SCORE2 risk prediction algorithms. Eur Heart J. 2021;42:2439–2454.
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

# Клиническая шкала: Оценка сердечно-сосудистого риска при артериальной гипертензии

> ⚕️ Шкала используется для формализованной оценки риска осложнений и выбора тактики ведения пациента.

## Назначение шкалы
Оценка сердечно-сосудистого риска у пациентов с артериальной гипертензией для определения дальнейшей тактики лечения и наблюдения.

## Область применения
- артериальная гипертензия;
- амбулаторная практика;
- первичный приём и последующее наблюдение.

## Параметры оценки

| Параметр | Значения | Баллы |
|----------|----------|-------|
| Систолическое АД | < 140 мм рт. ст. | 0 |
| Систолическое АД | 140–159 мм рт. ст. | 1 |
| Систолическое АД | ≥ 160 мм рт. ст. | 2 |
| Курение | нет | 0 |
| Курение | да | 1 |
| Сахарный диабет | нет | 0 |
| Сахарный диабет | да | 1 |
| Возраст | < 60 лет | 0 |
| Возраст | ≥ 60 лет | 1 |

## Правила расчёта
1. Суммируются баллы по всем параметрам.
2. Оцениваются все доступные факторы риска.
3. При отсутствии данных параметр не учитывается.

## Интерпретация результата

| Сумма баллов | Категория риска | Клиническое значение |
|--------------|------------------|----------------------|
| 0–1 | низкий | возможно немедикаментозное ведение |
| 2–3 | умеренный | требуется медикаментозная терапия |
| ≥ 4 | высокий | высокий риск осложнений, требуется активная тактика |

## Тактическая значимость
- низкий риск → амбулаторное наблюдение;
- умеренный риск → [[PROT-PROTOCOL-001]];
- высокий риск → [[PROT-ROUTING-001]] или усиленная терапия.

## Ограничения
- шкала является упрощённой моделью;
- не заменяет клиническое решение врача;
- требует учёта сопутствующих заболеваний.

## Особенности применения
- **Пожилые**: учитывать коморбидность.
- **Пациенты с сахарным диабетом**: риск может быть выше, чем по шкале.
- **Коморбидные пациенты**: требуется индивидуализация.

## Связанные документы
- [[PROT-PROTOCOL-001]] — клинический протокол;
- [[PROT-ROUTING-001]] — маршрутизация пациента;
- [[PHARM-REGIMEN-001]] — терапия.

## Источники
1. Клинические рекомендации «Артериальная гипертензия у взрослых». Минздрав РФ, 2024.
2. Mancia G. et al. 2023 ESH Guidelines for the management of arterial hypertension. J Hypertens. 2023;41:1874–2071.
3. SCORE2 working group and ESC Cardiovascular risk collaboration. SCORE2 risk prediction algorithms. Eur Heart J. 2021;42:2439–2454.

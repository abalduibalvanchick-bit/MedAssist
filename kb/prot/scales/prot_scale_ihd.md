---
id: PROT-SCALE-003
schema_version: 2
title: 'Клиническая шкала: Функциональный класс стенокардии (CCS) и риск осложнений при ИБС'
domain: prot
category: scale
body_system:
- cardiovascular
tags:
- scale
- angina
- ccs_class
- risk
urgency: routine
access_level: professional
target_specialist:
- cardiologist
- therapist
age_group:
- adult
- elderly
evidence_level: IIa
recommendation_class: I
relations:
- target: PROT-PROTOCOL-003
  type: assesses
  description: Шкала используется в клиническом протоколе ИБС.
- target: PROT-ROUTING-003
  type: next_step
  description: ФК стенокардии и риск определяют маршрут пациента.
- target: DIAG-DISEASE-002
  type: assesses
  description: Оценивает тяжесть ИБС и прогноз.
- target: PHARM-REGIMEN-003
  type: recommends
  description: Категория риска влияет на выбор схемы лечения.
parameters:
- code: ccs
  label: ФК стенокардии III–IV
  options:
  - when:
      param: ccs_class
      op: '>='
      value: 3
    points: 2
  - when:
      param: ccs_class
      op: <
      value: 3
    points: 0
- code: prior_mi
  label: Перенесённый инфаркт миокарда
  options:
  - when:
      fact: prior_mi
    points: 1
  - when:
      not:
        fact: prior_mi
    points: 0
- code: heart_failure
  label: Сердечная недостаточность
  options:
  - when:
      fact: heart_failure
    points: 2
  - when:
      not:
        fact: heart_failure
    points: 0
- code: diabetes
  label: Сахарный диабет
  options:
  - when:
      any:
      - disease: DIAG-DISEASE-006
      - fact: known_diabetes
    points: 1
  - when:
      not:
        any:
        - disease: DIAG-DISEASE-006
        - fact: known_diabetes
    points: 0
- code: lvef
  label: ФВ ЛЖ менее 45 %
  options:
  - when:
      param: lvef
      op: <
      value: 45
    points: 2
  - when:
      param: lvef
      op: '>='
      value: 45
    points: 0
- code: troponin
  label: Положительный высокочувствительный тропонин
  options:
  - when:
      param: troponin_positive
    points: 1
  - when:
      param: troponin_positive
      op: ==
      value: false
    points: 0
- code: refractory
  label: Рефрактерная стенокардия
  options:
  - when:
      fact: refractory_angina
    points: 1
  - when:
      not:
        fact: refractory_angina
    points: 0
interpretation:
- min: 0
  max: 1
  category: low
  label: низкий риск
  action: PROT-PROTOCOL-003
- min: 2
  max: 3
  category: moderate
  label: умеренный риск
  action: PROT-ROUTING-003
- min: 4
  max: null
  category: high
  label: высокий риск
  action: PROT-ROUTING-003
missing_policy: skip
sources:
- 2023 ESC Guidelines for CCS
- Canadian Cardiovascular Society (CCS) grading of angina pectoris
clinical_guidelines:
- 2023 ESC Guidelines for CCS
last_medical_review: '2026-05-06'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.1'
date_created: '2026-05-02'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Клиническая шкала: Функциональный класс стенокардии (CCS) и риск осложнений при ИБС

> ⚕️ Шкала используется для формализованной оценки функционального класса стенокардии и сердечно-сосудистого риска.

## Назначение шкалы
1. Определение функционального класса стенокардии по классификации Канадского сердечно-сосудистого общества (CCS).
2. Простая оценка риска смерти и инфаркта миокарда у пациентов с хронической ИБС (на основе модифицированных критериев).

## Область применения
- Хроническая ИБС (стабильная стенокардия)
- Амбулаторная и стационарная практика
- Первичный приём и динамическое наблюдение

## Функциональный класс стенокардии (CCS)

| Класс | Описание |
|-------|----------|
| **I** | Обычная физическая нагрузка (ходьба, подъём по лестнице) не вызывает стенокардию. Стенокардия возникает только при интенсивной, быстрой или продолжительной нагрузке (например, бег). |
| **II** | Небольшое ограничение обычной активности. Стенокардия возникает при ходьбе на расстояние > 2 кварталов (> 200 м) или подъёме на 2 лестничных пролёта, а также при ходьбе в гору, после еды, на холоде, при стрессе. |
| **III** | Выраженное ограничение обычной активности. Стенокардия возникает при ходьбе на 1–2 квартала (100–200 м) или подъёме на 1 лестничный пролёт. |
| **IV** | Невозможность выполнять любую физическую нагрузку без дискомфорта. Стенокардия может возникать в покое. |

## Оценка риска (модифицированная шкала, для учебных целей)

| Параметр | Баллы |
|----------|-------|
| ФК стенокардии III–IV | 2 |
| Перенесённый инфаркт миокарда (> 6 мес назад) | 1 |
| Сердечная недостаточность (одышка, отёки, сниженная ФВ) | 2 |
| Сахарный диабет | 1 |
| Снижение ФВ ЛЖ < 45% | 2 |
| Положительный высокочувствительный тропонин (> 99 перцентиля) | 1 |
| Стенокардия, рефрактерная к оптимальной терапии (≥ 2 антиангинальных препарата) | 1 |

**Интерпретация суммы баллов:**
- **0–1 балл**: низкий риск (годовая смертность < 1%)
- **2–3 балла**: умеренный риск (годовая смертность 1–3%)
- **≥ 4 баллов**: высокий риск (годовая смертность > 3%)

## Правила расчёта
1. Определить ФК стенокардии по шкале CCS.
2. Собрать дополнительные данные (анамнез, ФВ, тропонин).
3. Суммировать баллы.
4. Категория риска влияет на тактику.

## Тактическая значимость
- **Низкий риск + ФК I–II** → амбулаторное ведение (PROT-PROTOCOL-003), повтор через 12 мес.
- **Умеренный риск + ФК II–III** → направление к кардиологу, нагрузочные тесты, возможно изменение терапии (PROT-ROUTING-003).
- **Высокий риск, ФК III–IV, рефрактерная стенокардия** → направление на коронарографию, рассмотреть реваскуляризацию, частое наблюдение (PROT-ROUTING-003).

## Ограничения
- Не заменяет формальные калькуляторы риска (например, GRACE, SYNTAX, EUROSCORE II).
- Требует клинической оценки и данных инструментальных методов.

## Особенности применения
- **Пожилые**: ФК может быть завышен из-за сопутствующих заболеваний (одышка, ХОБЛ, артрит).
- **Сахарный диабет**: часто безболевая ишемия – учитывать данные нагрузочных тестов.

## Связанные документы
- [[PROT-PROTOCOL-003]] – клинический протокол
- [[PROT-ROUTING-003]] – маршрутизация
- [[PHARM-REGIMEN-003]] – схема лечения

## Источники
1. Campeau L. Grading of angina pectoris. Circulation. 1976.
2. 2023 ESC Guidelines for the management of chronic coronary syndromes.
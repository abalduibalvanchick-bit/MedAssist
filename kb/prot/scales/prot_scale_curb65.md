---
id: PROT-SCALE-004
schema_version: 2
title: 'Клиническая шкала: CURB-65 для оценки тяжести внебольничной пневмонии'
domain: prot
category: scale
body_system:
- respiratory
tags:
- curb65
- pneumonia
- severity
- scale
urgency: urgent
access_level: professional
target_specialist:
- pulmonologist
- therapist
- emergency_physician
age_group:
- adult
- elderly
evidence_level: IIa
recommendation_class: I
relations:
- target: PROT-PROTOCOL-004
  type: assesses
  description: Шкала используется для выбора места лечения.
- target: PROT-ROUTING-004
  type: next_step
  description: Результаты шкалы определяют маршрут (амбулаторно/стационар/ОРИТ).
- target: DIAG-DISEASE-003
  type: assesses
  description: Оценивает тяжесть пневмонии.
- target: PHARM-REGIMEN-004
  type: recommends
  description: Категория тяжести влияет на выбор антибиотиков.
parameters:
- code: confusion
  label: C — спутанность сознания
  options:
  - when:
      fact: confusion
    points: 1
  - when:
      not:
        fact: confusion
    points: 0
- code: urea
  label: U — мочевина более 7 ммоль/л
  options:
  - when:
      param: urea
      op: '>'
      value: 7
    points: 1
  - when:
      param: urea
      op: <=
      value: 7
    points: 0
- code: rr
  label: R — ЧДД 30 в минуту и более
  options:
  - when:
      param: rr
      op: '>='
      value: 30
    points: 1
  - when:
      param: rr
      op: <
      value: 30
    points: 0
- code: bp
  label: B — САД менее 90 или ДАД 60 мм рт. ст. и ниже
  options:
  - when:
      any:
      - param: sbp
        op: <
        value: 90
      - param: dbp
        op: <=
        value: 60
    points: 1
  - when:
      all:
      - param: sbp
        op: '>='
        value: 90
      - param: dbp
        op: '>'
        value: 60
    points: 0
- code: age
  label: 65 — возраст 65 лет и старше
  options:
  - when:
      param: age
      op: '>='
      value: 65
    points: 1
  - when:
      param: age
      op: <
      value: 65
    points: 0
interpretation:
- min: 0
  max: 1
  category: mild
  label: лёгкое течение
  action: PROT-PROTOCOL-004
- min: 2
  max: 2
  category: moderate
  label: среднетяжёлое течение
  action: PROT-ROUTING-004
- min: 3
  max: 5
  category: severe
  label: тяжёлое течение
  action: PROT-EMERGENCY_P-004
missing_policy: skip
sources:
- IDSA/ATS Guidelines for CAP, 2023
- Lim WS et al. Thorax. 2003
clinical_guidelines:
- IDSA/ATS CAP Guidelines
last_medical_review: '2026-05-02'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №3
version: '2.1'
date_created: '2026-05-02'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Клиническая шкала: CURB-65 для оценки тяжести внебольничной пневмонии

> ⚕️ Шкала используется для формализованной оценки тяжести пневмонии и выбора места лечения.

## Назначение шкалы
Определение тяжести внебольничной пневмонии для решения вопроса о необходимости госпитализации, лечения в отделении интенсивной терапии (ОРИТ) и эмпирической антибактериальной терапии.

## Область применения
- Взрослые пациенты с внебольничной пневмонией
- При первичном осмотре врача скорой помощи, терапевта, пульмонолога

## Параметры оценки (каждый критерий – 1 балл)

| Критерий | Описание | Баллы |
|----------|----------|-------|
| **C** – Confusion (спутанность сознания) | Снижение уровня сознания, дезориентация (новая) | 1 |
| **U** – Uremia (азотемия) | Мочевина > 7 ммоль/л (или > 20 мг/дл) | 1 |
| **R** – Respiratory rate | Частота дыхания ≥ 30 в минуту | 1 |
| **B** – Blood pressure | САД < 90 мм рт. ст. или ДАД ≤ 60 мм рт. ст. | 1 |
| **65** – Age ≥ 65 лет | Возраст ≥ 65 лет | 1 |

## Правила расчёта
1. Суммируются баллы по каждому присутствующему критерию.
2. Сумма 0–1; 2; 3–5.

## Интерпретация результата

| Сумма баллов | Категория тяжести | Клиническое значение / место лечения |
|--------------|-------------------|--------------------------------------|
| 0–1 | лёгкая | Амбулаторное лечение. Низкий риск смерти (< 2%). |
| 2 | средняя | Госпитализация в терапевтическое/пульмонологическое отделение. Риск смерти ~9%. |
| 3–5 | тяжёлая | Госпитализация в ОРИТ (отделение реанимации и интенсивной терапии). Риск смерти ~15–40%. |

## Тактическая значимость
- **0–1 балл** → амбулаторное лечение по [[PROT-PROTOCOL-004]] (схема для лёгкой пневмонии).
- **2 балла** → госпитализация в стационар, [[PROT-ROUTING-004]] (госпитализация), [[PHARM-REGIMEN-004]] внутривенные антибиотики.
- **≥3 балла** → экстренная госпитализация в ОРИТ, переход к [[PROT-EMERGENCY_P-004]].

## Ограничения
- Шкала не учитывает коморбидность (истощающие заболевания, иммуносупрессию), но для принятия решений применима.
- У молодых пациентов без коморбидности даже 2 балла могут не требовать госпитализации? Но правило – госпитализация.
- Не適用 при подозрении на аспирацию, внутрибольничную пневмонию, легионеллёз (могут требовать госпитализации независимо от баллов).

## Особенности применения
- **Пожилые (≥ 65 лет)**: автоматически получают 1 балл, но требуется осторожность при балле 2 (может потребоваться ОРИТ, если есть сепсис).
- **Беременные**: шкала не специфична, но при 2 баллах также госпитализация.

## Связанные документы
- [[PROT-PROTOCOL-004]] – клинический протокол
- [[PROT-ROUTING-004]] – маршрутизация
- [[PROT-EMERGENCY_P-004]] – неотложная помощь при тяжёлой пневмонии
- [[PHARM-REGIMEN-004]] – схема лечения

## Источники
1. IDSA/ATS Guidelines for CAP, 2023.
2. Lim WS, et al. Defining community-acquired pneumonia severity on presentation to hospital. Thorax 2003.
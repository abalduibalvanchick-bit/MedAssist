---
id: DIAG-DIFDIAG-001
schema_version: 2
title: Дифференциальная диагностика боли в груди
domain: diag
category: difdiag
body_system:
- cardiovascular
- respiratory
- multisystem
tags:
- difdiag
- chest_pain
urgency: urgent
access_level: professional
target_specialist:
- therapist
- cardiologist
- emergency_physician
age_group:
- adult
- all_ages
evidence_level: IV
recommendation_class: I
relations:
- target: DIAG-SYMPTOM-002
  type: differential_for
  description: ведущий симптом для дифференциальной диагностики
- target: DIAG-DISEASE-002
  type: considers
  description: одна из ключевых кардиальных причин
- target: DIAG-EMERGENCY-001
  type: considers
  description: жизнеугрожающее состояние, которое нужно исключить
- target: DIAG-EXAM-002
  type: uses_exam
  description: ключевое первичное исследование при боли в груди
- target: DIAG-EXAM-001
  type: uses_exam
  description: перенесено из поля related (схема v1)
- target: DIAG-REDFLAG-001
  type: considers
  description: перенесено из поля related (схема v1)
- target: DIAG-DISEASE-003
  type: considers
  description: выведено из машиночитаемого слоя (branches)
- target: DIAG-EXAM-004
  type: uses_exam
  description: выведено из машиночитаемого слоя (branches)
leading_symptom: DIAG-SYMPTOM-002
branches:
- target: DIAG-EMERGENCY-001
  supporting:
    any:
    - feature: chest_pain.at_rest
    - feature: chest_pain.nitrate_unresponsive
    - feature: chest_pain.cold_sweat
    - param: symptom_duration_min
      op: '>'
      value: 20
    - exam_result: DIAG-EXAM-002
      value: st_elevation
  key_exam: DIAG-EXAM-002
  prior: high
  urgency: emergency
- target: DIAG-REDFLAG-001
  supporting:
    param: sbp
    op: '>='
    value: 180
  key_exam: DIAG-EXAM-001
  prior: medium
  urgency: emergency
- target: DIAG-DISEASE-002
  supporting:
    all:
    - feature: chest_pain.exertional
    - feature: chest_pain.relieved_by_rest
  against:
    feature: chest_pain.at_rest
  key_exam: DIAG-EXAM-002
  prior: medium
  urgency: urgent
- target: DIAG-DISEASE-003
  supporting:
    any:
    - feature: chest_pain.pleuritic
    - all:
      - symptom: DIAG-SYMPTOM-004
      - symptom: DIAG-SYMPTOM-008
  against:
    feature: chest_pain.exertional
  key_exam: DIAG-EXAM-004
  prior: medium
  urgency: urgent
sources:
- Клинические рекомендации «Стабильная ишемическая болезнь сердца». Минздрав РФ, 2024.
- Vrints C. et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45:3415–3537.
clinical_guidelines:
- КР «Стабильная ишемическая болезнь сердца», Минздрав РФ, 2024
- 2024 ESC Guidelines for the management of chronic coronary syndromes
last_medical_review: '2026-04-09'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.1'
date_created: '2026-04-08'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Дифференциальная диагностика: боль в груди

## Ведущий симптом
[[DIAG-SYMPTOM-002]] Боль в груди.

## Ключевые вопросы при сборе анамнеза
1. Когда началась боль и как быстро нарастала? — помогает отличить острое состояние от хронического.
2. Где локализована боль и есть ли иррадиация? — ориентирует на ишемический, плевральный или мышечно-скелетный характер.
3. Связана ли боль с нагрузкой, дыханием, движением, положением тела, приёмом пищи? — помогает сузить диагностический ряд.
4. Есть ли одышка, потливость, слабость, тошнота, страх, кашель, лихорадка? — уточняет системную значимость и срочность.
5. Есть ли сердечно-сосудистые факторы риска или уже известная ИБС/АГ? — повышает вероятность кардиальной причины.

## Ключевые данные объективного осмотра
- оценка общего состояния и уровня сознания;
- витальные показатели, в том числе [[DIAG-EXAM-001]] измерение АД;
- признаки дыхательной недостаточности;
- аускультация сердца и лёгких;
- поиск признаков гемодинамической нестабильности;
- оценка воспроизводимости боли при пальпации.

## Дифференциально-диагностическая таблица

| Заболевание / состояние | Ключевые признаки | Отличительные особенности | Обязательные обследования | Тактическая значимость |
|-------------------------|------------------|---------------------------|---------------------------|------------------------|
| [[DIAG-EMERGENCY-001]] Острый коронарный синдром | Интенсивная загрудинная боль, слабость, потливость, одышка | Боль в покое, системные симптомы, неотложность | ЭКГ, тропонины, оценка гемодинамики | Исключать в первую очередь |
| [[DIAG-DISEASE-002]] Ишемическая болезнь сердца | Загрудинная боль, связь с нагрузкой | Более типично хроническое, стереотипное течение | ЭКГ, функциональная оценка ишемии | Срочная, но не всегда экстренная оценка |
| [[DIAG-REDFLAG-001]] Гипертонический криз осложнённый | Боль в груди на фоне высокого АД | Есть острое поражение органов-мишеней или угрожающий контекст | Измерение АД, ЭКГ, клиническая оценка осложнений | Экстренная оценка |
| Плеврит / пневмония | Боль при дыхании, кашель | Плевральный характер боли, дыхательная симптоматика | Аускультация, рентгенография | Срочность зависит от тяжести |
| Мышечно-скелетная боль | Локальная боль, связь с движением | Воспроизводится пальпацией, нет типичной ишемии | Осмотр, исключение опасных причин | Обычно неотложность ниже |
| ГЭРБ / эзофагеальная боль | Жжение, дискомфорт за грудиной | Связь с пищей и положением тела | Клиническая оценка, при необходимости гастроэнтерологическое обследование | После исключения опасных причин |

## 🚩 «Красные флаги»
- 🔴 Боль в груди с одышкой, холодным потом и слабостью → срочно исключать ОКС.
- 🔴 Боль в груди на фоне очень высокого АД → исключать осложнённый гипертонический криз.
- 🔴 Гемодинамическая нестабильность, синкопе, снижение сознания → немедленная экстренная помощь.
- 🔴 Внезапная крайне интенсивная боль → исключать жизнеугрожающее состояние.

## Приоритетные диагностические направления
- исключение острого коронарного синдрома;
- оценка гемодинамики и уровня артериального давления;
- разграничение кардиальной, респираторной, гастроэнтерологической и мышечно-скелетной боли;
- выявление признаков критического течения.

## Связанные документы
- [[DIAG-SYMPTOM-002]] — ведущий симптом
- [[DIAG-DISEASE-002]] — частая нозологическая причина
- [[DIAG-EMERGENCY-001]] — состояние, требующее первоочередного исключения
- [[DIAG-EXAM-001]] — обязательная часть первичной оценки
- [[DIAG-REDFLAG-001]] — опасный гипертензивный контекст боли

## Источники
1. Клинические рекомендации «Стабильная ишемическая болезнь сердца». Минздрав РФ, 2024.
2. Vrints C. et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45:3415–3537.

---
id: DIAG-EXAM-007
schema_version: 2
title: Высокочувствительный сердечный тропонин
domain: diag
category: exam
body_system:
- cardiovascular
tags:
- troponin
- biomarker
- acs
- exam
urgency: urgent
access_level: professional
target_specialist:
- cardiologist
- emergency_physician
- therapist
age_group:
- adult
- elderly
evidence_level: Ia
recommendation_class: I
relations:
- target: DIAG-EMERGENCY-001
  type: diagnoses
  description: подтверждает инфаркт миокарда в рамках ОКС
- target: DIAG-DISEASE-002
  type: diagnoses
  description: повышение указывает на повреждение миокарда
- target: DIAG-SYMPTOM-002
  type: diagnoses
  description: обязателен при подозрении на ишемическую боль в груди
results:
- value: negative
  label: ниже 99-го перцентиля верхнего референсного предела при повторном измерении
- value: positive_dynamic
  label: выше 99-го перцентиля с нарастанием или снижением при повторном измерении
  indicates:
  - DIAG-EMERGENCY-001
- value: positive_stable
  label: стабильно повышен без динамики
turnaround: алгоритм 0/1 ч или 0/2 ч
sources:
- Byrne R.A. et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44:3720–3826.
- Thygesen K. et al. Fourth Universal Definition of Myocardial Infarction (2018). Circulation. 2018;138:e618–e651.
- Клинические рекомендации «Острый инфаркт миокарда без подъёма сегмента ST электрокардиограммы». Минздрав РФ, 2024.
clinical_guidelines:
- 2023 ESC Guidelines for the management of acute coronary syndromes
- КР «Острый инфаркт миокарда без подъёма сегмента ST», Минздрав РФ, 2024
last_medical_review: '2026-09-16'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.0'
date_created: '2026-09-16'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Высокочувствительный сердечный тропонин

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов.

## Определение
Количественное определение сердечного тропонина I или T высокочувствительным методом — биохимический маркер повреждения кардиомиоцитов.

## Назначение метода
Подтверждение или исключение инфаркта миокарда у пациентов с подозрением на острый коронарный синдром без подъёма сегмента ST.

## Показания
- боль в груди ишемического характера;
- эквиваленты стенокардии (одышка, слабость, синкопе) при подозрении на ОКС;
- изменения ЭКГ, характерные для ишемии.

## Диагностическая роль
Инфаркт миокарда диагностируется при повышении тропонина выше 99-го перцентиля верхнего референсного предела с динамикой (нарастание или снижение) в сочетании с клиническими признаками ишемии. Используются ускоренные алгоритмы 0/1 ч и 0/2 ч.

## Интерпретация результатов
| Результат | Значение |
|---|---|
| Отрицательный при повторном измерении | Инфаркт миокарда маловероятен |
| Повышен с динамикой | Острое повреждение миокарда, при клинике ишемии — инфаркт |
| Стабильно повышен | Хроническое повреждение (ХБП, сердечная недостаточность) |

## Ограничения
Повышение возможно при ТЭЛА, миокардите, сепсисе, хронической болезни почек. При подъёме сегмента ST реперфузия не откладывается до получения результата.

## Последовательность назначения
Забор при поступлении и повторно через 1–2 часа (в зависимости от используемого алгоритма), после ЭКГ.

## Связанные документы
- [[DIAG-EMERGENCY-001]] Острый коронарный синдром
- [[DIAG-DISEASE-002]] Ишемическая болезнь сердца

## Источники
1. Byrne R.A. et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44:3720–3826.
2. Thygesen K. et al. Fourth Universal Definition of Myocardial Infarction (2018). Circulation. 2018;138:e618–e651.
3. Клинические рекомендации «Острый инфаркт миокарда без подъёма сегмента ST электрокардиограммы». Минздрав РФ, 2024.

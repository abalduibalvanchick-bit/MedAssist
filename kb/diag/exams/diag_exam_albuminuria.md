---
id: DIAG-EXAM-015
schema_version: 2
title: Альбуминурия (отношение альбумин/креатинин в моче)
domain: diag
category: exam
body_system:
- urinary
tags:
- albuminuria
- uacr
- ckd
- exam
urgency: routine
access_level: professional
target_specialist:
- therapist
- endocrinologist
- nephrologist
age_group:
- adult
- elderly
relations:
- target: PROT-PROTOCOL-002
  type: exam_used_in
  description: скрининг диабетической нефропатии
- target: PROT-FOLLOW_UP-002
  type: exam_used_in
  description: ежегодный контроль при СД2
- target: PROT-PROTOCOL-001
  type: exam_used_in
  description: оценка поражения почек при АГ
results:
- value: a1
  label: менее 3 мг/ммоль (норма, А1)
- value: a2
  label: 3–30 мг/ммоль (умеренно повышена, А2)
- value: a3
  label: более 30 мг/ммоль (значительно повышена, А3)
turnaround: 1 день
sources:
- KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease. Kidney Int. 2024;105(4S):S117–S314.
- American Diabetes Association Professional Practice Committee. Standards of Care in Diabetes — 2025. Diabetes Care. 2025;48(Suppl 1).
clinical_guidelines:
- KDIGO 2024 CKD Guideline
- ADA Standards of Care in Diabetes — 2025
last_medical_review: '2026-09-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.1'
date_created: '2026-09-30'
date_updated: '2026-09-30'
status: approved
disclaimer: true
---

# Альбуминурия (отношение альбумин/креатинин в моче)

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не заменяет консультацию врача.

## Определение
Определение отношения альбумина к креатинину в разовой порции мочи.

## Назначение метода
Раннее выявление поражения почек при сахарном диабете и артериальной гипертензии.

## Показания
- сахарный диабет 2 типа — при установлении диагноза и ежегодно;
- артериальная гипертензия — при оценке поражения органов-мишеней.

## Диагностическая роль
Альбуминурия А2 и выше — маркер поражения почек и повышенного сердечно-сосудистого риска; учитывается в шкале риска осложнений СД2 и в выборе органопротективной терапии.

## Интерпретация результатов
| Отношение альбумин/креатинин | Категория |
|---|---|
| менее 3 мг/ммоль | А1 — норма |
| 3–30 мг/ммоль | А2 — умеренно повышена |
| более 30 мг/ммоль | А3 — значительно повышена |

## Ограничения
Транзиторное повышение при лихорадке, интенсивной нагрузке, инфекции мочевых путей; для подтверждения нужны 2 из 3 положительных проб за 3–6 месяцев.

## Последовательность назначения
Вместе с креатинином и СКФ.

## Связанные заболевания и симптомы
Сахарный диабет 2 типа, артериальная гипертензия, хроническая болезнь почек; отёки.

## Особенности у отдельных групп
У беременных повышение требует исключения преэклампсии.

## Связанные документы
- [[PROT-PROTOCOL-002]] Клинический протокол: Сахарный диабет 2 типа — скрининг диабетической нефропатии
- [[PROT-FOLLOW_UP-002]] Наблюдение пациента: Сахарный диабет 2 типа — ежегодный контроль при СД2
- [[PROT-PROTOCOL-001]] Клинический протокол: Артериальная гипертензия — оценка поражения почек при АГ

## Источники
1. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease. Kidney Int. 2024;105(4S):S117–S314.
2. American Diabetes Association Professional Practice Committee. Standards of Care in Diabetes — 2025. Diabetes Care. 2025;48(Suppl 1).

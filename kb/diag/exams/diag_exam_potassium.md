---
id: DIAG-EXAM-013
schema_version: 2
title: Калий сыворотки
domain: diag
category: exam
body_system:
- urinary
- cardiovascular
tags:
- potassium
- electrolytes
- exam
urgency: routine
access_level: professional
target_specialist:
- therapist
- cardiologist
- nephrologist
- endocrinologist
age_group:
- adult
- elderly
relations:
- target: PROT-FOLLOW_UP-001
  type: exam_used_in
  description: контроль калия на фоне иАПФ, БРА и диуретиков
- target: PROT-EMERGENCY_P-002
  type: exam_used_in
  description: контроль калия при инсулинотерапии гипергликемического криза
results:
- value: hypokalemia
  label: менее 3,5 ммоль/л
- value: normal
  label: 3,5–5,0 ммоль/л
- value: mild_hyperkalemia
  label: 5,1–5,5 ммоль/л
- value: hyperkalemia
  label: более 5,5 ммоль/л
turnaround: 1 час
sources:
- Palmer B.F., Clegg D.J. Physiology and pathophysiology of potassium homeostasis. Adv Physiol Educ. 2016;40:480–490.
- Mancia G. et al. 2023 ESH Guidelines for the management of arterial hypertension. J Hypertens. 2023;41:1874–2071.
clinical_guidelines:
- 2023 ESH Guidelines for the management of arterial hypertension
last_medical_review: '2026-09-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.1'
date_created: '2026-09-30'
date_updated: '2026-09-30'
status: approved
disclaimer: true
---

# Калий сыворотки

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не заменяет консультацию врача.

## Определение
Определение концентрации калия в сыворотке крови.

## Назначение метода
Контроль безопасности терапии препаратами, влияющими на обмен калия, и оценка электролитных нарушений при неотложных состояниях.

## Показания
- перед началом и через 1–2 недели после назначения иАПФ, БРА, диуретиков;
- гипергликемический криз (инсулинотерапия снижает калий);
- сниженная функция почек.

## Диагностическая роль
Калий более 5,5 ммоль/л — противопоказание к началу терапии иАПФ и БРА (правило RULE-PHARM-007); гипокалиемия — противопоказание к тиазидным диуретикам до коррекции.

## Интерпретация результатов
| Калий | Значение |
|---|---|
| менее 3,5 ммоль/л | гипокалиемия |
| 3,5–5,0 ммоль/л | норма |
| 5,1–5,5 ммоль/л | умеренная гиперкалиемия, контроль |
| более 5,5 ммоль/л | гиперкалиемия, коррекция терапии |

## Ограничения
Ложное повышение при гемолизе пробы и длительном наложении жгута.

## Последовательность назначения
Вместе с креатинином и СКФ.

## Связанные заболевания и симптомы
Артериальная гипертензия, хроническая болезнь почек, гипергликемические кризы; сердцебиение, слабость.

## Особенности у отдельных групп
При СКФ менее 30 риск гиперкалиемии на фоне иАПФ и БРА особенно высок.

## Связанные документы
- [[PROT-FOLLOW_UP-001]] Наблюдение пациента: Артериальная гипертензия — контроль калия на фоне иАПФ, БРА и диуретиков
- [[PROT-EMERGENCY_P-002]] Алгоритм неотложной помощи: Тяжёлая гипергликемия / Гиперосмолярное гипергликемическое состояние (ГГС) — контроль калия при инсулинотерапии гипергликемического криза

## Источники
1. Palmer B.F., Clegg D.J. Physiology and pathophysiology of potassium homeostasis. Adv Physiol Educ. 2016;40:480–490.
2. Mancia G. et al. 2023 ESH Guidelines for the management of arterial hypertension. J Hypertens. 2023;41:1874–2071.

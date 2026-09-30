---
id: DIAG-EXAM-016
schema_version: 2
title: Липидный профиль
domain: diag
category: exam
body_system:
- cardiovascular
- metabolic
tags:
- lipids
- ldl
- cholesterol
- exam
urgency: routine
access_level: professional
target_specialist:
- therapist
- cardiologist
- endocrinologist
age_group:
- adult
- elderly
relations:
- target: PROT-PROTOCOL-003
  type: exam_used_in
  description: контроль гиполипидемической терапии при ИБС
- target: PROT-SCREENING-003
  type: exam_used_in
  description: оценка сердечно-сосудистого риска
- target: PROT-PROTOCOL-001
  type: exam_used_in
  description: оценка факторов риска при АГ
results:
- value: at_target
  label: ХС ЛПНП в пределах целевого уровня для категории риска
- value: above_target
  label: ХС ЛПНП выше целевого уровня
- value: severe
  label: ХС ЛПНП 4,9 ммоль/л и выше
turnaround: 1 день
sources:
- 'Mach F. et al. 2019 ESC/EAS Guidelines for the management of dyslipidaemias: lipid modification to reduce cardiovascular risk. Eur Heart J. 2020;41:111–188.'
- Vrints C. et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45:3415–3537.
clinical_guidelines:
- '2019 ESC/EAS Guidelines for the management of dyslipidaemias: lipid modification to reduce cardiovascular risk'
- 2024 ESC Guidelines for the management of chronic coronary syndromes
last_medical_review: '2026-09-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.1'
date_created: '2026-09-30'
date_updated: '2026-09-30'
status: approved
disclaimer: true
---

# Липидный профиль

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не заменяет консультацию врача.

## Определение
Определение общего холестерина, холестерина липопротеинов низкой плотности (ЛПНП), высокой плотности (ЛПВП) и триглицеридов.

## Назначение метода
Оценка сердечно-сосудистого риска и контроль эффективности гиполипидемической терапии.

## Показания
- ИБС, сахарный диабет, артериальная гипертензия;
- скрининг сердечно-сосудистого риска у взрослых;
- через 4–12 недель после начала или изменения терапии статинами.

## Диагностическая роль
Основная цель терапии — ХС ЛПНП: при очень высоком риске (ИБС) — менее 1,4 ммоль/л и снижение не менее чем на 50 %, при высоком — менее 1,8 ммоль/л.

## Интерпретация результатов
| Результат | Значение |
|---|---|
| в пределах цели | продолжить терапию |
| выше цели | интенсификация терапии |
| ЛПНП 4,9 ммоль/л и выше | тяжёлая гиперхолестеринемия, исключить семейную форму |

## Ограничения
Триглицериды зависят от приёма пищи; при триглицеридах более 4,5 ммоль/л расчётный ЛПНП неточен.

## Последовательность назначения
При первичной оценке риска и в динамике на фоне терапии.

## Связанные заболевания и симптомы
ИБС, артериальная гипертензия, сахарный диабет 2 типа.

## Особенности у отдельных групп
У пациентов с СД2 и поражением органов-мишеней категория риска повышается.

## Связанные документы
- [[PROT-PROTOCOL-003]] Клинический протокол: Ишемическая болезнь сердца (хроническая) — контроль гиполипидемической терапии при ИБС
- [[PROT-SCREENING-003]] Скрининг: Ишемическая болезнь сердца (оценка риска) — оценка сердечно-сосудистого риска
- [[PROT-PROTOCOL-001]] Клинический протокол: Артериальная гипертензия — оценка факторов риска при АГ

## Источники
1. Mach F. et al. 2019 ESC/EAS Guidelines for the management of dyslipidaemias: lipid modification to reduce cardiovascular risk. Eur Heart J. 2020;41:111–188.
2. Vrints C. et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45:3415–3537.

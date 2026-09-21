---
id: DIAG-DIFDIAG-002
schema_version: 2
title: Дифференциальная диагностика головной боли
domain: diag
category: difdiag
body_system:
- nervous
- cardiovascular
- multisystem
tags:
- difdiag
- headache
- redflag
- neurology
urgency: urgent
access_level: professional
target_specialist:
- therapist
- neurologist
- emergency_physician
age_group:
- adult
- elderly
- all_ages
evidence_level: IV
recommendation_class: I
relations:
- target: DIAG-SYMPTOM-001
  type: differential_for
  description: ведущий симптом
- target: DIAG-DISEASE-005
  type: considers
  description: первичная головная боль
- target: DIAG-REDFLAG-002
  type: considers
  description: красный флаг опасной вторичной боли
- target: DIAG-EMERGENCY-002
  type: considers
  description: сосудистая катастрофа в дифференциальном ряду
- target: DIAG-DISEASE-001
  type: considers
  description: перенесено из поля related (схема v1)
- target: DIAG-REDFLAG-001
  type: considers
  description: перенесено из поля related (схема v1)
- target: DIAG-EXAM-001
  type: uses_exam
  description: перенесено из поля related (схема v1)
- target: DIAG-EXAM-009
  type: uses_exam
  description: выведено из машиночитаемого слоя (branches)
- target: DIAG-EMERGENCY-006
  type: considers
  description: выведено из машиночитаемого слоя (branches)
leading_symptom: DIAG-SYMPTOM-001
branches:
- target: DIAG-REDFLAG-002
  supporting:
    any:
    - feature: headache.sudden_onset
    - feature: headache.worst_ever
    - feature: headache.meningism
  key_exam: DIAG-EXAM-009
  prior: low
  urgency: emergency
- target: DIAG-EMERGENCY-002
  supporting:
    any:
    - symptom: DIAG-SYMPTOM-010
    - exam_result: DIAG-EXAM-009
      value: focal_deficit
  key_exam: DIAG-EXAM-009
  prior: low
  urgency: emergency
- target: DIAG-REDFLAG-001
  supporting:
    param: sbp
    op: '>='
    value: 180
  key_exam: DIAG-EXAM-001
  prior: medium
  urgency: emergency
- target: DIAG-EMERGENCY-006
  supporting:
    feature: headache.over_72h
  prior: low
  urgency: emergency
- target: DIAG-DISEASE-005
  supporting:
    at_least:
      n: 2
      of:
      - feature: headache.unilateral
      - feature: headache.pulsating
      - feature: headache.nausea
      - feature: headache.photophobia
      - feature: headache.worse_with_activity
  against:
    any:
    - feature: headache.sudden_onset
    - symptom: DIAG-SYMPTOM-010
  key_exam: DIAG-EXAM-009
  prior: high
  urgency: routine
- target: DIAG-DISEASE-001
  supporting:
    param: sbp
    op: '>='
    value: 140
  key_exam: DIAG-EXAM-001
  prior: medium
  urgency: routine
sources:
- Клинические рекомендации «Ишемический инсульт и транзиторная ишемическая атака у взрослых». Минздрав РФ, 2024.
- Клинические рекомендации «Мигрень». Минздрав РФ, 2024.
clinical_guidelines:
- КР «Ишемический инсульт и ТИА у взрослых», Минздрав РФ, 2024
- КР «Мигрень», Минздрав РФ, 2024
last_medical_review: '2026-04-30'
medical_reviewer: модельная верификация (учебный проект)
author: Инженер знаний №1
version: '2.1'
date_created: '2026-04-30'
date_updated: '2026-09-16'
status: approved
disclaimer: true
---

# Дифференциальная диагностика: головная боль

> ⚕️ **Дисклеймер**: Информация носит справочный характер и предназначена для медицинских специалистов. Не является руководством по самолечению и не заменяет клиническое решение врача.

## Ведущий симптом
[[DIAG-SYMPTOM-001]] Головная боль.

## Ключевые вопросы при сборе анамнеза
1. Когда началась боль и была ли она внезапной? — помогает выявить красные флаги.
2. Изменился ли характер привычной головной боли? — важно для исключения вторичной причины.
3. Есть ли неврологические симптомы? — указывает на необходимость срочной оценки.
4. Есть ли лихорадка, ригидность затылочных мышц, нарушение сознания? — помогает выявить инфекционные и опасные причины.
5. Измерялось ли артериальное давление? — важно при подозрении на гипертонический криз.

## Ключевые данные объективного осмотра
- уровень сознания;
- неврологический статус;
- артериальное давление;
- признаки менингеального синдрома;
- температура тела.

## Дифференциально-диагностическая таблица
| Направление | Поддерживающие признаки | Документ БЗ |
|---|---|---|
| Мигрень | Повторные приступы, светобоязнь, тошнота, возможная аура | [[DIAG-DISEASE-005]] |
| Гипертонический криз | Высокое АД + признаки поражения органов-мишеней | [[DIAG-REDFLAG-001]] |
| ОНМК/кровоизлияние | внезапное начало, неврологический дефицит, нарушение сознания | [[DIAG-EMERGENCY-002]] |
| Инфекционная причина | лихорадка, менингеальные признаки | требуется срочная оценка |

## 🚩 «Красные флаги»
- [[DIAG-REDFLAG-002]] внезапная сильнейшая головная боль;
- неврологический дефицит;
- нарушение сознания;
- лихорадка с менингеальными признаками;
- новый тип боли у пожилого пациента;
- головная боль после травмы.

## Приоритетные диагностические направления
- оценка срочности и жизненных показателей;
- [[DIAG-EXAM-001]] измерение артериального давления;
- неврологический осмотр;
- решение о дополнительных обследованиях врачом.

## Связанные документы
- [[DIAG-SYMPTOM-001]] — головная боль.
- [[DIAG-DISEASE-005]] — мигрень.
- [[DIAG-REDFLAG-002]] — внезапная сильнейшая головная боль.
- [[DIAG-EMERGENCY-002]] — острое нарушение мозгового кровообращения.

## Источники
1. Клинические рекомендации «Ишемический инсульт и транзиторная ишемическая атака у взрослых». Минздрав РФ, 2024.
2. Клинические рекомендации «Мигрень». Минздрав РФ, 2024.

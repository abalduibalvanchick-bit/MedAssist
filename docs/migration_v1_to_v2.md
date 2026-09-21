# Отчёт о миграции базы знаний v1 → v2

Режим: **выполнено**. Дата миграции: 2026-09-16.
Сформировано скриптом `scripts/migrate_v1_to_v2.py`.

## Итоги

- мигрировано карточек: **125**
- пропущено (уже v2): 0
- перенесено папок доменов: 4
- переименовано файлов: 6
- изменено типов связей: 338
- целей перенесено из related в relations: 61
- удалено дублирующих связей: 0
- заменено значений medical_reviewer: 125
- изменено статусов: 11
- карточек с числом источников меньше минимума: 16
- неразрешённых ссылок: 0

## Папки доменов

| Было | Стало |
|---|---|
| `kb/diagnostics` | `kb/diag` |
| `kb/global` | `kb/glb` |
| `kb/protocols` | `kb/prot` |
| `kb/therapy` | `kb/pharm` |

## Переименованные файлы

| Было | Стало |
|---|---|
| `prot/emergency/prot_emergency_hyperglycemia.md` | `prot/emergency/prot_emergency_p_hyperglycemia.md` |
| `prot/emergency/prot_emergency_hypertensive_crisis.md` | `prot/emergency/prot_emergency_p_hypertensive_crisis.md` |
| `prot/emergency/prot_emergency_migrainosus.md` | `prot/emergency/prot_emergency_p_migrainosus.md` |
| `prot/emergency/prot_emergency_severe_pneumonia.md` | `prot/emergency/prot_emergency_p_severe_pneumonia.md` |
| `prot/emergency/prot_emergency_status_asthmaticus.md` | `prot/emergency/prot_emergency_p_status_asthmaticus.md` |
| `prot/emergency/prot_emergency_unstable_angina.md` | `prot/emergency/prot_emergency_p_unstable_angina.md` |

## Преобразование типов связей

| Тип v1 | Тип v2 | Способ | Количество |
|---|---|---|---|
| `used_by_regimen` | `included_in` | алиас v1 | 26 |
| `used_for` | `treats` | алиас v1 | 25 |
| `uses_drugclass` | `includes` | алиас v1 | 22 |
| `uses_regimen` | `recommends` | алиас v1 | 21 |
| `uses_routing` | `next_step` | по паре категорий | 17 |
| `emergency_protocol_for` | `has_emergency_protocol` | обращение направления | 16 |
| `diagnosed_by` | `diagnoses` | обращение направления | 14 |
| `uses_scale` | `assessed_by` | алиас v1 | 14 |
| `uses_routing` | `has_routing` | алиас v1 | 13 |
| `used_by_protocol` | `recommended_by` | алиас v1 | 11 |
| `red_flag_for` | `has_red_flag` | обращение направления | 9 |
| `related` | `red_flag_for` | по паре категорий | 9 |
| `associated_with` | `symptom_of` | по паре категорий | 8 |
| `related` | `diagnosed_by` | по паре категорий | 7 |
| `includes_nonpharm` | `includes` | алиас v1 | 6 |
| `influences_routing` | `next_step` | алиас v1 | 6 |
| `nonpharm_for` | `treats` | алиас v1 | 6 |
| `regimen_for` | `treats` | алиас v1 | 6 |
| `related` | `diagnoses` | по паре категорий | 6 |
| `related` | `has_symptom` | по паре категорий | 6 |
| `related_to` | `routing_for` | по паре категорий | 6 |
| `related_to` | `screening_for` | по паре категорий | 6 |
| `used_by_protocol` | `assesses` | по паре категорий | 6 |
| `uses_protocol` | `checklist_for` | по паре категорий | 6 |
| `uses_redflag` | `has_red_flag` | алиас v1 | 6 |
| `influences_routing` | `assessed_by` | по паре категорий | 5 |
| `related_to` | `emergency_protocol_for` | по паре категорий | 5 |
| `uses_checklist` | `has_checklist` | алиас v1 | 5 |
| `uses_follow_up` | `has_follow_up` | алиас v1 | 5 |
| `uses_redflag` | `emergency_protocol_for` | по паре категорий | 5 |
| `uses_screening` | `has_screening` | алиас v1 | 5 |
| `differentiates_from` | `considered_in` | по паре категорий | 4 |
| `differentiates_from` | `considers` | по паре категорий | 4 |
| `includes_drug` | `includes` | алиас v1 | 4 |
| `red_flag_for` | `considers` | по паре категорий | 4 |
| `related` | `considers` | по паре категорий | 4 |
| `related` | `has_red_flag` | по паре категорий | 4 |
| `related` | `recommends` | по паре категорий | 4 |
| `related` | `uses_exam` | по паре категорий | 4 |
| `belongs_to_class` | `included_in` | алиас v1 | 3 |
| `class_contains_drug` | `includes` | алиас v1 | 3 |
| `diagnosed_by` | `exam_used_in` | по паре категорий | 3 |
| `differentiates_from` | `differential_for` | по паре категорий | 3 |
| `differentiates_from` | `has_differential` | по паре категорий | 3 |
| `drug_in_regimen` | `included_in` | алиас v1 | 3 |
| `related` | `considered_in` | по паре категорий | 3 |
| `complicates` | `complicated_by` | обращение направления | 2 |
| `diagnosed_by` | `uses_exam` | по паре категорий | 2 |
| `differentiates_from` | `red_flag_for` | по паре категорий | 2 |
| `patient_info_for` | `has_patient_info` | обращение направления | 2 |
| `red_flag_for` | `symptom_of` | по паре категорий | 2 |
| `related` | `associated_with` | общая ассоциация | 2 |
| `related` | `complicates` | по паре категорий | 2 |
| `related` | `emergency_protocol_for` | по паре категорий | 2 |
| `related` | `has_routing` | по паре категорий | 2 |
| `uses_drug` | `recommends` | алиас v1 | 2 |
| `adverse_reaction_for` | `adr_caused_by` | алиас v1 | 1 |
| `assesses` | `diagnoses` | по паре категорий | 1 |
| `associated_with` | `has_symptom` | по паре категорий | 1 |
| `associated_with` | `red_flag_for` | по паре категорий | 1 |
| `complicates` | `has_red_flag` | по паре категорий | 1 |
| `differentiates_from` | `has_red_flag` | по паре категорий | 1 |
| `has_symptom` | `symptom_of` | обращение направления | 1 |
| `includes_nonpharm` | `patient_info_for` | по паре категорий | 1 |
| `may_cause_adr` | `causes_adr` | алиас v1 | 1 |
| `related` | `assessed_by` | по паре категорий | 1 |
| `related` | `exam_used_in` | по паре категорий | 1 |
| `related` | `has_checklist` | по паре категорий | 1 |
| `related` | `has_follow_up` | по паре категорий | 1 |
| `related` | `has_screening` | по паре категорий | 1 |
| `related` | `includes` | по паре категорий | 1 |
| `requires_dose_adjustment` | `dose_adjusted_by` | алиас v1 | 1 |
| `used_by_regimen` | `dose_adjustment_for` | по паре категорий | 1 |
| `uses_redflag` | `routing_for` | по паре категорий | 1 |

Способы выбора типа: *алиас v1* — по таблице `legacy_relation_aliases` схемы; *обращение направления* — исходный тип указывал в обратную сторону, использован обратный тип; *по паре категорий* — тип выбран по категориям источника и цели; *общая ассоциация* — специфичный тип для пары категорий не определён.

## Поле medical_reviewer

Внешняя медицинская верификация в учебном проекте не проводилась. Все значения, включая условные ФИО из примеров ТЗ, заменены на единообразную маркировку.

| Было | Количество |
|---|---|
| — | 52 |
| (пусто) | 36 |
| Петрова А.А., к.м.н., пульмонолог | 11 |
| Иванов И.И., д.м.н., кардиолог | 9 |
| Петрова А.А., к.м.н., эндокринолог | 5 |
| Иванов И.И., д.м.н., эндокринолог | 3 |
| Иванов И.И., д.м.н., невролог | 3 |
| Иванов И.И., д.м.н. | 2 |
| Петров С.И., д.м.н., эндокринолог | 1 |
| Петрова А.А., к.м.н. | 1 |
| Сидорова Е.А., д.м.н., нефролог | 1 |
| Петрова А.А., к.м.н., клинический фармаколог | 1 |

## Статусы

| Изменение | Количество |
|---|---|
| approved -> medical_review (нет машиночитаемого слоя) | 11 |

## Исправления evidence_level

- DIAG-EXAM-001: evidence_level='I' удалён (значение класса рекомендаций)
- DIAG-EXAM-003: evidence_level='I' удалён (значение класса рекомендаций)
- DIAG-EXAM-004: evidence_level='I' удалён (значение класса рекомендаций)
- DIAG-EXAM-002: evidence_level='I' удалён (значение класса рекомендаций)

## Карточки с недостаточным числом источников

Требуется дополнить до двух источников: `DIAG-REDFLAG-004`, `DIAG-SYMPTOM-006`, `DIAG-SYMPTOM-007`, `PHARM-DRUGCLASS-010`, `PROT-CHECKLIST-001`, `PROT-CHECKLIST-006`, `PROT-EMERGENCY_P-006`, `PROT-FOLLOW_UP-006`, `PROT-PATIENT_INFO-001`, `PROT-PATIENT_INFO-006`, `PROT-PROTOCOL-001`, `PROT-ROUTING-001`, `PROT-ROUTING-006`, `PROT-SCALE-001`, `PROT-SCREENING-001`, `PROT-SCREENING-006`

<!-- Сгенерировано scripts/generate_docs.py из kb/_schema/schema.yaml. Не редактировать вручную. -->

# Схема YAML-метаданных MedAssist (v2)
Версия схемы: **2**. Источник: `kb/_schema/schema.yaml`.
## Обязательные поля
| Поле | Назначение |
|---|---|
| `id` | Уникальный идентификатор `DOMAIN-CATEGORY-NNN` |
| `schema_version` | Версия схемы карточки (2) |
| `title` | Название карточки |
| `domain` | Код домена: `diag`, `prot`, `glb`, `pharm` |
| `category` | Код категории (см. ниже) |
| `body_system` | Системы организма (список, enum body_system) |
| `tags` | Теги для поиска |
| `urgency` | Срочность (enum urgency) |
| `access_level` | Уровень доступа (enum access_level) |
| `target_specialist` | Целевые специалисты (список, enum target_specialist) |
| `age_group` | Возрастные группы (список, enum age_group) |
| `relations` | Типизированные связи: `target`, `type`, `description` |
| `sources` | Источники, не менее 2 |
| `clinical_guidelines` | Клинические рекомендации (название, год) |
| `last_medical_review` | Дата последней медицинской проверки, YYYY-MM-DD |
| `medical_reviewer` | Рецензент; без внешнего рецензента — «модельная верификация (учебный проект)» |
| `author` | Автор (роль инженера знаний) |
| `version` | Версия карточки |
| `date_created` | Дата создания, YYYY-MM-DD |
| `date_updated` | Дата обновления, YYYY-MM-DD |
| `status` | Статус (enum status); `approved` требует заполненного машиночитаемого слоя |
| `disclaimer` | Всегда `true` |

## Необязательные поля
`icd_10`, `icd_11`, `atc_code`, `inn`, `evidence_level`, `recommendation_class`, `synonyms`, `notes`

## Поля, удалённые в v2
`related` — вычисляется из `relations`.

## Домены и категории
| Домен | Категория | Папка | Название |
|---|---|---|---|
| `diag` | `symptom` | `kb/diag/symptoms/` | Симптом / синдром |
| `diag` | `disease` | `kb/diag/diseases/` | Заболевание |
| `diag` | `exam` | `kb/diag/exams/` | Метод обследования |
| `diag` | `difdiag` | `kb/diag/differential_diagnosis/` | Дифференциальная диагностика |
| `diag` | `redflag` | `kb/diag/red_flags/` | Красный флаг |
| `diag` | `emergency` | `kb/diag/emergencies/` | Неотложное состояние (диагностика) |
| `pharm` | `drug` | `kb/pharm/drugs/` | Лекарственное средство |
| `pharm` | `drugclass` | `kb/pharm/drug_classes/` | Фармакологическая группа |
| `pharm` | `interaction` | `kb/pharm/interactions/` | Лекарственное взаимодействие |
| `pharm` | `adr` | `kb/pharm/adverse_reactions/` | Нежелательная лекарственная реакция |
| `pharm` | `regimen` | `kb/pharm/regimens/` | Терапевтическая схема |
| `pharm` | `dosing` | `kb/pharm/dosing/` | Коррекция доз |
| `pharm` | `nonpharm` | `kb/pharm/nonpharm/` | Нефармакологический метод |
| `prot` | `protocol` | `kb/prot/clinical_protocols/` | Клинический протокол |
| `prot` | `emergency_p` | `kb/prot/emergency/` | Алгоритм неотложной помощи |
| `prot` | `routing` | `kb/prot/routing/` | Маршрутизация пациента |
| `prot` | `scale` | `kb/prot/scales/` | Клиническая шкала |
| `prot` | `screening` | `kb/prot/screening/` | Скрининг |
| `prot` | `patient_info` | `kb/prot/patient_info/` | Памятка для пациента |
| `prot` | `checklist` | `kb/prot/checklists/` | Чек-лист врача |
| `prot` | `follow_up` | `kb/prot/follow_up/` | Наблюдение пациента |
| `prot` | `vaccine` | `kb/prot/vaccines/` | Вакцина |
| `glb` | `glossary` | `kb/glb/glossary/` | Глоссарная статья |
| `glb` | `profile` | `kb/glb/patient_profiles/` | Профиль группы пациентов |
| `glb` | `disclaimer` | `kb/glb/disclaimers/` | Дисклеймер |
| `glb` | `lab` | `kb/glb/lab_reference/` | Лабораторный показатель |
| `glb` | `imaging` | `kb/glb/imaging_reference/` | Инструментальный метод (справочник) |
| `glb` | `anatomy` | `kb/glb/anatomy/` | Анатомо-физиологический раздел |
| `glb` | `cross` | `kb/glb/cross_domain/` | Межпредметный документ |

## Перечисления
- **access_level**: `professional`, `nursing`, `student`, `patient`
- **age_group**: `neonate`, `infant`, `child`, `adolescent`, `adult`, `elderly`, `all_ages`
- **body_system**: `cardiovascular`, `respiratory`, `gastrointestinal`, `nervous`, `endocrine`, `metabolic`, `urinary`, `musculoskeletal`, `immune`, `reproductive`, `hematologic`, `dermatologic`, `multisystem`
- **evidence_level**: `Ia`, `Ib`, `IIa`, `IIb`, `III`, `IV`
- **exam_role**: `confirms`, `excludes`, `supports`, `monitors`, `stratifies`
- **frequency**: `very_common`, `common`, `uncommon`, `rare`
- **interaction_severity**: `critical`, `major`, `moderate`, `minor`
- **prior**: `high`, `medium`, `low`
- **recommendation_class**: `I`, `IIa`, `IIb`, `III`
- **route**: `outpatient`, `urgent_referral`, `emergency`, `hospitalization`
- **status**: `draft`, `medical_review`, `approved`, `deprecated`
- **target_specialist**: `therapist`, `general_practitioner`, `cardiologist`, `pulmonologist`, `gastroenterologist`, `neurologist`, `endocrinologist`, `nephrologist`, `hematologist`, `rheumatologist`, `psychiatrist`, `surgeon`, `oncologist`, `pediatrician`, `obstetrician`, `allergist`, `infectious_disease`, `radiologist`, `dietitian`, `rehabilitation_specialist`, `icu`, `intensivist`, `emergency_physician`, `nursing`, `all_specialties`
- **urgency**: `routine`, `urgent`, `emergency`, `elective`
- **weight**: `1`, `2`, `3`

## Инвариант идентификации
Префикс ID, значение `domain`, имя корневой папки в `kb/` и префикс имени файла обозначают один домен. Категория в ID совпадает с полем `category` и с подпапкой. Пример: `DIAG-DISEASE-001` → `domain: diag`, `category: disease`, файл `kb/diag/diseases/diag_disease_hypertension.md`.

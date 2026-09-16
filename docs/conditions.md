<!-- Сгенерировано scripts/generate_docs.py из kb/_schema/schema.yaml. Не редактировать вручную. -->

# Мини-язык условий
Единый формат условий для машиночитаемого слоя карточек и для правил `kb/rules/`. Условие — YAML-словарь: атом или комбинатор. Оценка трёхзначная: `true`, `false`, `unknown`.

## Атомы
| Запись | Смысл |
|---|---|
| `{symptom: DIAG-SYMPTOM-002}` | у пациента предъявлен симптом |
| `{feature: chest_pain.pressing}` | признак симптома, объявленный в `features` карточки симптома |
| `{param: sbp, op: ">=", value: 180}` | числовой параметр; операторы: `>`, `>=`, `<`, `<=`, `==`, `!=`, `between` |
| `{param: age, op: between, value: [18, 65]}` | диапазон включительно |
| `{param: troponin_positive}` | булев параметр (равен true) |
| `{fact: smoker}` | булев факт о пациенте |
| `{disease: DIAG-DISEASE-001}` | установленный или предполагаемый диагноз |
| `{redflag: DIAG-REDFLAG-001}` | сработавший красный флаг (производный факт) |
| `{emergency: DIAG-EMERGENCY-001}` | распознанное неотложное состояние |
| `{profile: GLB-PROFILE-002}` | принадлежность к профилю пациентов |
| `{scale: PROT-SCALE-001, op: ">=", value: 4}` | вычисленное значение шкалы |
| `{scale_category: PROT-SCALE-001, value: high}` | категория по шкале |
| `{exam_result: DIAG-EXAM-002, value: st_elevation}` | результат обследования из `results` карточки exam |

## Комбинаторы
| Запись | Смысл |
|---|---|
| `{all: [c1, c2]}` | все условия истинны |
| `{any: [c1, c2]}` | хотя бы одно истинно |
| `{not: c}` | отрицание |
| `{at_least: {n: 2, of: [c1, c2, c3]}}` | не менее n из списка |

## Семантика неизвестного
Если данных для оценки атома нет, атом принимает значение `unknown`. `all` с `unknown` даёт `unknown` (если нет `false`), `any` с `unknown` даёт `unknown` (если нет `true`), `not unknown` = `unknown`. Решатель трактует `unknown` как повод запросить уточнение у пользователя, а не как ложь. Режим закрытого мира (`closed_world: true`) переводит все `unknown` в `false`.

## Параметры
| Код | Тип | Единица | Название |
|---|---|---|---|
| `age` | number | лет | Возраст |
| `sbp` | number | мм рт. ст. | Систолическое АД |
| `dbp` | number | мм рт. ст. | Диастолическое АД |
| `hr` | number | уд/мин | Частота сердечных сокращений |
| `rr` | number | в мин | Частота дыхания |
| `spo2` | number | % | Сатурация кислорода |
| `temperature` | number | °C | Температура тела |
| `gcs` | number | баллы | Шкала комы Глазго |
| `egfr` | number | мл/мин/1.73м² | Расчётная СКФ |
| `creatinine` | number | мкмоль/л | Креатинин |
| `glucose` | number | ммоль/л | Глюкоза крови |
| `hba1c` | number | % | Гликированный гемоглобин |
| `bmi` | number | кг/м² | Индекс массы тела |
| `pef_percent` | number | % | ПСВ, % от лучшего |
| `symptom_duration_min` | number | мин | Длительность ведущего симптома |
| `symptom_duration_days` | number | сут | Длительность ведущего симптома |
| `urea` | number | ммоль/л | Мочевина |
| `troponin_positive` | boolean |  | Тропонин выше порога |

## Факты
| Код | Название |
|---|---|
| `smoker` | Курение |
| `pregnant` | Беременность |
| `lactating` | Лактация |
| `immunocompromised` | Иммунокомпрометированный |
| `on_anticoagulants` | Принимает антикоагулянты |
| `nsaid_use` | Принимает НПВС |
| `recent_surgery` | Недавняя операция или травма |
| `confusion` | Спутанность сознания |
| `new_onset` | Впервые возникший симптом |
| `exertional` | Связь с нагрузкой |
| `at_rest` | Возникает в покое |
| `nitrate_unresponsive` | Не купируется нитратами |

## Пример
```yaml
triggers:
  all:
    - symptom: DIAG-SYMPTOM-002        # боль в груди
    - param: symptom_duration_min
      op: ">"
      value: 20
    - any:
        - fact: nitrate_unresponsive
        - fact: at_rest
```

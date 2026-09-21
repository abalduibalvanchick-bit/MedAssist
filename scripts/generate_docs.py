"""Генерирует документацию базы знаний из kb/_schema/schema.yaml.

Запуск из корня проекта:
    python scripts/generate_docs.py

Создаёт/перезаписывает:
    docs/schema.md            — полное описание схемы v2
    docs/metadata_schema.md   — поля метаданных
    docs/link_types.md        — типы связей и обратные пары
    docs/conditions.md        — мини-язык условий

Файлы помечены как сгенерированные; править их вручную не нужно.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.schema import load_schema  # noqa: E402

DOCS = ROOT / "docs"
HEADER = "<!-- Сгенерировано scripts/generate_docs.py из kb/_schema/schema.yaml. Не редактировать вручную. -->\n\n"


def table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |")
    return "\n".join(out) + "\n"


def code(value) -> str:
    return f"`{value}`"


def gen_metadata_schema(schema) -> str:
    lines = [HEADER, "# Схема YAML-метаданных MedAssist (v2)\n",
             f"Версия схемы: **{schema.version}**. Источник: `kb/_schema/schema.yaml`.\n",
             "## Обязательные поля\n"]
    descr = {
        "id": "Уникальный идентификатор `DOMAIN-CATEGORY-NNN`",
        "schema_version": "Версия схемы карточки (2)",
        "title": "Название карточки",
        "domain": "Код домена: " + ", ".join(code(d) for d in schema.domain_codes),
        "category": "Код категории (см. ниже)",
        "body_system": "Системы организма (список, enum body_system)",
        "tags": "Теги для поиска",
        "urgency": "Срочность (enum urgency)",
        "access_level": "Уровень доступа (enum access_level)",
        "target_specialist": "Целевые специалисты (список, enum target_specialist)",
        "age_group": "Возрастные группы (список, enum age_group)",
        "relations": "Типизированные связи: `target`, `type`, `description`",
        "sources": f"Источники, не менее {schema.min_sources}",
        "clinical_guidelines": "Клинические рекомендации (название, год)",
        "last_medical_review": "Дата последней медицинской проверки, YYYY-MM-DD",
        "medical_reviewer": f"Рецензент; без внешнего рецензента — «{schema.model_review_marker}»",
        "author": "Автор (роль инженера знаний)",
        "version": "Версия карточки",
        "date_created": "Дата создания, YYYY-MM-DD",
        "date_updated": "Дата обновления, YYYY-MM-DD",
        "status": "Статус (enum status); `approved` требует заполненного машиночитаемого слоя",
        "disclaimer": "Всегда `true`",
    }
    lines.append(table(["Поле", "Назначение"], [[code(f), descr.get(f, "")] for f in schema.common_required]))
    lines.append("\n## Необязательные поля\n")
    lines.append(", ".join(code(f) for f in schema.common_optional) + "\n")
    lines.append("\n## Поля, удалённые в v2\n")
    lines.append(", ".join(code(f) for f in schema.removed_in_v2) + " — вычисляется из `relations`.\n")
    lines.append("\n## Домены и категории\n")
    rows = []
    for name, cat in schema.categories.items():
        rows.append([code(cat.domain), code(name), code(f"kb/{schema.domains[cat.domain]['folder']}/{cat.folder}/"), cat.title])
    lines.append(table(["Домен", "Категория", "Папка", "Название"], rows))
    lines.append("\n## Перечисления\n")
    for name in sorted(schema.enum_names()):
        lines.append(f"- **{name}**: " + ", ".join(code(v) for v in schema.enum(name)) + "\n")
    lines.append("\n## Инвариант идентификации\n")
    lines.append("Префикс ID, значение `domain`, имя корневой папки в `kb/` и префикс имени файла обозначают один домен. "
                 "Категория в ID совпадает с полем `category` и с подпапкой. Пример: `DIAG-DISEASE-001` → `domain: diag`, "
                 "`category: disease`, файл `kb/diag/diseases/diag_disease_hypertension.md`.\n")
    return "".join(lines)


def gen_link_types(schema) -> str:
    lines = [HEADER, "# Типы связей между документами (v2)\n",
             "Автор записывает связь в одном направлении. Обратная связь материализуется загрузчиком по таблице ниже; "
             "если обе стороны записаны явно, валидатор проверяет их согласованность.\n\n"]
    rows = []
    for name, info in schema.relation_types.items():
        rows.append([code(name), code(info.inverse_name()), ", ".join(info.from_categories) or "любая",
                     ", ".join(info.to_categories) or "любая", "да" if info.symmetric else ""])
    lines.append(table(["Тип", "Обратный", "От (категории)", "К (категории)", "Симметр."], rows))
    lines.append("\n## Соответствие типам схемы v1\n")
    rows = [[code(old), code(new["type"])] for old, new in schema.legacy_relation_aliases.items()]
    lines.append(table(["Тип v1", "Тип v2"], rows))
    return "".join(lines)


def gen_conditions(schema) -> str:
    lines = [HEADER, "# Мини-язык условий\n",
             "Единый формат условий для машиночитаемого слоя карточек и для правил `kb/rules/`. "
             "Условие — YAML-словарь: атом или комбинатор. Оценка трёхзначная: `true`, `false`, `unknown`.\n",
             "\n## Атомы\n"]
    atoms = [
        ["`{symptom: DIAG-SYMPTOM-002}`", "у пациента предъявлен симптом"],
        ["`{feature: chest_pain.pressing}`", "признак симптома, объявленный в `features` карточки симптома"],
        ["`{param: sbp, op: \">=\", value: 180}`", "числовой параметр; операторы: " + ", ".join(code(o) for o in schema.condition_operators)],
        ["`{param: age, op: between, value: [18, 65]}`", "диапазон включительно"],
        ["`{param: troponin_positive}`", "булев параметр (равен true)"],
        ["`{fact: smoker}`", "булев факт о пациенте"],
        ["`{disease: DIAG-DISEASE-001}`", "установленный или предполагаемый диагноз"],
        ["`{redflag: DIAG-REDFLAG-001}`", "сработавший красный флаг (производный факт)"],
        ["`{emergency: DIAG-EMERGENCY-001}`", "распознанное неотложное состояние"],
        ["`{profile: GLB-PROFILE-002}`", "принадлежность к профилю пациентов"],
        ["`{scale: PROT-SCALE-001, op: \">=\", value: 4}`", "вычисленное значение шкалы"],
        ["`{scale_category: PROT-SCALE-001, value: high}`", "категория по шкале"],
        ["`{exam_result: DIAG-EXAM-002, value: st_elevation}`", "результат обследования из `results` карточки exam"],
    ]
    lines.append(table(["Запись", "Смысл"], atoms))
    lines.append("\n## Комбинаторы\n")
    lines.append(table(["Запись", "Смысл"], [
        ["`{all: [c1, c2]}`", "все условия истинны"],
        ["`{any: [c1, c2]}`", "хотя бы одно истинно"],
        ["`{not: c}`", "отрицание"],
        ["`{at_least: {n: 2, of: [c1, c2, c3]}}`", "не менее n из списка"],
    ]))
    lines.append("\n## Семантика неизвестного\n")
    lines.append("Если данных для оценки атома нет, атом принимает значение `unknown`. `all` с `unknown` даёт `unknown` "
                 "(если нет `false`), `any` с `unknown` даёт `unknown` (если нет `true`), `not unknown` = `unknown`. "
                 "Решатель трактует `unknown` как повод запросить уточнение у пользователя, а не как ложь. "
                 "Режим закрытого мира (`closed_world: true`) переводит все `unknown` в `false`.\n")
    lines.append("\n## Параметры\n")
    lines.append(table(["Код", "Тип", "Единица", "Название"],
                       [[code(k), v.get("type", ""), v.get("unit", ""), v.get("label", "")] for k, v in schema.parameters.items()]))
    lines.append("\n## Факты\n")
    lines.append(table(["Код", "Название"], [[code(k), v.get("label", "")] for k, v in schema.facts.items()]))
    lines.append("\n## Пример\n")
    lines.append("```yaml\n"
                 "triggers:\n"
                 "  all:\n"
                 "    - symptom: DIAG-SYMPTOM-002        # боль в груди\n"
                 "    - param: symptom_duration_min\n"
                 "      op: \">\"\n"
                 "      value: 20\n"
                 "    - any:\n"
                 "        - feature: chest_pain.nitrate_unresponsive\n"
                 "        - feature: chest_pain.at_rest\n"
                 "```\n")
    return "".join(lines)


def gen_schema_full(schema) -> str:
    lines = [HEADER, "# Схема базы знаний MedAssist v2\n",
             "Полное описание структуры базы знаний. Разделы «Метаданные», «Связи» и «Условия» продублированы в отдельных "
             "файлах `docs/metadata_schema.md`, `docs/link_types.md`, `docs/conditions.md`.\n",
             "\n## Домены\n"]
    lines.append(table(["Код", "Префикс ID", "Папка", "Название"],
                       [[code(k), code(v["id_prefix"]), code(f"kb/{v['folder']}/"), v["title"]] for k, v in schema.domains.items()]))
    lines.append("\n## Машиночитаемый слой по категориям\n")
    lines.append("Поля, которые решатель читает напрямую. `required_for_approved` — обязательны для `status: approved`.\n")
    for cat_name, cat in schema.categories.items():
        ml = schema.machine_layer(cat_name)
        fields = ml.get("fields", {}) or {}
        lines.append(f"\n### {cat_name} — {cat.title}\n")
        req = ml.get("required_for_approved", []) or []
        lines.append(("Обязательны для approved: " + ", ".join(code(r) for r in req) if req else "Машиночитаемый слой не требуется.") + "\n")
        if fields:
            rows = []
            for fname, fspec in fields.items():
                rows.append([code(fname), code(fspec.get("type", "")), "нет" if fspec.get("optional") else "да", fspec.get("doc", "")])
            lines.append("\n" + table(["Поле", "Тип", "Обяз.", "Описание"], rows))
            for fname, fspec in fields.items():
                item = fspec.get("item")
                if item:
                    lines.append(f"\nСтруктура элемента `{fname}`:\n\n")
                    lines.append(table(["Ключ", "Тип", "Обяз.", "Описание"],
                                       [[code(k), code(v.get("type", "")), "нет" if v.get("optional") else "да", v.get("doc", "")] for k, v in item.items()]))
    lines.append("\n## Правила (kb/rules/*.yaml)\n")
    lines.append("Обязательные поля: " + ", ".join(code(f) for f in schema.rule_required) + ".\n")
    lines.append("Необязательные: " + ", ".join(code(f) for f in schema.rule_optional) + ".\n\n")
    lines.append(table(["Действие", "Цель / значение", "Доп. параметры", "Описание"],
                       [[code(k), code(v.get("target", v.get("value", ""))), ", ".join(code(e) for e in (v.get("extra") or {})), v.get("doc", "")]
                        for k, v in schema.rule_actions.items()]))
    return "".join(lines)


def main() -> None:
    schema = load_schema(ROOT / "kb" / "_schema" / "schema.yaml")
    DOCS.mkdir(exist_ok=True)
    outputs = {
        "schema.md": gen_schema_full(schema),
        "metadata_schema.md": gen_metadata_schema(schema),
        "link_types.md": gen_link_types(schema),
        "conditions.md": gen_conditions(schema),
    }
    for name, text in outputs.items():
        (DOCS / name).write_text(text, encoding="utf-8")
        print(f"записан docs/{name}")


if __name__ == "__main__":
    main()

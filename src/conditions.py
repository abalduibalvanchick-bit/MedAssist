"""Мини-язык условий базы знаний MedAssist.

Условие — дерево из атомов и комбинаторов, описанное в разделе 8 schema.yaml.
Модуль решает три задачи:

1. Статическая проверка условия: корректность формы, допустимость операторов,
   существование параметров, фактов и ссылок на карточки (validate_condition).
2. Оценка условия относительно набора фактов о пациенте (evaluate).
   Логика трёхзначная: TRUE, FALSE, UNKNOWN. UNKNOWN возникает, когда для
   оценки атома не хватает данных; решатель использует его, чтобы запросить
   уточнение, а не молча считать условие ложным.
3. Сбор ссылок условия на карточки и параметры (collect_references) — для
   валидатора и для построения объяснений.

Модуль не знает ничего о медицине: все допустимые имена берутся из схемы.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable

from .schema import Schema, load_schema


class Truth(Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"

    def __bool__(self) -> bool:  # pragma: no cover - защита от неявного bool
        raise TypeError("Truth нельзя приводить к bool неявно; используйте .is_true()")

    def is_true(self) -> bool:
        return self is Truth.TRUE

    def is_false(self) -> bool:
        return self is Truth.FALSE

    def is_unknown(self) -> bool:
        return self is Truth.UNKNOWN


def _not(value: Truth) -> Truth:
    if value is Truth.TRUE:
        return Truth.FALSE
    if value is Truth.FALSE:
        return Truth.TRUE
    return Truth.UNKNOWN


def _all(values: Iterable[Truth]) -> Truth:
    result = Truth.TRUE
    for value in values:
        if value is Truth.FALSE:
            return Truth.FALSE
        if value is Truth.UNKNOWN:
            result = Truth.UNKNOWN
    return result


def _any(values: Iterable[Truth]) -> Truth:
    result = Truth.FALSE
    for value in values:
        if value is Truth.TRUE:
            return Truth.TRUE
        if value is Truth.UNKNOWN:
            result = Truth.UNKNOWN
    return result


class ConditionError(ValueError):
    """Ошибка формы условия."""


# ---------------------------------------------------------------------------
# Факты о пациенте
# ---------------------------------------------------------------------------
@dataclass
class PatientFacts:
    """Всё, что известно о пациенте на момент решения задачи.

    Отсутствие ключа означает «неизвестно». Для булевых коллекций (symptoms,
    features, facts) отсутствие элемента трактуется как «неизвестно», если
    коллекция не объявлена закрытой (closed_world=True), иначе — как «нет».
    """

    symptoms: set[str] = field(default_factory=set)
    features: set[str] = field(default_factory=set)
    facts: dict[str, bool] = field(default_factory=dict)
    params: dict[str, float | bool] = field(default_factory=dict)
    diseases: set[str] = field(default_factory=set)
    red_flags: set[str] = field(default_factory=set)
    emergencies: set[str] = field(default_factory=set)
    profiles: set[str] = field(default_factory=set)
    scales: dict[str, float] = field(default_factory=dict)
    scale_categories: dict[str, str] = field(default_factory=dict)
    exam_results: dict[str, str] = field(default_factory=dict)
    # Явно отрицаемые элементы (пациент сообщил, что симптома нет).
    denied_symptoms: set[str] = field(default_factory=set)
    denied_features: set[str] = field(default_factory=set)
    # Закрытый мир: всё, что не перечислено, считается отсутствующим.
    closed_world: bool = False

    def has_symptom(self, symptom_id: str) -> Truth:
        if symptom_id in self.symptoms:
            return Truth.TRUE
        if symptom_id in self.denied_symptoms or self.closed_world:
            return Truth.FALSE
        return Truth.UNKNOWN

    def has_feature(self, code: str) -> Truth:
        if code in self.features:
            return Truth.TRUE
        if code in self.denied_features or self.closed_world:
            return Truth.FALSE
        return Truth.UNKNOWN

    def has_fact(self, code: str) -> Truth:
        if code in self.facts:
            return Truth.TRUE if self.facts[code] else Truth.FALSE
        return Truth.FALSE if self.closed_world else Truth.UNKNOWN

    def _in_set(self, collection: set[str], item: str) -> Truth:
        if item in collection:
            return Truth.TRUE
        return Truth.FALSE if self.closed_world else Truth.UNKNOWN


# ---------------------------------------------------------------------------
# Разбор и статическая проверка
# ---------------------------------------------------------------------------
_COMPARISONS: dict[str, Callable[[float, Any], bool]] = {
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "between": lambda a, b: b[0] <= a <= b[1],
}


def _atom_kind(node: dict[str, Any], schema: Schema) -> str | None:
    """Возвращает тип атома или None, если узел не атом."""
    for atom in schema.condition_atoms:
        if atom in node:
            return atom
    return None


def _combinator_kind(node: dict[str, Any], schema: Schema) -> str | None:
    for comb in schema.condition_combinators:
        if comb in node:
            return comb
    return None


@dataclass
class ConditionIssue:
    path: str
    message: str


def validate_condition(
    node: Any,
    schema: Schema | None = None,
    *,
    known_ids: set[str] | None = None,
    known_features: set[str] | None = None,
    known_exam_values: dict[str, set[str]] | None = None,
    known_scale_categories: dict[str, set[str]] | None = None,
    path: str = "$",
) -> list[ConditionIssue]:
    """Статически проверяет условие. Возвращает список проблем (пустой — ок).

    known_* передаёт валидатор, когда база уже загружена; без них проверяется
    только форма условия и словарные имена из схемы.
    """
    schema = schema or load_schema()
    issues: list[ConditionIssue] = []

    def add(msg: str, p: str = path) -> None:
        issues.append(ConditionIssue(path=p, message=msg))

    if not isinstance(node, dict) or not node:
        add("Условие должно быть непустым словарём")
        return issues

    comb = _combinator_kind(node, schema)
    atom = _atom_kind(node, schema)
    if comb and atom:
        add(f"Узел не может быть одновременно атомом ({atom}) и комбинатором ({comb})")
        return issues

    if comb:
        extra = set(node) - {comb}
        if extra:
            add(f"Лишние ключи у комбинатора {comb}: {sorted(extra)}")
        body = node[comb]
        if comb in ("all", "any"):
            if not isinstance(body, list) or not body:
                add(f"{comb} требует непустой список условий")
            else:
                for i, child in enumerate(body):
                    issues.extend(validate_condition(child, schema, known_ids=known_ids, known_features=known_features,
                                                     known_exam_values=known_exam_values,
                                                     known_scale_categories=known_scale_categories,
                                                     path=f"{path}.{comb}[{i}]"))
        elif comb == "not":
            issues.extend(validate_condition(body, schema, known_ids=known_ids, known_features=known_features,
                                             known_exam_values=known_exam_values,
                                             known_scale_categories=known_scale_categories, path=f"{path}.not"))
        elif comb == "at_least":
            if not isinstance(body, dict) or "n" not in body or "of" not in body:
                add("at_least требует ключи n и of")
            else:
                n, of = body["n"], body["of"]
                if not isinstance(n, int) or n < 1:
                    add("at_least.n должно быть целым >= 1")
                if not isinstance(of, list) or not of:
                    add("at_least.of должно быть непустым списком")
                elif isinstance(n, int) and n > len(of):
                    add(f"at_least.n={n} больше числа альтернатив {len(of)}")
                else:
                    for i, child in enumerate(of):
                        issues.extend(validate_condition(child, schema, known_ids=known_ids, known_features=known_features,
                                                         known_exam_values=known_exam_values,
                                                         known_scale_categories=known_scale_categories,
                                                         path=f"{path}.at_least.of[{i}]"))
        return issues

    if not atom:
        add(f"Неизвестный узел условия: ключи {sorted(node)}")
        return issues

    value = node[atom]
    allowed_keys = {atom}
    if atom in ("param", "scale"):
        allowed_keys |= {"op", "value"}
    elif atom in ("scale_category", "exam_result"):
        allowed_keys |= {"value"}
    extra = set(node) - allowed_keys
    if extra:
        add(f"Лишние ключи у атома {atom}: {sorted(extra)}")

    if atom == "param":
        if value not in schema.parameters:
            add(f"Неизвестный параметр {value}")
        _check_comparison(node, schema, add, is_boolean=schema.parameters.get(value, {}).get("type") == "boolean")
    elif atom == "scale":
        _check_id(value, ("scale",), known_ids, schema, add)
        _check_comparison(node, schema, add)
    elif atom == "fact":
        if value not in schema.facts:
            add(f"Неизвестный факт {value}")
    elif atom == "feature":
        if not isinstance(value, str) or "." not in value:
            add(f"Код признака должен иметь вид <symptom>.<feature>: {value!r}")
        elif known_features is not None and value not in known_features:
            add(f"Признак {value} не объявлен ни в одной карточке симптома")
    elif atom == "scale_category":
        _check_id(value, ("scale",), known_ids, schema, add)
        if "value" not in node:
            add("scale_category требует ключ value")
        elif known_scale_categories is not None and value in known_scale_categories \
                and node["value"] not in known_scale_categories[value]:
            add(f"Категория {node['value']} не объявлена в шкале {value}")
    elif atom == "exam_result":
        _check_id(value, ("exam",), known_ids, schema, add)
        if "value" not in node:
            add("exam_result требует ключ value")
        elif known_exam_values is not None and value in known_exam_values \
                and node["value"] not in known_exam_values[value]:
            add(f"Значение {node['value']} не объявлено в results обследования {value}")
    else:
        expected = {
            "symptom": ("symptom",),
            "disease": ("disease",),
            "redflag": ("redflag",),
            "emergency": ("emergency",),
            "profile": ("profile",),
        }[atom]
        _check_id(value, expected, known_ids, schema, add)
    return issues


def _check_comparison(node: dict[str, Any], schema: Schema, add: Callable[[str], None], *, is_boolean: bool = False) -> None:
    op = node.get("op")
    if is_boolean:
        if "value" in node and not isinstance(node["value"], bool):
            add("Булев параметр сравнивается только с true/false")
        if op not in (None, "==", "!="):
            add(f"Для булева параметра допустимы только == и !=, получено {op}")
        return
    if op not in schema.condition_operators:
        add(f"Недопустимый оператор {op!r}; допустимо: {schema.condition_operators}")
        return
    value = node.get("value")
    if op == "between":
        if not (isinstance(value, list) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value)):
            add("between требует value вида [min, max]")
        elif value[0] > value[1]:
            add("between: min больше max")
    elif not isinstance(value, (int, float)) or isinstance(value, bool):
        add(f"Числовое сравнение требует числовое value, получено {value!r}")


def _check_id(value: Any, categories: tuple[str, ...], known_ids: set[str] | None, schema: Schema, add: Callable[[str], None]) -> None:
    if not isinstance(value, str) or not schema.id_pattern.match(value):
        add(f"Некорректный идентификатор {value!r}")
        return
    cat_code = value.split("-")[1].lower()
    if cat_code not in categories:
        add(f"Идентификатор {value} должен указывать на карточку категории {list(categories)}")
    if known_ids is not None and value not in known_ids:
        add(f"Ссылка на несуществующую карточку {value}")


# ---------------------------------------------------------------------------
# Сбор ссылок
# ---------------------------------------------------------------------------
@dataclass
class ConditionRefs:
    card_ids: set[str] = field(default_factory=set)
    params: set[str] = field(default_factory=set)
    facts: set[str] = field(default_factory=set)
    features: set[str] = field(default_factory=set)


def collect_references(node: Any, schema: Schema | None = None, refs: ConditionRefs | None = None) -> ConditionRefs:
    """Собирает все идентификаторы, параметры, факты и признаки, на которые ссылается условие."""
    schema = schema or load_schema()
    refs = refs or ConditionRefs()
    if not isinstance(node, dict):
        return refs
    comb = _combinator_kind(node, schema)
    if comb:
        body = node[comb]
        children = body if comb in ("all", "any") else [body] if comb == "not" else body.get("of", []) if isinstance(body, dict) else []
        for child in children:
            collect_references(child, schema, refs)
        return refs
    atom = _atom_kind(node, schema)
    if atom is None:
        return refs
    value = node[atom]
    if atom == "param":
        refs.params.add(str(value))
    elif atom == "fact":
        refs.facts.add(str(value))
    elif atom == "feature":
        refs.features.add(str(value))
    else:
        refs.card_ids.add(str(value))
    return refs


# ---------------------------------------------------------------------------
# Оценка
# ---------------------------------------------------------------------------
@dataclass
class EvalTrace:
    """Запись о вычислении одного узла условия — основа объяснений решателя."""

    path: str
    node: dict[str, Any]
    result: Truth
    detail: str = ""


def evaluate(
    node: Any,
    facts: PatientFacts,
    schema: Schema | None = None,
    *,
    trace: list[EvalTrace] | None = None,
    path: str = "$",
) -> Truth:
    """Оценивает условие относительно фактов о пациенте (трёхзначная логика)."""
    schema = schema or load_schema()

    def record(result: Truth, detail: str = "") -> Truth:
        if trace is not None:
            trace.append(EvalTrace(path=path, node=node, result=result, detail=detail))
        return result

    if not isinstance(node, dict):
        raise ConditionError(f"Условие должно быть словарём: {node!r}")

    comb = _combinator_kind(node, schema)
    if comb:
        body = node[comb]
        if comb == "all":
            return record(_all(evaluate(c, facts, schema, trace=trace, path=f"{path}.all[{i}]") for i, c in enumerate(body)))
        if comb == "any":
            return record(_any(evaluate(c, facts, schema, trace=trace, path=f"{path}.any[{i}]") for i, c in enumerate(body)))
        if comb == "not":
            return record(_not(evaluate(body, facts, schema, trace=trace, path=f"{path}.not")))
        if comb == "at_least":
            n = int(body["n"])
            results = [evaluate(c, facts, schema, trace=trace, path=f"{path}.at_least.of[{i}]") for i, c in enumerate(body["of"])]
            trues = sum(1 for r in results if r is Truth.TRUE)
            unknowns = sum(1 for r in results if r is Truth.UNKNOWN)
            if trues >= n:
                return record(Truth.TRUE, f"{trues} из {len(results)} истинны")
            if trues + unknowns < n:
                return record(Truth.FALSE, f"истинных {trues}, неизвестных {unknowns}, нужно {n}")
            return record(Truth.UNKNOWN, f"истинных {trues}, неизвестных {unknowns}, нужно {n}")
        raise ConditionError(f"Неизвестный комбинатор {comb}")

    atom = _atom_kind(node, schema)
    if atom is None:
        raise ConditionError(f"Неизвестный узел условия: {sorted(node)}")
    value = node[atom]

    if atom == "symptom":
        return record(facts.has_symptom(value))
    if atom == "feature":
        return record(facts.has_feature(value))
    if atom == "fact":
        return record(facts.has_fact(value))
    if atom == "disease":
        return record(facts._in_set(facts.diseases, value))
    if atom == "redflag":
        return record(facts._in_set(facts.red_flags, value))
    if atom == "emergency":
        return record(facts._in_set(facts.emergencies, value))
    if atom == "profile":
        return record(facts._in_set(facts.profiles, value))
    if atom == "param":
        if value not in facts.params:
            return record(Truth.UNKNOWN, f"параметр {value} не задан")
        actual = facts.params[value]
        if isinstance(actual, bool) or schema.parameters.get(value, {}).get("type") == "boolean":
            expected = node.get("value", True)
            op = node.get("op", "==")
            ok = (bool(actual) == bool(expected)) if op == "==" else (bool(actual) != bool(expected))
            return record(Truth.TRUE if ok else Truth.FALSE, f"{value}={actual}")
        ok = _COMPARISONS[node["op"]](float(actual), node["value"])
        return record(Truth.TRUE if ok else Truth.FALSE, f"{value}={actual} {node['op']} {node['value']}")
    if atom == "scale":
        if value not in facts.scales:
            return record(Truth.UNKNOWN, f"шкала {value} не вычислена")
        ok = _COMPARISONS[node["op"]](float(facts.scales[value]), node["value"])
        return record(Truth.TRUE if ok else Truth.FALSE, f"{value}={facts.scales[value]} {node['op']} {node['value']}")
    if atom == "scale_category":
        if value not in facts.scale_categories:
            return record(Truth.UNKNOWN, f"категория шкалы {value} не вычислена")
        ok = facts.scale_categories[value] == node["value"]
        return record(Truth.TRUE if ok else Truth.FALSE, f"{value}: {facts.scale_categories[value]}")
    if atom == "exam_result":
        if value not in facts.exam_results:
            return record(Truth.UNKNOWN, f"результат {value} неизвестен")
        ok = facts.exam_results[value] == node["value"]
        return record(Truth.TRUE if ok else Truth.FALSE, f"{value}: {facts.exam_results[value]}")
    raise ConditionError(f"Атом {atom} не поддерживается интерпретатором")


def missing_inputs(node: Any, facts: PatientFacts, schema: Schema | None = None) -> ConditionRefs:
    """Возвращает ссылки атомов, оценка которых дала UNKNOWN — что нужно уточнить у пользователя."""
    schema = schema or load_schema()
    trace: list[EvalTrace] = []
    evaluate(node, facts, schema, trace=trace)
    missing = ConditionRefs()
    for entry in trace:
        if entry.result is not Truth.UNKNOWN:
            continue
        atom = _atom_kind(entry.node, schema)
        if atom is None:
            continue
        collect_references(entry.node, schema, missing)
    return missing


def describe(node: Any, schema: Schema | None = None, labels: dict[str, str] | None = None) -> str:
    """Человекочитаемое описание условия на русском (для объяснений и документации)."""
    schema = schema or load_schema()
    labels = labels or {}

    def name(value: str) -> str:
        return labels.get(value, value)

    if not isinstance(node, dict):
        return str(node)
    comb = _combinator_kind(node, schema)
    if comb == "all":
        return "(" + " И ".join(describe(c, schema, labels) for c in node["all"]) + ")"
    if comb == "any":
        return "(" + " ИЛИ ".join(describe(c, schema, labels) for c in node["any"]) + ")"
    if comb == "not":
        return "НЕ " + describe(node["not"], schema, labels)
    if comb == "at_least":
        body = node["at_least"]
        return f"не менее {body['n']} из [" + "; ".join(describe(c, schema, labels) for c in body["of"]) + "]"
    atom = _atom_kind(node, schema)
    value = node.get(atom)
    if atom == "param":
        label = schema.parameters.get(value, {}).get("label", value)
        unit = schema.parameters.get(value, {}).get("unit", "")
        if node.get("op") == "between":
            return f"{label} в диапазоне {node['value'][0]}–{node['value'][1]} {unit}".strip()
        if "op" in node:
            return f"{label} {node['op']} {node['value']} {unit}".strip()
        return f"{label} = {node.get('value', True)}"
    if atom == "fact":
        return schema.facts.get(value, {}).get("label", value)
    if atom == "scale":
        return f"{name(value)} {node['op']} {node['value']}"
    if atom in ("scale_category", "exam_result"):
        return f"{name(value)}: {node['value']}"
    prefixes = {"symptom": "симптом", "feature": "признак", "disease": "диагноз", "redflag": "красный флаг",
                "emergency": "неотложное состояние", "profile": "профиль"}
    return f"{prefixes.get(atom, atom)} «{name(value)}»"

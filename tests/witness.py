"""Построение «свидетеля» условия: описания пациента, на котором условие истинно.

Используется тестами достижимости: для каждого правила, красного флага и
неотложного состояния строится пациент, и проверяется, что решатель
действительно приходит к этому выводу. Так обнаруживаются правила, которые
не могут сработать никогда (опечатка в коде признака, недостижимый порог,
противоречивое условие), даже если ни один сценарий их не затрагивает.

Свидетель строится жадно: для all — все ветви, для any и at_least — первые
выполнимые ветви, для not — отрицание атома (отрицаемый симптом, ложный факт,
значение параметра вне порога). Ссылки на выводимые сущности (красный флаг,
неотложное состояние, профиль, рабочий диагноз, шкала) разворачиваются через
условия соответствующих карточек.
"""

from __future__ import annotations

import copy
from typing import Any

from src.conditions import compare


class Unsatisfiable(Exception):
    pass


def _number_for_all(spec: dict[str, Any], rules: list[tuple[str, Any, bool]]) -> float:
    """Значение параметра, удовлетворяющее всем ограничениям (op, value, отрицание)."""
    lo, hi = spec.get("min", 0), spec.get("max", 1000)
    candidates = {lo, hi}
    for op, value, _ in rules:
        for threshold in (value if isinstance(value, list) else [value]):
            for delta in (0, 1, -1, 0.1, -0.1, 10, -10):
                candidates.add(round(threshold + delta, 1))
    for c in sorted(candidates):
        if lo <= c <= hi and all(compare(c, op, value) != negate for op, value, negate in rules):
            return int(c) if float(c).is_integer() else c
    raise Unsatisfiable(f"нет значения в [{lo}, {hi}] для ограничений {rules}")


class Witness:
    def __init__(self, kb) -> None:
        self.kb = kb
        self.schema = kb.schema
        self.patient: dict[str, Any] = {"age": 50, "params": {}, "facts": {}}
        # Все ограничения на числовой параметр: значение подбирается так, чтобы выполнялись все.
        self.constraints: dict[str, list[tuple[str, Any, bool]]] = {}

    # ------------------------------------------------------------ helpers
    def _list(self, key: str) -> list:
        return self.patient.setdefault(key, [])

    def _set_param(self, name: str, value: Any) -> None:
        params = self.patient["params"]
        if name == "age":
            self.patient["age"] = value
            return
        if name in params and params[name] != value:
            raise Unsatisfiable(f"конфликт значений {name}")
        params[name] = value

    # ------------------------------------------------------------ main
    def satisfy(self, node: Any, negate: bool = False) -> None:
        if not isinstance(node, dict):
            raise Unsatisfiable(f"не условие: {node!r}")
        if "all" in node:
            children = node["all"]
            if negate:
                self._satisfy_any([{"not": c} for c in children])
            else:
                for c in children:
                    self.satisfy(c)
            return
        if "any" in node:
            if negate:
                for c in node["any"]:
                    self.satisfy(c, negate=True)
            else:
                self._satisfy_any(node["any"])
            return
        if "not" in node:
            self.satisfy(node["not"], negate=not negate)
            return
        if "at_least" in node:
            body = node["at_least"]
            if negate:
                for c in body["of"]:
                    self.satisfy(c, negate=True)
                return
            done = 0
            for c in body["of"]:
                snapshot = copy.deepcopy(self.patient)
                try:
                    self.satisfy(c)
                    done += 1
                except Unsatisfiable:
                    self.patient = snapshot
                if done >= body["n"]:
                    return
            raise Unsatisfiable("at_least не выполнить")
        self._atom(node, negate)

    def _satisfy_any(self, children: list) -> None:
        last = None
        for c in children:
            snapshot = copy.deepcopy(self.patient)
            try:
                self.satisfy(c)
                return
            except Unsatisfiable as exc:
                self.patient = snapshot
                last = exc
        raise Unsatisfiable(f"ни одна ветвь any не выполнима: {last}")

    def _atom(self, node: dict[str, Any], negate: bool) -> None:
        kb = self.kb
        if "symptom" in node:
            sid = node["symptom"]
            target, other = ("denied_symptoms", "symptoms") if negate else ("symptoms", "denied_symptoms")
            if sid in self.patient.get(other, []):
                raise Unsatisfiable(f"симптом {sid} и есть, и нет")
            if negate and any(kb.feature_owner.get(f) == sid for f in self.patient.get("features", [])):
                raise Unsatisfiable(f"признак симптома {sid} уже указан")
            if sid not in self._list(target):
                self._list(target).append(sid)
            return
        if "feature" in node:
            code = node["feature"]
            target, other = ("denied_features", "features") if negate else ("features", "denied_features")
            if code in self.patient.get(other, []):
                raise Unsatisfiable(f"признак {code} и есть, и нет")
            if not negate and kb.feature_owner.get(code) in self.patient.get("denied_symptoms", []):
                raise Unsatisfiable(f"симптом признака {code} отрицается")
            if code not in self._list(target):
                self._list(target).append(code)
            return
        if "fact" in node:
            name = node["fact"]
            value = node.get("value", True) != negate
            if self.patient["facts"].get(name, value) != value:
                raise Unsatisfiable(f"конфликт факта {name}")
            self.patient["facts"][name] = value
            return
        if "known" in node:
            if negate:
                return  # «не сообщено» — просто не задаём значение
            name = node["known"]
            if name in self.schema.parameters:
                spec = self.schema.parameters[name]
                self._set_param(name, True if spec.get("type") == "boolean" else spec.get("min", 1))
            else:
                self.patient["facts"].setdefault(name, False)
            return
        if "param" in node:
            name = node["param"]
            spec = self.schema.parameters.get(name, {})
            if spec.get("type") == "boolean":
                expected = node.get("value", True)
                if node.get("op", "==") == "!=":
                    expected = not expected
                self._set_param(name, bool(expected) != negate)
                return
            rules = self.constraints.setdefault(name, []) + [(node["op"], node["value"], negate)]
            value = _number_for_all(spec, rules)
            self.constraints[name] = rules
            if name == "age":
                self.patient["age"] = value
            else:
                self.patient["params"][name] = value
            return
        if "exam_result" in node:
            if negate:
                card = kb.get(node["exam_result"])
                others = [r["value"] for r in card.metadata.get("results") or [] if r["value"] != node["value"]]
                self.patient.setdefault("exam_results", {})[node["exam_result"]] = others[0]
            else:
                self.patient.setdefault("exam_results", {})[node["exam_result"]] = node["value"]
            return
        if negate:
            # Отрицание выводимой сущности обеспечивается тем, что её условие не выполнено;
            # жадный свидетель не добавляет ничего, что её вызывает.
            return
        if "disease" in node:
            if node["disease"] not in self._list("diseases"):
                self._list("diseases").append(node["disease"])
            return
        if "redflag" in node:
            self.satisfy(kb.get(node["redflag"]).metadata["triggers"])
            return
        if "emergency" in node:
            self.satisfy(kb.get(node["emergency"]).metadata["criteria"])
            return
        if "profile" in node:
            self.satisfy(kb.get(node["profile"]).metadata["criteria"])
            return
        if "scale" in node or "scale_category" in node:
            raise Unsatisfiable("шкалы свидетель не строит")
        raise Unsatisfiable(f"атом не поддержан: {node}")


def witness_for(condition: dict[str, Any], kb) -> dict[str, Any]:
    w = Witness(kb)
    w.satisfy(condition)
    patient = w.patient
    patient["params"] = {k: v for k, v in patient["params"].items()}
    if not patient["params"]:
        patient.pop("params")
    if not patient["facts"]:
        patient.pop("facts")
    return {"patient": patient}

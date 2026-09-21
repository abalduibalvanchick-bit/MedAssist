"""Извлечение ссылок на карточки из машиночитаемого слоя.

Поля машиночитаемого слоя с типом id(...) или list[id(...)] могут иметь в схеме
атрибут implies — тип связи, которая должна отражать эту ссылку в графе
relations. Модуль обходит слой по спецификации схемы и возвращает все такие
ссылки. Используется валидатором (проверка согласованности слоя и графа) и
скриптом синхронизации связей.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

from .schema import Schema


@dataclass(frozen=True)
class MachineRef:
    path: str
    target: str
    implies: str | None


def iter_machine_refs(meta: dict[str, Any], schema: Schema, category: str) -> Iterator[MachineRef]:
    fields = schema.machine_fields(category)
    for name, spec in fields.items():
        if name in meta:
            yield from _walk(meta[name], spec or {}, name)


def _walk(value: Any, spec: dict[str, Any], path: str) -> Iterator[MachineRef]:
    ftype = str(spec.get("type", ""))
    implies = spec.get("implies")
    if value is None:
        return
    if ftype.startswith("list["):
        inner = ftype[5:-1]
        if not isinstance(value, list):
            return
        for i, item in enumerate(value):
            if inner == "object":
                yield from _walk_object(item, spec.get("item") or {}, f"{path}[{i}]")
            elif inner.startswith("id") and isinstance(item, str):
                yield MachineRef(path=f"{path}[{i}]", target=item, implies=implies)
        return
    if ftype == "object":
        yield from _walk_object(value, spec.get("item") or {}, path)
        return
    if ftype.startswith("id") and isinstance(value, str):
        yield MachineRef(path=path, target=value, implies=implies)


def _walk_object(value: Any, item_spec: dict[str, Any], path: str) -> Iterator[MachineRef]:
    if not isinstance(value, dict):
        return
    for key, sub_spec in item_spec.items():
        if key in value:
            yield from _walk(value[key], sub_spec or {}, f"{path}.{key}")

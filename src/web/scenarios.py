"""Каталог примеров и регрессионных сценариев решателя."""

from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_LABELS = {
    "pneumonia": "Кашель и лихорадка",
    "pneumonia_no_urea": "Кашель и неполные данные",
    "chest_pain_acs": "Боль в груди",
    "migraine": "Головная боль",
    "pneumonia_elderly": "Лихорадка и кашель у пожилой пациентки",
    "stroke": "Асимметрия лица и слабость в руке",
    "child_refusal": "Случай вне возрастной области применения",
}
QUICK_EXAMPLES = ("pneumonia", "pneumonia_no_urea", "chest_pain_acs", "migraine")


@lru_cache(maxsize=1)
def scenarios():
    cases = {}
    for path in sorted((ROOT / "examples").glob("*.yaml")):
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
        info = content.get("scenario", {})
        cases[path.stem] = {
            "id": path.stem,
            "title": info.get("title", EXAMPLE_LABELS.get(path.stem, path.stem.replace("_", " "))),
            "group": info.get("group", "example"),
            "note": info.get("note"),
            "source": info.get("source"),
            "request": {"patient": content["patient"]},
        }

    for path in sorted((ROOT / "tests" / "cases").glob("*.yaml")):
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
        cases[path.stem] = {
            "id": path.stem,
            "code": content["id"],
            "title": content["title"],
            "group": content["group"],
            "request": {"patient": content["patient"]},
            "role": content.get("role", "professional"),
        }
    return cases


def scenario_list():
    return [{key: value for key, value in case.items() if key in {"id", "code", "title", "group"}}
            for case in scenarios().values()]

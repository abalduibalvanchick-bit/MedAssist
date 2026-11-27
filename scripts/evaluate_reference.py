"""Сравнить поиск на размеченных вопросах или проверить реальный вызов Ollama."""

import argparse
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.reference_embeddings import OllamaRanker
from src.reference import answer_reference, ollama_generator, search_reference


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ollama-model", help="Дополнительно потребовать проверенную цитату от локальной модели")
    parser.add_argument("--ollama-embed-model", help="Проверить ранжирование через локальный /api/embed")
    args = parser.parse_args()
    cases = yaml.safe_load((ROOT / "tests/reference_cases.yaml").read_text(encoding="utf-8"))
    totals = []
    print("| Сценарий | Ожидаемая карточка | Ранг BM25 | Ранг BM25 + векторы |")
    print("|---|---|---:|---:|")
    for method in ("bm25", "hybrid"):
        rows = []
        for name, role, question, target in cases:
            ids = [s["id"] for s in search_reference(question, role, method=method)]
            rank = ids.index(target) + 1 if target in ids else 0
            rows.append((rank, not ids))
        totals.append(rows)
    for case, baseline, hybrid in zip(cases, *totals):
        def display(row):
            return str(row[0]) if row[0] else ("нет выдачи" if row[1] else "вне топ-5")
        print(f"| {case[0]} | {case[3] or 'нет ответа'} | {display(baseline)} | {display(hybrid)} |")
    for label, rows in zip(("BM25", "Гибрид"), totals):
        ranks = [row[0] for case, row in zip(cases, rows) if case[3]]
        refusals = [row[1] for case, row in zip(cases, rows) if not case[3]]
        print(f"\n{label} — первая позиция {ranks.count(1)}/{len(ranks)}, "
              f"топ-5 {sum(bool(rank) for rank in ranks)}/{len(ranks)}, "
              f"корректный отказ {sum(refusals)}/{len(refusals)}.")
    ok = all(rank if case[3] else empty for case, (rank, empty) in zip(cases, totals[1]))
    if args.ollama_embed_model:
        sources = search_reference("Из чего состоит шкала CURB-65?", ranker=OllamaRanker(args.ollama_embed_model))
        semantic_ok = sources and sources[0]["retrieval"] == "hybrid_semantic" and any(
            source["id"] == "PROT-SCALE-004" for source in sources)
        print("Смысловой поиск через Ollama:", "пройден" if semantic_ok else "не пройден")
        ok = ok and semantic_ok
    if args.ollama_model:
        reply = answer_reference("Из чего состоит шкала CURB-65?", generator=ollama_generator(args.ollama_model))
        if reply["mode"] != "generated" or not reply["answer"]:
            print("Проверенная цитата модели не получена. Проверьте локальный сервис и имя модели.", file=sys.stderr)
            ok = False
        else:
            claim = reply["answer"][0]
            print("\nПроверенная цитата модели:", claim["text"], "—", reply["sources"][claim["source"] - 1]["id"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

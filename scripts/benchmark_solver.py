"""Замер стоимости обхода правил на фиксированном учебном сценарии."""

from dataclasses import replace
from pathlib import Path
from statistics import median
import sys
from time import perf_counter_ns

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.solver import load_default_kb, solve


def main() -> None:
    kb = load_default_kb()
    request = yaml.safe_load((ROOT / "examples/pneumonia_no_urea.yaml").read_text(encoding="utf-8"))
    base = solve(request, kb=kb, include_trace=False)
    print("| Правил | Медиана, мс | P95, мс |")
    print("| ---: | ---: | ---: |")
    for multiplier in (1, 2, 4, 8):
        extras = [
            replace(rule, id=f"BENCH-{index}-{rule.id}", domain="benchmark",
                    condition={"all": [{"known": "age"}, {"not": {"known": "age"}}]}, actions=())
            for index in range(1, multiplier)
            for rule in kb.rules
        ]
        simulated_kb = replace(kb, rules=[*kb.rules, *extras])
        samples = []
        for _ in range(60):
            start = perf_counter_ns()
            result = solve(request, kb=simulated_kb, include_trace=False)
            samples.append((perf_counter_ns() - start) / 1_000_000)
            assert result["status"] == base["status"] and result["routing"] == base["routing"]
        percentile_95 = sorted(samples)[56]
        print(f"| {len(simulated_kb.rules)} | {median(samples):.2f} | {percentile_95:.2f} |")


if __name__ == "__main__":
    main()

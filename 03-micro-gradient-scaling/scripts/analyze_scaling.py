#!/usr/bin/env python3
"""
===============================================================================
MICRO-GRADIENT SCALING ANALYZER (EXP 03)
Evaluates scaling phase boundaries across problem sizes against SABRE O3 and TKET.
Strictly validates CSV schema and cross-verifies abstract_2q_operations ==
logical_abstract_2q_gates + routing_induced_2q_overhead.
===============================================================================
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

REQUIRED_COLUMNS = {
    "benchmark",
    "compiler",
    "Hellinger_fidelity",
    "abstract_2q_operations",
    "logical_abstract_2q_gates",
    "routing_induced_2q_overhead",
}


def parse_benchmark_name(name: str):
    """Extracts family and N from strings like QAOA_9_MAXCUT."""
    match = re.match(r"([A-Za-z_]+)_(\d+)", name)
    if match:
        fam = match.group(1).replace("_MAXCUT", "").replace("_NONTRIVIAL", "")
        return fam, int(match.group(2))
    return name, 0


def _require_nonempty(row: dict, col: str, row_num: int) -> str:
    val = row.get(col)
    if val is None or str(val).strip() == "":
        raise ValueError(f"Row {row_num}: missing or empty required column '{col}'")
    return str(val).strip()


def load_matched_records(csv_path: Path):
    raw_data = defaultdict(dict)
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Empty CSV header in {csv_path}")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise KeyError(
                f"CSV schema mismatch in {csv_path}: missing required column(s) {sorted(missing)}"
            )

        for row_num, row in enumerate(reader, start=2):
            bench = _require_nonempty(row, "benchmark", row_num)
            comp = _require_nonempty(row, "compiler", row_num).upper()
            fid = float(_require_nonempty(row, "Hellinger_fidelity", row_num))
            abs_2q = int(float(_require_nonempty(row, "abstract_2q_operations", row_num)))
            logical_2q = int(float(_require_nonempty(row, "logical_abstract_2q_gates", row_num)))
            overhead_2q = int(float(_require_nonempty(row, "routing_induced_2q_overhead", row_num)))

            if abs_2q != logical_2q + overhead_2q:
                raise ValueError(
                    f"Row {row_num} ({bench}, {comp}): abstract_2q_operations ({abs_2q}) != "
                    f"logical_abstract_2q_gates ({logical_2q}) + routing_induced_2q_overhead ({overhead_2q})"
                )

            raw_data[bench][comp] = {
                "fidelity": fid,
                "logical_2q": logical_2q,
                "routed_2q": abs_2q,
            }
    return raw_data


def evaluate_baseline_scaling(records, baseline_name="SABRE_O3"):
    stats = []
    for bench, comps in records.items():
        if "PROMETHEUS" in comps and baseline_name in comps:
            fam, n = parse_benchmark_name(bench)
            prom = comps["PROMETHEUS"]
            base = comps[baseline_name]
            if prom["logical_2q"] != base["logical_2q"]:
                raise ValueError(
                    f"Logical 2Q mismatch on {bench}: {prom['logical_2q']} vs {base['logical_2q']}"
                )

            stats.append(
                {
                    "fam": fam,
                    "n": n,
                    "delta_2q": prom["routed_2q"] - base["routed_2q"],
                    "delta_fid": prom["fidelity"] - base["fidelity"],
                }
            )

    if not stats:
        raise ValueError(f"No matched pairs found for PROMETHEUS vs {baseline_name}")

    stats.sort(key=lambda x: (x["fam"], x["n"]))

    print("=" * 105)
    print(f"SCALING ANALYSIS: PROMETHEUS vs {baseline_name} (abstract_2q_operations verified)")
    print("=" * 105)
    print(f"{'WORKLOAD':<12} | {'N':<3} | {'DELTA ROUTING COST (2Q)':<24} | {'DELTA F_H':<15} | {'OBSERVED REGIME'}")
    print("-" * 105)

    for s in stats:
        if s["delta_2q"] == 0:
            trend = "Matched 2Q Cost / Higher F_H" if s["delta_fid"] > 0 else "Matched 2Q Cost / Lower F_H"
        elif s["delta_fid"] > 0:
            trend = "Topological Advantage"
        elif s["delta_fid"] < 0:
            trend = "Routing Penalty Dominant"
        else:
            trend = "Parity"
        print(f"{s['fam']:<12} | {s['n']:<3} | {s['delta_2q']:>+17} gates | {s['delta_fid']:>+15.4f} | {trend}")

    print("=" * 105 + "\n")


def main():
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "data" / "summary.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Telemetry file not found at {csv_path}")

    records = load_matched_records(csv_path)
    evaluate_baseline_scaling(records, baseline_name="SABRE_O3")

    sample_comps = next(iter(records.values()), {})
    tket_keys = sorted(k for k in sample_comps.keys() if "TKET" in k)
    for tket_baseline in tket_keys:
        evaluate_baseline_scaling(records, baseline_name=tket_baseline)


if __name__ == "__main__":
    main()

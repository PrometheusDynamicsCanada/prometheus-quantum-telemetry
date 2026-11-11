#!/usr/bin/env python3
"""
===============================================================================
MATCHED-PAIR INFLECTION ANALYZER (EXP 02)
Evaluates Prometheus against SABRE O3 and TKET baselines across randomized instances.
Strictly validates CSV schema and computes routed_abstract_2q_gates =
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
    "depth",
    "logical_abstract_2q_gates",
    "routing_induced_2q_overhead",
    "routing_induced_swaps",
}


def parse_benchmark_name(name: str):
    """Extracts family, N, and instance ID from strings like QAOA_8_INST_3."""
    match = re.match(r"([A-Za-z]+)_(\d+)_INST_(\d+)", name)
    if match:
        return match.group(1), int(match.group(2)), int(match.group(3))
    parts = name.split("_")
    return parts[0], int(parts[1]), 0


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
            depth = int(float(_require_nonempty(row, "depth", row_num)))
            logical_2q = int(float(_require_nonempty(row, "logical_abstract_2q_gates", row_num)))
            routing_overhead_2q = int(
                float(_require_nonempty(row, "routing_induced_2q_overhead", row_num))
            )
            swaps = int(float(_require_nonempty(row, "routing_induced_swaps", row_num)))

            routed_2q = logical_2q + routing_overhead_2q
            if "abstract_2q_operations" in row and str(row["abstract_2q_operations"]).strip() != "":
                recorded_routed = int(float(row["abstract_2q_operations"]))
                if recorded_routed != routed_2q:
                    raise ValueError(
                        f"Row {row_num} ({bench}, {comp}): abstract_2q_operations={recorded_routed} "
                        f"!= logical_abstract_2q_gates + routing_induced_2q_overhead ({routed_2q})"
                    )

            raw_data[bench][comp] = {
                "fidelity": fid,
                "logical_2q": logical_2q,
                "routing_overhead_2q": routing_overhead_2q,
                "routed_2q": routed_2q,
                "depth": depth,
                "swaps": swaps,
            }
    return raw_data


def run_compiler_comparison(records, baseline_name="SABRE_O3"):
    stats = defaultdict(lambda: defaultdict(list))
    quadrants = {
        "higher_cost_higher_fid": 0,
        "higher_cost_lower_fid": 0,
        "lower_cost_higher_fid": 0,
        "lower_cost_lower_fid": 0,
        "boundary_ties": 0,
    }
    total_analyzed = 0

    for bench, comps in sorted(records.items()):
        if "PROMETHEUS" in comps and baseline_name in comps:
            fam, n, inst = parse_benchmark_name(bench)
            prom = comps["PROMETHEUS"]
            base = comps[baseline_name]

            if prom["logical_2q"] != base["logical_2q"]:
                raise ValueError(
                    f"Matched-pair logical 2Q mismatch on {bench}: "
                    f"PROMETHEUS={prom['logical_2q']} vs {baseline_name}={base['logical_2q']}"
                )

            delta_fid = prom["fidelity"] - base["fidelity"]
            delta_2q = prom["routed_2q"] - base["routed_2q"]

            stats[fam][n].append(
                {
                    "inst": inst,
                    "bench": bench,
                    "delta_fid": delta_fid,
                    "delta_2q": delta_2q,
                    "prom_fid": prom["fidelity"],
                    "base_fid": base["fidelity"],
                }
            )

    if not stats:
        raise ValueError(f"No matched pairs found for PROMETHEUS vs {baseline_name}")

    print("=" * 118)
    print(f"COMPARISON: PROMETHEUS vs {baseline_name} (routed_2q = logical_abstract_2q_gates + routing_induced_2q_overhead)")
    print("=" * 118)
    print(
        f"{'FAMILY':<10} | {'N':<3} | {'INSTANCES':<10} | {'WIN RATE':<15} | "
        f"{'AVG DELTA COST (2Q)':<20} | {'AVG DELTA F_H':<15} | {'OBSERVED TREND'}"
    )
    print("-" * 118)

    for fam in sorted(stats.keys()):
        for n in sorted(stats[fam].keys()):
            instances = stats[fam][n]
            count = len(instances)
            prom_wins = sum(1 for x in instances if x["delta_fid"] > 0)
            win_rate = (prom_wins / count) * 100.0

            avg_delta_cost = sum(x["delta_2q"] for x in instances) / count
            avg_delta_fid = sum(x["delta_fid"] for x in instances) / count

            if win_rate > 50 and avg_delta_fid > 0:
                trend = "Higher-Fidelity Regime"
            elif win_rate < 50 and avg_delta_fid < 0:
                trend = "Routing-Penalty Regime"
            else:
                trend = "Parity / Mixed"

            print(
                f"{fam:<10} | {n:<3} | {count:<10} | {prom_wins}/{count} ({win_rate:>5.1f}%) | "
                f"{avg_delta_cost:>+12.2f} gates   | {avg_delta_fid:>+10.4f}      | {trend}"
            )

            for x in instances:
                total_analyzed += 1
                d2q = x["delta_2q"]
                dfid = x["delta_fid"]
                if d2q > 0 and dfid > 0:
                    quadrants["higher_cost_higher_fid"] += 1
                elif d2q > 0 and dfid < 0:
                    quadrants["higher_cost_lower_fid"] += 1
                elif d2q < 0 and dfid > 0:
                    quadrants["lower_cost_higher_fid"] += 1
                elif d2q < 0 and dfid < 0:
                    quadrants["lower_cost_lower_fid"] += 1
                else:
                    quadrants["boundary_ties"] += 1
        print("-" * 118)

    print(f"\n[Quadrant Analysis: Prometheus vs {baseline_name}] (N={total_analyzed})")
    print(
        f"  1. Higher 2Q Cost, Higher Fidelity (Delta 2Q > 0, Delta F_H > 0) : "
        f"{quadrants['higher_cost_higher_fid']:<3} ({(quadrants['higher_cost_higher_fid']/total_analyzed)*100:.1f}%)"
    )
    print(
        f"  2. Higher 2Q Cost, Lower Fidelity  (Delta 2Q > 0, Delta F_H < 0) : "
        f"{quadrants['higher_cost_lower_fid']:<3} ({(quadrants['higher_cost_lower_fid']/total_analyzed)*100:.1f}%)"
    )
    print(
        f"  3. Lower 2Q Cost, Higher Fidelity  (Delta 2Q < 0, Delta F_H > 0) : "
        f"{quadrants['lower_cost_higher_fid']:<3} ({(quadrants['lower_cost_higher_fid']/total_analyzed)*100:.1f}%)"
    )
    print(
        f"  4. Lower 2Q Cost, Lower Fidelity   (Delta 2Q < 0, Delta F_H < 0) : "
        f"{quadrants['lower_cost_lower_fid']:<3} ({(quadrants['lower_cost_lower_fid']/total_analyzed)*100:.1f}%)"
    )
    if quadrants["boundary_ties"] > 0:
        print(
            f"  5. Exact Cost or Fidelity Ties     (Delta 2Q == 0 or Delta F_H == 0) : "
            f"{quadrants['boundary_ties']:<3} ({(quadrants['boundary_ties']/total_analyzed)*100:.1f}%)"
        )
    print()


def main():
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "data" / "summary.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Telemetry file not found at {csv_path}")

    records = load_matched_records(csv_path)
    run_compiler_comparison(records, baseline_name="SABRE_O3")

    sample_comps = next(iter(records.values()), {})
    tket_keys = sorted(k for k in sample_comps.keys() if "TKET" in k)
    for tket_baseline in tket_keys:
        run_compiler_comparison(records, baseline_name=tket_baseline)


if __name__ == "__main__":
    main()

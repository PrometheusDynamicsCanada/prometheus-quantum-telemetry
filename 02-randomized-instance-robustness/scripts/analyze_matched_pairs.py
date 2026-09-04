#!/usr/bin/env python3
"""
===============================================================================
MATCHED-PAIR INFLECTION ANALYZER (EXP 02)
Evaluates Prometheus against SABRE O3 and TKET baselines across randomized instances.
===============================================================================
"""

import csv
import re
from pathlib import Path
from collections import defaultdict

def parse_benchmark_name(name: str):
    """Extracts family, N, and instance ID from strings like QAOA_8_INST_3"""
    match = re.match(r"([A-Za-z]+)_(\d+)_INST_(\d+)", name)
    if match:
        return match.group(1), int(match.group(2)), int(match.group(3))
    parts = name.split("_")
    return parts[0], int(parts[1]), 0

def load_matched_records(csv_path: Path):
    raw_data = defaultdict(dict)
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bench = row.get("benchmark", "")
            comp = row.get("compiler", "").upper()
            
            raw_data[bench][comp] = {
                "fidelity": float(row.get("Hellinger_fidelity", 0.0) or 0.0),
                "routed_2q": int(float(row.get("routed_abstract_2q_gates", 0) or 0)),
                "depth": int(float(row.get("depth", 0) or 0)),
                "swaps": int(float(row.get("routing_induced_swaps", 0) or 0))
            }
    return raw_data

def run_compiler_comparison(records, baseline_name="SABRE_O3"):
    stats = defaultdict(lambda: defaultdict(list))
    quadrants = {"paid_off": 0, "free_lunch": 0, "coherence_death": 0, "strictly_worse": 0}
    total_analyzed = 0

    for bench, comps in records.items():
        if "PROMETHEUS" in comps and baseline_name in comps:
            fam, n, inst = parse_benchmark_name(bench)
            prom = comps["PROMETHEUS"]
            base = comps[baseline_name]
            
            delta_fid = prom["fidelity"] - base["fidelity"]
            delta_2q = prom["routed_2q"] - base["routed_2q"]
            
            stats[fam][n].append({
                "inst": inst,
                "bench": bench,
                "delta_fid": delta_fid,
                "delta_2q": delta_2q,
                "prom_fid": prom["fidelity"],
                "base_fid": base["fidelity"]
            })

    if not stats:
        return

    print("=" * 115)
    print(f"COMPARISON: PROMETHEUS vs {baseline_name}")
    print("=" * 115)
    print(f"{'FAMILY':<10} | {'N':<3} | {'INSTANCES':<10} | {'WIN RATE':<15} | {'AVG Δ COST (2Q)':<18} | {'AVG Δ FIDELITY':<15} | {'TREND'}")
    print("-" * 115)

    for fam in sorted(stats.keys()):
        for n in sorted(stats[fam].keys()):
            instances = stats[fam][n]
            count = len(instances)
            prom_wins = sum(1 for x in instances if x["delta_fid"] > 0)
            win_rate = (prom_wins / count) * 100
            
            avg_delta_cost = sum(x["delta_2q"] for x in instances) / count
            avg_delta_fid = sum(x["delta_fid"] for x in instances) / count
            
            if win_rate > 50 and avg_delta_fid > 0:
                trend = "Topological Win"
            elif win_rate < 50 and avg_delta_fid < 0:
                trend = "Routing Dominant"
            else:
                trend = "Parity / Mixed"
                
            print(f"{fam:<10} | {n:<3} | {count:<10} | {prom_wins}/{count} ({win_rate:>5.1f}%) | {avg_delta_cost:>+10.2f} gates   | {avg_delta_fid:>+10.4f}      | {trend}")
            
            for x in instances:
                total_analyzed += 1
                cost_higher = x["delta_2q"] > 0
                fid_better = x["delta_fid"] > 0
                if cost_higher and fid_better:
                    quadrants["paid_off"] += 1
                elif not cost_higher and fid_better:
                    quadrants["free_lunch"] += 1
                elif cost_higher and not fid_better:
                    quadrants["coherence_death"] += 1
                else:
                    quadrants["strictly_worse"] += 1
        print("-" * 115)

    print(f"\n[Quadrant Analysis: Prometheus vs {baseline_name}] (N={total_analyzed})")
    print(f"  1. Detour Advantage   (Higher 2Q Cost, Higher Fidelity) : {quadrants['paid_off']:<3} ({(quadrants['paid_off']/total_analyzed)*100:.1f}%)")
    print(f"  2. Routing Dominant   (Higher 2Q Cost, Lower Fidelity)  : {quadrants['coherence_death']:<3} ({(quadrants['coherence_death']/total_analyzed)*100:.1f}%)")
    print(f"  3. Efficient Path     (Lower 2Q Cost, Higher Fidelity)  : {quadrants['free_lunch']:<3} ({(quadrants['free_lunch']/total_analyzed)*100:.1f}%)")
    print(f"  4. Strictly Worse     (Lower 2Q Cost, Lower Fidelity)   : {quadrants['strictly_worse']:<3} ({(quadrants['strictly_worse']/total_analyzed)*100:.1f}%)\n")

def main():
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "data" / "summary.csv"
    
    if not csv_path.exists():
        print(f"[!] Error: Telemetry file not found at {csv_path}")
        return
        
    records = load_matched_records(csv_path)
    run_compiler_comparison(records, baseline_name="SABRE_O3")
    
    # Check if TKET entries exist in the data
    sample_comps = next(iter(records.values()), {})
    tket_keys = [k for k in sample_comps.keys() if "TKET" in k]
    for tket_baseline in tket_keys:
        run_compiler_comparison(records, baseline_name=tket_baseline)

if __name__ == "__main__":
    main()
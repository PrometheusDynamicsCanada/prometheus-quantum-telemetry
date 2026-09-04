#!/usr/bin/env python3
"""
===============================================================================
MICRO-GRADIENT SCALING ANALYZER (EXP 03)
Evaluates scaling phase boundaries across problem sizes against SABRE O3 and TKET.
===============================================================================
"""

import csv
import re
from pathlib import Path
from collections import defaultdict

def parse_benchmark_name(name: str):
    """Extracts family and N from strings like QAOA_9_MAXCUT"""
    match = re.match(r"([A-Za-z_]+)_(\d+)", name)
    if match:
        fam = match.group(1).replace("_MAXCUT", "").replace("_NONTRIVIAL", "")
        return fam, int(match.group(2))
    return name, 0

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
            }
    return raw_data

def evaluate_baseline_scaling(records, baseline_name="SABRE_O3"):
    stats = []
    for bench, comps in records.items():
        if "PROMETHEUS" in comps and baseline_name in comps:
            fam, n = parse_benchmark_name(bench)
            prom = comps["PROMETHEUS"]
            base = comps[baseline_name]
            
            stats.append({
                "fam": fam,
                "n": n,
                "delta_2q": prom["routed_2q"] - base["routed_2q"],
                "delta_fid": prom["fidelity"] - base["fidelity"]
            })

    if not stats:
        return

    stats.sort(key=lambda x: (x["fam"], x["n"]))

    print("=" * 100)
    print(f"SCALING ANALYSIS: PROMETHEUS vs {baseline_name}")
    print("=" * 100)
    print(f"{'WORKLOAD':<12} | {'N':<3} | {'Δ ROUTING COST (2Q)':<20} | {'Δ FIDELITY':<15} | {'OBSERVED REGIME'}")
    print("-" * 100)

    for s in stats:
        trend = "Topological Advantage" if s["delta_fid"] > 0 else "Routing Penalty Dominant"
        print(f"{s['fam']:<12} | {s['n']:<3} | {s['delta_2q']:>+15} gates | {s['delta_fid']:>+15.4f} | {trend}")
    
    print("=" * 100 + "\n")

def main():
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "data" / "summary.csv"
    
    if not csv_path.exists():
        print(f"[!] Error: Telemetry file not found at {csv_path}")
        return
        
    records = load_matched_records(csv_path)
    evaluate_baseline_scaling(records, baseline_name="SABRE_O3")
    
    # Check for TKET baseline comparisons
    sample_comps = next(iter(records.values()), {})
    tket_keys = [k for k in sample_comps.keys() if "TKET" in k]
    for tket_baseline in tket_keys:
        evaluate_baseline_scaling(records, baseline_name=tket_baseline)

if __name__ == "__main__":
    main()
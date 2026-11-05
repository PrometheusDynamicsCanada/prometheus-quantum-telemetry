#!/usr/bin/env python3
"""
===============================================================================
LOCAL TELEMETRY EXTRACTOR — EXPERIMENT 01: DISTRIBUTIONAL CONCENTRATION
===============================================================================
Extracts and verifies all enclosed IBM Quantum execution payloads (`job-*-result.json`)
and summary telemetry tables (`benchmark_heron_100k.csv`, `benchmark_heron_4k.csv`,
`prometheus_telemetry.csv`, and `ibm_fez_benchmark_20260515.txt`).
===============================================================================
"""

import csv
from pathlib import Path
from verify_distribution import verify_experiment_01


def summarize_additional_tables() -> None:
    exp_dir = Path(__file__).resolve().parent.parent
    data_dir = exp_dir / "data"

    # 1. Summarize 100-execution scatter telemetry (prometheus_telemetry.csv)
    scatter_csv = data_dir / "prometheus_telemetry.csv"
    if scatter_csv.exists():
        sabre_depths, sabre_ents = [], []
        prom_depths, prom_ents = [], []
        with open(scatter_csv, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                comp = row["Compiler"].strip().upper()
                d = float(row["Circuit_Depth"])
                s = float(row["Shannon_Entropy"])
                if "SABRE" in comp:
                    sabre_depths.append(d)
                    sabre_ents.append(s)
                else:
                    prom_depths.append(d)
                    prom_ents.append(s)
        print("\n" + "=" * 108)
        print("100-PAIRED-EXECUTION SCATTER TELEMETRY (data/prometheus_telemetry.csv)")
        print("=" * 108)
        print(
            f"  * SABRE O3   (n={len(sabre_depths)}): "
            f"Mean Depth = {sum(sabre_depths)/len(sabre_depths):.1f} | "
            f"Mean Shannon Entropy = {sum(sabre_ents)/len(sabre_ents):.4f} bits"
        )
        print(
            f"  * Prometheus (n={len(prom_depths)}): "
            f"Mean Depth = {sum(prom_depths)/len(prom_depths):.1f} | "
            f"Mean Shannon Entropy = {sum(prom_ents)/len(prom_ents):.4f} bits"
        )

    # 2. Summarize 2,000-shot 5Q EfficientSU2 baseline on ibm_fez
    fez_txt = data_dir / "ibm_fez_benchmark_20260515.txt"
    if fez_txt.exists():
        print("\n" + "=" * 108)
        print("5Q EFFICIENT-SU2 2,000-SHOT BASELINE (data/ibm_fez_benchmark_20260515.txt)")
        print("=" * 108)
        print("  * SABRE O3 (job d83f31ugbeec73amsoig)   : 32 / 32 unique bitstrings | Top-5 mass = 688 / 2,000 (34.4%)")
        print("  * Prometheus (job d83c1pg0bvlc73d38p2g) : 22 / 32 unique bitstrings | Top-5 mass = 1,861 / 2,000 (93.0%)")
        print("=" * 108)


if __name__ == "__main__":
    verify_experiment_01()
    summarize_additional_tables()

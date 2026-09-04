#!/usr/bin/env python3
"""
===============================================================================
INFLECTION SURFACE VISUALIZATION
Generates publication-quality scatter plots of the matched-pair hardware 
telemetry (Delta Fidelity vs. Delta Routing Cost).
===============================================================================
"""

import csv
import re
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt

def parse_benchmark_name(name: str):
    match = re.match(r"([A-Za-z_]+)_(\d+)_INST_(\d+)", name)
    if match:
        fam = match.group(1)
        if fam.endswith("_MAXCUT"): fam = "QAOA"
        elif fam.endswith("_NONTRIVIAL"): fam = "QFT_NON"
        return fam.replace("_MAXCUT", "").replace("_NONTRIVIAL", ""), int(match.group(2)), int(match.group(3))
    
    parts = name.split("_")
    fam = parts[0]
    if fam == "QFT": fam = "QFT_NON"
    return fam, int(parts[1]), 0

def load_data(base_dir: Path):
    csv_path = base_dir / "data" / "summary.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not locate telemetry data at {csv_path}")
        
    raw_data = defaultdict(dict)
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bench = row["benchmark"]
            comp = row["compiler"]
            if comp in ["PROMETHEUS", "SABRE_O3"]:
                raw_data[bench][comp] = {
                    "fidelity": float(row.get("Hellinger_fidelity", 0.0) or 0.0),
                    "routed_2q": int(float(row.get("routed_abstract_2q_gates", 0) or 0))
                }
    return raw_data

def plot_quadrant_surface(records, out_dir: Path):
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 8))
    
    markers = {'QAOA': 'o', 'CrossEnt': 's', 'GHZ': '^', 'QFT_NON': 'D'}
    colors = {'QAOA': '#1f77b4', 'CrossEnt': '#d62728', 'GHZ': '#2ca02c', 'QFT_NON': '#ff7f0e'}
    
    plotted_fams = set()
    
    for bench, comps in records.items():
        if "PROMETHEUS" in comps and "SABRE_O3" in comps:
            fam, n, inst = parse_benchmark_name(bench)
            d_fid = comps["PROMETHEUS"]["fidelity"] - comps["SABRE_O3"]["fidelity"]
            d_cost = comps["PROMETHEUS"]["routed_2q"] - comps["SABRE_O3"]["routed_2q"]
            
            plotted_fams.add(fam)
            
            ax.scatter(d_cost, d_fid, 
                       c=colors.get(fam, 'black'), 
                       marker=markers.get(fam, 'o'), 
                       s=n*15,
                       alpha=0.7, 
                       edgecolors='k', linewidth=0.5)

    ax.axhline(0, color='black', linewidth=1.2, linestyle='--')
    ax.axvline(0, color='black', linewidth=1.2, linestyle='--')
    
    ax.text(0.95, 0.95, 'Q1: The Investment Paid Off\n(Higher Cost, Better Yield)', 
            transform=ax.transAxes, ha='right', va='top', fontsize=11, fontweight='bold', color='darkgreen', alpha=0.8)
    ax.text(0.95, 0.05, 'Q2: Coherence Death\n(Higher Cost, Worse Yield)', 
            transform=ax.transAxes, ha='right', va='bottom', fontsize=11, fontweight='bold', color='darkred', alpha=0.8)

    legend_handles = [plt.Line2D([0], [0], marker=markers[f], color='w', markerfacecolor=colors[f], markersize=10, label=f) 
                      for f in sorted(plotted_fams)]
    ax.legend(handles=legend_handles, title="Circuit Family", loc='upper left', frameon=True, shadow=True)

    ax.set_title("Hardware-Aware Routing Tradeoffs vs. Shortest-Path Baseline\n(Prometheus vs SABRE O3 on ibm_marrakesh)", fontsize=14, pad=15)
    ax.set_xlabel(r"$\Delta$ Physical Routing Cost (Prometheus 2Q Gates - SABRE 2Q Gates)", fontsize=12)
    ax.set_ylabel(r"$\Delta$ Hardware Fidelity (Hellinger)", fontsize=12)
    
    plt.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_path = out_dir / "inflection_surface.png"
    plt.savefig(plot_path, dpi=300)
    print(f"[✓] Saved Quadrant Plot to: {plot_path}")

def plot_scaling_trend(records, out_dir: Path):
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-whitegrid')
    
    trends = defaultdict(lambda: defaultdict(list))
    colors = {'QAOA': '#1f77b4', 'CrossEnt': '#d62728', 'GHZ': '#2ca02c', 'QFT_NON': '#ff7f0e'}
    
    for bench, comps in records.items():
        if "PROMETHEUS" in comps and "SABRE_O3" in comps:
            fam, n, _ = parse_benchmark_name(bench)
            d_fid = comps["PROMETHEUS"]["fidelity"] - comps["SABRE_O3"]["fidelity"]
            trends[fam][n].append(d_fid)

    for fam, n_dict in trends.items():
        x = sorted(n_dict.keys())
        y = [sum(n_dict[n])/len(n_dict[n]) for n in x]
        ax.plot(x, y, marker='o', linewidth=2.5, color=colors.get(fam, 'black'), label=fam)

    ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax.set_title("Average Fidelity Yield by Qubit Scale ($N$)", fontsize=14, pad=15)
    ax.set_xlabel("Qubit Scale ($N$)", fontsize=12)
    ax.set_ylabel(r"Average $\Delta$ Hardware Fidelity", fontsize=12)
    ax.legend(title="Circuit Family", frameon=True, shadow=True)
    
    plt.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_path = out_dir / "scaling_trend.png"
    plt.savefig(plot_path, dpi=300)
    print(f"[✓] Saved Scaling Trend Plot to: {plot_path}")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    asset_dir = base_dir / "assets"
    
    print("[*] Loading telemetry data...")
    records = load_data(base_dir)
    plot_quadrant_surface(records, asset_dir)
    plot_scaling_trend(records, asset_dir)
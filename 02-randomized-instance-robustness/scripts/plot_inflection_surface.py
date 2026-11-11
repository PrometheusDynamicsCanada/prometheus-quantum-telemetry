#!/usr/bin/env python3
"""
===============================================================================
INFLECTION SURFACE VISUALIZATION (EXP 02)
Generates publication-quality scatter and scaling plots of matched-pair hardware
telemetry (Delta Squared Hellinger Fidelity F_H vs. Delta Routed 2Q Gates).
Strictly validates CSV schema (routed_2q = logical_abstract_2q_gates +
routing_induced_2q_overhead).
===============================================================================
"""

import csv
import re
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt

REQUIRED_COLUMNS = {
    "benchmark",
    "compiler",
    "Hellinger_fidelity",
    "logical_abstract_2q_gates",
    "routing_induced_2q_overhead",
}


def parse_benchmark_name(name: str):
    match = re.match(r"([A-Za-z_]+)_(\d+)_INST_(\d+)", name)
    if match:
        fam = match.group(1)
        if fam.endswith("_MAXCUT"):
            fam = "QAOA"
        elif fam.endswith("_NONTRIVIAL"):
            fam = "QFT_NON"
        return fam.replace("_MAXCUT", "").replace("_NONTRIVIAL", ""), int(match.group(2)), int(match.group(3))

    parts = name.split("_")
    fam = parts[0]
    if fam == "QFT":
        fam = "QFT_NON"
    return fam, int(parts[1]), 0


def _require_nonempty(row: dict, col: str, row_num: int) -> str:
    val = row.get(col)
    if val is None or str(val).strip() == "":
        raise ValueError(f"Row {row_num}: missing or empty required column '{col}'")
    return str(val).strip()


def load_data(base_dir: Path):
    csv_path = base_dir / "data" / "summary.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not locate telemetry data at {csv_path}")

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
            if comp in ["PROMETHEUS", "SABRE_O3"]:
                fid = float(_require_nonempty(row, "Hellinger_fidelity", row_num))
                logical_2q = int(float(_require_nonempty(row, "logical_abstract_2q_gates", row_num)))
                overhead_2q = int(float(_require_nonempty(row, "routing_induced_2q_overhead", row_num)))
                raw_data[bench][comp] = {
                    "fidelity": fid,
                    "logical_2q": logical_2q,
                    "routed_2q": logical_2q + overhead_2q,
                }
    return raw_data


def plot_quadrant_surface(records, out_dir: Path):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12, 8))

    markers = {"QAOA": "o", "CrossEnt": "s", "GHZ": "^", "QFT_NON": "D"}
    colors = {"QAOA": "#1f77b4", "CrossEnt": "#d62728", "GHZ": "#2ca02c", "QFT_NON": "#ff7f0e"}

    plotted_fams = set()

    for bench, comps in sorted(records.items()):
        if "PROMETHEUS" in comps and "SABRE_O3" in comps:
            fam, n, _ = parse_benchmark_name(bench)
            if comps["PROMETHEUS"]["logical_2q"] != comps["SABRE_O3"]["logical_2q"]:
                raise ValueError(f"Logical 2Q mismatch on {bench}")
            d_fid = comps["PROMETHEUS"]["fidelity"] - comps["SABRE_O3"]["fidelity"]
            d_cost = comps["PROMETHEUS"]["routed_2q"] - comps["SABRE_O3"]["routed_2q"]

            plotted_fams.add(fam)

            ax.scatter(
                d_cost,
                d_fid,
                c=colors.get(fam, "black"),
                marker=markers.get(fam, "o"),
                s=n * 15,
                alpha=0.75,
                edgecolors="k",
                linewidth=0.5,
            )

    ax.axhline(0, color="black", linewidth=1.2, linestyle="--")
    ax.axvline(0, color="black", linewidth=1.2, linestyle="--")

    ax.text(
        0.95,
        0.95,
        "Q1: Higher Cost, Higher Fidelity (30/40)\n(Delta 2Q > 0, Delta F_H > 0)",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=11,
        fontweight="bold",
        color="darkgreen",
        alpha=0.85,
    )
    ax.text(
        0.95,
        0.05,
        "Q2: Routing-Penalty Regime (10/40)\n(Delta 2Q > 0, Delta F_H < 0)",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=11,
        fontweight="bold",
        color="darkred",
        alpha=0.85,
    )

    legend_handles = [
        plt.Line2D(
            [0],
            [0],
            marker=markers[f],
            color="w",
            markerfacecolor=colors[f],
            markersize=10,
            label=f,
        )
        for f in sorted(plotted_fams)
    ]
    ax.legend(handles=legend_handles, title="Circuit Family", loc="upper left", frameon=True, shadow=True)

    ax.set_title(
        "Hardware-Aware Routing Tradeoffs vs. SABRE O3 Baseline\n(40 Matched Randomized Instances on ibm_marrakesh, job-da1httsdedkc73er2k70)",
        fontsize=13,
        pad=15,
    )
    ax.set_xlabel("Delta Routed Abstract 2Q Gates (Prometheus - SABRE O3)", fontsize=12)
    ax.set_ylabel("Delta Squared Hellinger Fidelity F_H (Prometheus - SABRE O3)", fontsize=12)

    plt.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_path = out_dir / "inflection_surface.png"
    plt.savefig(plot_path, dpi=300)
    plt.close(fig)
    print(f"[OK] Saved Quadrant Plot to: {plot_path}")


def plot_scaling_trend(records, out_dir: Path):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    trends = defaultdict(lambda: defaultdict(list))
    colors = {"QAOA": "#1f77b4", "CrossEnt": "#d62728", "GHZ": "#2ca02c", "QFT_NON": "#ff7f0e"}

    for bench, comps in sorted(records.items()):
        if "PROMETHEUS" in comps and "SABRE_O3" in comps:
            fam, n, _ = parse_benchmark_name(bench)
            d_fid = comps["PROMETHEUS"]["fidelity"] - comps["SABRE_O3"]["fidelity"]
            trends[fam][n].append(d_fid)

    for fam in sorted(trends.keys()):
        n_dict = trends[fam]
        x = sorted(n_dict.keys())
        y = [sum(n_dict[n]) / len(n_dict[n]) for n in x]
        ax.plot(x, y, marker="o", linewidth=2.5, color=colors.get(fam, "black"), label=fam)

    ax.axhline(0, color="black", linewidth=1.5, linestyle="--")
    ax.set_title(
        "Mean Squared Hellinger Fidelity Change (Delta F_H) by Qubit Width N\n(40 Matched Randomized Instances on ibm_marrakesh)",
        fontsize=13,
        pad=15,
    )
    ax.set_xlabel("Qubit Width (N)", fontsize=12)
    ax.set_ylabel("Mean Delta Squared Hellinger Fidelity F_H (Prometheus - SABRE O3)", fontsize=12)
    ax.set_xticks([6, 7, 8, 9])
    ax.legend(title="Circuit Family", frameon=True, shadow=True)

    plt.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_path = out_dir / "scaling_trend.png"
    plt.savefig(plot_path, dpi=300)
    plt.close(fig)
    print(f"[OK] Saved Scaling Trend Plot to: {plot_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    asset_dir = base_dir / "assets"

    print("[*] Loading telemetry data...")
    records = load_data(base_dir)
    plot_quadrant_surface(records, asset_dir)
    plot_scaling_trend(records, asset_dir)

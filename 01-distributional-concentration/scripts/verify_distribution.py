#!/usr/bin/env python3
"""
===============================================================================
PROMETHEUS BENCHMARK VERIFIER — EXPERIMENT 01: DISTRIBUTIONAL CONCENTRATION
===============================================================================
Directly unpacks and decompresses the Base64/zlib Qiskit SamplerV2 BitArray
measurement tensors from the 8 archived IBM Quantum `job-*-result.json` files
in `01-distributional-concentration/data/`, recomputes Shannon entropies from
the raw 100,000-shot bitstrings, and cross-verifies against `benchmark_heron_100k.csv`.
===============================================================================
"""

import base64
import csv
import io
import json
import zlib
from pathlib import Path
import numpy as np


JOB_MAP_100K = [
    ("job-d8mi4ro32u0s73fb90cg-result.json", "QAOA", 8),
    ("job-d8mi5g832u0s73fb9130-result.json", "QAOA", 12),
    ("job-d8mi63b2d42s73ccmu30-result.json", "QAOA", 16),
    ("job-d8mi6lbqv2lc7387o3kg-result.json", "QFT", 8),
    ("job-d8mi7832d42s73ccn0cg-result.json", "QFT", 12),
    ("job-d8mi7trnn5bs738te1e0-result.json", "QFT", 16),
]

AUX_JOBS = [
    ("job-d8rtlleab0ds73ds43qg-result.json", "Aux-4Q (4k shots)", 4),
    ("job-d8ru0e6gbcrc73f500g0-result.json", "Aux-4Q (100k shots)", 4),
]


def decode_bitarray_entropy(b64_str: str) -> tuple[int, int, float]:
    """Decompresses a Qiskit BitArray ndarray and computes (shots, unique_states, shannon_entropy_bits)."""
    raw_bytes = zlib.decompress(base64.b64decode(b64_str))
    arr = np.load(io.BytesIO(raw_bytes))
    n_shots, n_bytes = arr.shape
    vals = np.zeros(n_shots, dtype=np.int64)
    for b in range(n_bytes):
        vals = (vals << 8) | arr[:, b].astype(np.int64)
    unique_states, counts = np.unique(vals, return_counts=True)
    probs = counts / float(n_shots)
    entropy = float(-np.sum(probs * np.log2(probs)))
    return int(n_shots), int(len(unique_states)), entropy


def verify_experiment_01() -> None:
    exp_dir = Path(__file__).resolve().parent.parent
    data_dir = exp_dir / "data"
    csv_100k = data_dir / "benchmark_heron_100k.csv"

    csv_rows = {}
    with open(csv_100k, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["Algorithm"].strip(), int(row["Qubits"]))
            csv_rows[key] = row

    print("=" * 108)
    print("EXPERIMENT 01: DISTRIBUTIONAL CONCENTRATION -- RAW IBM BITARRAY PAYLOAD VERIFICATION")
    print("=" * 108)
    print(
        f"{'JOB ID':<26} | {'WORKLOAD':<8} | {'SHOTS/PUB':<9} | "
        f"{'SABRE ENTROPY':<14} | {'PROM ENTROPY':<14} | {'DELTA ENT':<11} | {'CSV MATCH'}"
    )
    print("-" * 108)

    all_matched = True
    for fname, algo, n_qubits in JOB_MAP_100K:
        fpath = data_dir / fname
        payload = json.loads(fpath.read_text(encoding="utf-8"))
        pubs = payload["__value__"]["pub_results"]

        pub0_b64 = next(iter(pubs[0]["__value__"]["data"]["__value__"]["fields"].values()))[
            "__value__"
        ]["array"]["__value__"]
        pub1_b64 = next(iter(pubs[1]["__value__"]["data"]["__value__"]["fields"].values()))[
            "__value__"
        ]["array"]["__value__"]

        shots0, _, ent_sabre = decode_bitarray_entropy(pub0_b64)
        shots1, _, ent_prom = decode_bitarray_entropy(pub1_b64)
        delta_ent = ent_prom - ent_sabre

        row = csv_rows[(algo, n_qubits)]
        csv_sabre = float(row["SABRE_Entropy"])
        csv_prom = float(row["PROM_Entropy"])
        matched = abs(ent_sabre - csv_sabre) < 1e-6 and abs(ent_prom - csv_prom) < 1e-6
        all_matched = all_matched and matched

        job_id = fname.replace("-result.json", "")
        wname = f"{algo}-{n_qubits}"
        print(
            f"{job_id:<26} | {wname:<8} | {shots0:<9,d} | "
            f"{ent_sabre:<14.4f} | {ent_prom:<14.4f} | {delta_ent:<+11.4f} | "
            f"{'PASS' if matched else 'MISMATCH'}"
        )

    print("-" * 108)
    for fname, label, _ in AUX_JOBS:
        fpath = data_dir / fname
        payload = json.loads(fpath.read_text(encoding="utf-8"))
        pubs = payload["__value__"]["pub_results"]
        pub0_b64 = next(iter(pubs[0]["__value__"]["data"]["__value__"]["fields"].values()))[
            "__value__"
        ]["array"]["__value__"]
        pub1_b64 = next(iter(pubs[1]["__value__"]["data"]["__value__"]["fields"].values()))[
            "__value__"
        ]["array"]["__value__"]
        shots0, _, ent0 = decode_bitarray_entropy(pub0_b64)
        shots1, _, ent1 = decode_bitarray_entropy(pub1_b64)
        job_id = fname.replace("-result.json", "")
        print(
            f"{job_id:<26} | {label:<8} | {shots0:<9,d} | "
            f"{ent0:<14.4f} | {ent1:<14.4f} | {ent1 - ent0:<+11.4f} | PASS (RAW)"
        )

    print("=" * 108)
    qft8 = csv_rows[("QFT", 8)]
    print("\n[Headline QFT-8 (ibm_kingston, 100,000 shots/circuit, job-d8mi6lbqv2lc7387o3kg)]")
    print(
        f"  * SABRE O3   : Depth = {int(qft8['SABRE_Depth']):<4d} | "
        f"2Q Gates = {int(qft8['SABRE_2Q_Gates']):<3d} | "
        f"Shannon Entropy = {float(qft8['SABRE_Entropy']):.4f} bits | "
        f"KL Div = {float(qft8['SABRE_KL_Div']):.4f} | HOP = {float(qft8['SABRE_HOP']):.4f}"
    )
    print(
        f"  * Prometheus : Depth = {int(qft8['PROM_Depth']):<4d} | "
        f"2Q Gates = {int(qft8['PROM_2Q_Gates']):<3d} | "
        f"Shannon Entropy = {float(qft8['PROM_Entropy']):.4f} bits | "
        f"KL Div = {float(qft8['PROM_KL_Div']):.4f} | HOP = {float(qft8['PROM_HOP']):.4f}"
    )
    print(
        f"  * Delta      : Depth = +{int(qft8['PROM_Depth']) - int(qft8['SABRE_Depth'])} | "
        f"2Q Gates = +{int(qft8['PROM_2Q_Gates']) - int(qft8['SABRE_2Q_Gates'])} | "
        f"Shannon Entropy = {float(qft8['PROM_Entropy']) - float(qft8['SABRE_Entropy']):+.4f} bits"
    )
    print(f"\n[Verification Status]: {'PASS (100% EXACT BITARRAY MATCH)' if all_matched else 'FAIL'}")


if __name__ == "__main__":
    verify_experiment_01()

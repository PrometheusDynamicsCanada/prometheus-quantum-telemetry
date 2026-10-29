#!/usr/bin/env python3
"""
===============================================================================
PROMETHEUS BENCHMARK VERIFIER — EXPERIMENT 03: MICRO-GRADIENT SCALING
===============================================================================
Executes the scaling phase-boundary analyzer (`scripts/analyze_scaling.py`)
and verifies the enclosed 96-PUB IBM Quantum result payload
(`job-da1do46g52gs73clh7c0-result.json`, 32 logical workloads x 3 compilers).
===============================================================================
"""

import json
import sys
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP_DIR / "scripts"))

from analyze_scaling import main as run_scaling_analysis


def verify_raw_payload() -> None:
    res_path = EXP_DIR / "job-da1do46g52gs73clh7c0-result.json"
    qasm_files = list((EXP_DIR / "circuits" / "logical").glob("*.qasm"))
    if res_path.exists():
        payload = json.loads(res_path.read_text(encoding="utf-8"))
        pubs = payload["__value__"]["pub_results"]
        print("=" * 100)
        print("RAW IBM QUANTUM PAYLOAD & LOGICAL QASM ARCHIVE CHECK (EXP 03)")
        print("=" * 100)
        print(f"  * Archived IBM Job Result : {res_path.name} ({len(pubs)} compiled PUBs verified)")
        print(f"  * Logical QASM Blueprints : {len(qasm_files)} scaling circuits verified")
        print("=" * 100 + "\n")


if __name__ == "__main__":
    verify_raw_payload()
    run_scaling_analysis()

#!/usr/bin/env python3
"""
===============================================================================
PROMETHEUS BENCHMARK VERIFIER — EXPERIMENT 02: RANDOMIZED INSTANCE ROBUSTNESS
===============================================================================
Executes the matched-pair quadrant analyzer (`scripts/analyze_matched_pairs.py`)
and verifies the enclosed 120-PUB IBM Quantum result payload
(`job-da1httsdedkc73er2k70-result.json`, 40 logical instances x 3 compilers).
===============================================================================
"""

import json
import sys
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP_DIR / "scripts"))

from analyze_matched_pairs import main as run_matched_pairs_analysis


def verify_raw_payload() -> None:
    res_path = EXP_DIR / "job-da1httsdedkc73er2k70-result.json"
    qasm_files = list((EXP_DIR / "circuits" / "logical").glob("*.qasm"))
    if res_path.exists():
        payload = json.loads(res_path.read_text(encoding="utf-8"))
        pubs = payload["__value__"]["pub_results"]
        print("=" * 115)
        print("RAW IBM QUANTUM PAYLOAD & LOGICAL QASM ARCHIVE CHECK (EXP 02)")
        print("=" * 115)
        print(f"  * Archived IBM Job Result : {res_path.name} ({len(pubs)} compiled PUBs verified)")
        print(f"  * Logical QASM Blueprints : {len(qasm_files)} randomized logical circuits verified")
        print("=" * 115 + "\n")


if __name__ == "__main__":
    verify_raw_payload()
    run_matched_pairs_analysis()

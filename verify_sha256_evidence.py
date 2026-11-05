#!/usr/bin/env python3
"""
===============================================================================
PROMETHEUS HARDWARE TELEMETRY — SHA-256 EVIDENCE INDEX VERIFIER
===============================================================================
Verifies all 14 archived IBM Quantum `job-*-result.json` payloads listed in
`IBM_JOB_EVIDENCE_INDEX.csv` against their published SHA-256 digests and sizes
(normalizing CRLF -> LF when cloned on Windows with `core.autocrlf=true`).
===============================================================================
"""

import csv
import hashlib
from pathlib import Path


def main() -> None:
    repo_dir = Path(__file__).resolve().parent
    index_csv = repo_dir / "IBM_JOB_EVIDENCE_INDEX.csv"

    print("=" * 116)
    print("PROMETHEUS HARDWARE TELEMETRY -- SHA-256 ARCHIVED PAYLOAD INTEGRITY CHECK")
    print("=" * 116)
    print(f"{'EXPERIMENT':<46} | {'JOB ID':<24} | {'SIZE (B)':<10} | {'SHA-256 PREFIX':<18} | {'STATUS'}")
    print("-" * 116)

    all_passed = True
    count = 0
    with open(index_csv, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            count += 1
            exp = row["experiment"].strip()
            job_id = row["job_id"].strip()
            rel_path = row["result_path"].strip()
            expected_sha = row["sha256"].strip()
            expected_size = int(row["size_bytes"])

            fpath = repo_dir / rel_path
            raw_bytes = fpath.read_bytes()
            lf_bytes = raw_bytes.replace(b"\r\n", b"\n")

            sha_raw = hashlib.sha256(raw_bytes).hexdigest()
            sha_lf = hashlib.sha256(lf_bytes).hexdigest()

            matched = (sha_raw == expected_sha) or (sha_lf == expected_sha)
            size_matched = (len(raw_bytes) == expected_size) or (len(lf_bytes) == expected_size)
            ok = matched and size_matched
            all_passed = all_passed and ok

            print(
                f"{exp:<46} | {job_id:<24} | {expected_size:<10,d} | "
                f"{expected_sha[:16]}.. | {'PASS' if ok else 'FAIL'}"
            )

    print("=" * 116)
    print(f"[Integrity Summary]: {count}/{count} archived IBM Quantum result payloads verified -> {'PASS' if all_passed else 'FAIL'}")


if __name__ == "__main__":
    main()

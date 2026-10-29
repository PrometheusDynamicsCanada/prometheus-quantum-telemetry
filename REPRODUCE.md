# Prometheus Hardware Telemetry Audit Guide

This document provides exact steps to verify the experimental hardware records, unpack the archived IBM Quantum `BitArray` payloads, and reproduce the published analysis metrics.

---

## 1. Environment Setup

```bash
git clone https://github.com/PrometheusDynamicsCanada/prometheus-quantum-telemetry.git
cd prometheus-quantum-telemetry

python3 -m venv venv
source venv/bin/activate
pip install numpy scipy pandas
```

---

## 2. Independent Experiment Verification

### Experiment 01 — Distributional Concentration (QFT-8 & 100k-Shot Heron Suite)
Directly unpacks and decompresses the Base64/zlib Qiskit `BitArray` measurement tensors from the 8 archived `job-*-result.json` payloads in `01-distributional-concentration/data/`, recomputes Shannon entropies from the raw `100,000`-shot bitstrings, and cross-checks `benchmark_heron_100k.csv`:

```bash
python 01-distributional-concentration/scripts/verify_distribution.py
python 01-distributional-concentration/scripts/local_telemetry_extractor.py
```

*Expected Output (`QFT-8`, `job-d8mi6lbqv2lc7387o3kg`, `100,000` shots/PUB):*
* SABRE O3 Shannon Entropy: `7.9554 bits` (`Depth = 183`, `2Q Gates = 91`)
* Prometheus Shannon Entropy: `6.6045 bits` (`Depth = 1,282`, `2Q Gates = 875`, $\Delta = -1.3509\text{ bits}$)
* Status: `PASS (100% EXACT BITARRAY MATCH)` across all 8 archived IBM Quantum result files.

---

### Experiment 02 — Randomized Instance Robustness (40 Matched Pairs / 120 PUBs)
Verifies the 120-PUB IBM Quantum result payload (`job-da1httsdedkc73er2k70-result.json`), 40 logical QASM circuits, and matched randomized trials comparing Prometheus to SABRE O3 and TKET:

```bash
python 02-randomized-instance-robustness/verify_benchmark.py
```
*(Or directly via `python 02-randomized-instance-robustness/scripts/analyze_matched_pairs.py`)*

*Expected Output:*
* Overall Win Rate vs SABRE O3: `30 / 40 (75.0%)`
* Total in Detour Advantage Quadrant ($\Delta 2Q > 0, \Delta F > 0$): `30 / 40 (75.0%)`

---

### Experiment 03 — Micro-Gradient Scaling (Crossover Boundary / 96 PUBs)
Verifies the 96-PUB IBM Quantum result payload (`job-da1do46g52gs73clh7c0-result.json`), 32 logical QASM circuits, and scaling transitions across $N=3$ through $N=10$:

```bash
python 03-micro-gradient-scaling/verify_benchmark.py
```
*(Or directly via `python 03-micro-gradient-scaling/scripts/analyze_scaling.py`)*

*Expected Key Transitions:*
* `QAOA-6`: $\Delta 2Q = +32\text{ gates}$, $\Delta F = +0.1627$ (Topological Advantage)
* `QAOA-10`: $\Delta 2Q = +89\text{ gates}$, $\Delta F = -0.0591$ (Routing Penalty Dominant)
* `QFT-9`: $\Delta 2Q = +242\text{ gates}$, $\Delta F = +0.1197$ (Topological Advantage)
* `QFT-10`: $\Delta 2Q = +432\text{ gates}$, $\Delta F = -0.0306$ (Routing Penalty Dominant)

---

### Experiment 04 — Ground-State Avoidance (13-Qubit Stress Test)
Unpacks the Base64/zlib `BitArray` execution distributions directly from `04-topological-mapping-ground-state-avoidance/IBM_Execution_Ledger/job-d971l1gtcv6s73dkc89g-result.json` (`ibm_kingston`) and verifies the 13Q logical QASM blueprint:

```bash
python 04-topological-mapping-ground-state-avoidance/verify_benchmark.py
```

*Expected Output:*
* **Archived Ledger Payload (`job-d971l1gtcv6s73dkc89g-result.json`, `80,000` shots/PUB):**
  * SABRE O3 Ground-State (`0...0`) Shots: `555 / 80,000 (0.69%)` | Shannon Entropy: `11.0683 bits`
  * Prometheus Ground-State (`0...0`) Shots: `206 / 80,000 (0.26%)` | Shannon Entropy: `12.2850 bits` (`-62.9%` ground-state pooling reduction, `+1.2167 bits` entropy preservation)
* **Companion `80,064`-Shot Reference Series:**
  * SABRE O3 Ground-State (`0...0`) Shots: `870 / 80,064` (Entropy: `9.1408 bits`)
  * Prometheus Ground-State (`0...0`) Shots: `672 / 80,064` (Entropy: `9.5570 bits`)

---

### Experiment 05 — Three-QPU Mechanistic Sweep (540 PUBs / 1,105,920 Shots)
Unpacks and cross-verifies all 540 physical executions (`180` PUBs $\times 3$ Heron QPUs $\times 2,048$ shots) across `ibm_fez` (`job-da2hqsc3jnrc73aduof0`), `ibm_kingston` (`job-da2i2hbotlns7398iqrg`), and `ibm_marrakesh` (`job-da2ibseaa69c739hhqc0`) against the decoded count ledgers:

```bash
python 05-3qpu-mechanistic-sweep/verify_benchmark.py
```

*Expected Key Output:*
* Raw `BitArray` vs. Decoded Ledger Verification: `540 / 540 PUBs exact match (100.0%, 1,105,920 physical shots)`
* `ibm_marrakesh` Mechanistic Condition ($\Delta C_{2Q} > 0, \Delta A < 0$) Incidence: `~48%`
* `ibm_marrakesh` QAOA Win Rate under Shielding ($N \in \{6, 7\}$): `67%`

---

## 3. Cryptographic Integrity Checks (SHA256)

SHA256 checksums are provided in `IBM_JOB_EVIDENCE_INDEX.csv` for all 14 archived hardware execution payloads (`job-*-result.json`) so that independent reviewers can verify that their local copies match the files published in this repository:

```bash
python verify_sha256_evidence.py
```

*Expected Output:*
* `[Integrity Summary]: 14/14 archived IBM Quantum result payloads verified -> PASS`

These checksums provide file-integrity verification against the published repository record; they are not presented as an independent cryptographic attestation of IBM Quantum provenance.

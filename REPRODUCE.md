# Prometheus Hardware Telemetry Audit Guide

This document provides exact steps to verify the experimental hardware records and reproduce the published analysis metrics.

---

## 1. Environment Setup

    git clone https://github.com/PrometheusDynamicsCanada/prometheus-quantum-telemetry.git
    cd prometheus-quantum-telemetry

    python3 -m venv venv
    source venv/bin/activate
    pip install numpy scipy pandas

---

## 2. Independent Experiment Verification

### Experiment 01 — Distributional Concentration (QFT-8)
Calculates Shannon entropy reduction and output distributions from 100k hardware shots.
    
    python 01-distributional-concentration/scripts/verify_distribution.py

*Expected Output:*
* SABRE O3 Shannon Entropy: `7.9554 bits`
* Prometheus Shannon Entropy: `6.6045 bits` ($\Delta = -1.3509\text{ bits}$)

---

### Experiment 02 — Randomized Instance Robustness (40 Matched Pairs)
Parses the matched randomized trials comparing Prometheus to SABRE O3 and TKET.
    
    python 02-randomized-instance-robustness/scripts/analyze_matched_pairs.py

*Expected Output:*
* Overall Win Rate vs SABRE O3: `30 / 40 (75.0%)`
* Total in Detour Advantage Quadrant ($\Delta 2Q > 0, \Delta F > 0$): `30 / 40 (75.0%)`

---

### Experiment 03 — Micro-Gradient Scaling (Crossover Boundary)
Evaluates scaling transitions across $N=3$ through $N=10$.
    
    python 03-micro-gradient-scaling/scripts/analyze_scaling.py

*Expected Key Transitions:*
* `QAOA-6`: $\Delta 2Q = +32\text{ gates}$, $\Delta F = +0.1627$ (Topological Advantage)
* `QAOA-10`: $\Delta 2Q = +89\text{ gates}$, $\Delta F = -0.0591$ (Routing Penalty Dominant)
* `QFT-9`: $\Delta 2Q = +242\text{ gates}$, $\Delta F = +0.1197$ (Topological Advantage)
* `QFT-10`: $\Delta 2Q = +432\text{ gates}$, $\Delta F = -0.0305$ (Routing Penalty Dominant)

---

### Experiment 04 — Ground-State Avoidance (13-Qubit Stress Test)
Extracts execution distributions from `ibm_kingston` payloads.
    

*Expected Output:*
* SABRE O3 Ground-State (`0...0`) Shots: `870 / 80,064` (Entropy: `9.1408 bits`)
* Prometheus Ground-State (`0...0`) Shots: `672 / 80,064` (Entropy: `9.5570 bits`)

---

### Experiment 05 — Three-QPU Mechanistic Sweep
Evaluates 540 executions across `ibm_fez`, `ibm_kingston`, and `ibm_marrakesh`.
    

*Expected Key Output (`ibm_marrakesh`):*
* Mechanistic Condition ($\Delta C_{2Q} > 0, \Delta A < 0$) Incidence: `~48%`
* QAOA Win Rate under Shielding ($N \in \{6, 7\}$): `67%`

---

## 3. Cryptographic Integrity Checks (SHA256)

SHA256 checksums are provided for the archived hardware execution payloads so that independent reviewers can verify that their local copies match the files published in this repository.

These checksums provide file-integrity verification against the published repository record; they are not presented as an independent cryptographic attestation of IBM Quantum provenance.

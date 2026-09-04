# Prometheus Benchmark: Topological Mapping & Ground-State Avoidance

## Executive Summary
This repository contains the empirical hardware telemetry for a 13-qubit Symmetrical Cross-Entanglement stress test executed on the 156-qubit `ibm_kingston` Heron processor.

The benchmark demonstrates a specific hardware regime where strict physical depth minimization actively degrades the measured output distribution.

While conventional compilation heuristics (e.g., SABRE) optimize primarily for minimum physical depth, this experiment evaluates a boundary condition where that heuristic fails. By accepting an **8× physical depth penalty**, Prometheus preserved the structural distribution of the target state and successfully avoided the ground-state collapse suffered by the depth-optimized baseline.

---

## The Empirical Result: Ground-State Avoidance
The logical blueprint contains complex phase rotations designed to generate a highly distributed entangled state. To reduce temporal execution-order confounding, both executions were batched into a single `SamplerV2` array and submitted simultaneously to `ibm_kingston` (80,064 shots per circuit).

The hardware generated a distinct anomaly that challenges standard depth-minimization consensus:

1. **SABRE O3 (PUB 0):** Optimized the circuit to a highly efficient physical depth of **42**. However, the physical output suffered a severe ground-state collapse, returning 870 shots at the pure zero-state (`0...0`). This pooling of probability mass artificially lowered the Shannon entropy, indicating the distributed entanglement structure failed to survive the physical execution path.
2. **Prometheus (PUB 1):** Intentionally inflated the physical depth to **346**. Despite this massive physical depth penalty, the Prometheus topological mapping produced less concentration in the ground state and a higher-entropy output distribution, consistent with improved preservation of the distributed target-state structure.

| Pipeline | Physical Depth | Physical Gates (Total) | Ground-State (`0...0`) Shots | Shannon Entropy |
| :--- | :--- | :--- | :--- | :--- |
| **SABRE O3** | 42 | 290 | **870 / 80,064** | **9.1408 bits** |
| **Prometheus** | 346 | 1,309 | **672 / 80,064** | **9.5570 bits** |

*(Note: In a 13-qubit system, there are 8,192 possible states. A perfectly uniform distribution expects roughly 9.7 shots per state. In this specific distributed workload, a lower entropy score indicates undesirable pooling of amplitude mass, making entropy a diagnostic for distribution survival rather than a universal fidelity metric.)*

---

## Conclusion & Mechanism
This stress test demonstrates that physical circuit depth is not a sufficient predictor of measured distributional behavior on the tested QPU. In this 13-qubit workload, the substantially deeper Prometheus realization produced less concentration in the all-zero state and higher Shannon entropy than the depth-optimized SABRE realization. The result does not establish that additional depth is beneficial in general; rather, it demonstrates a regime in which minimizing depth alone fails to predict the observed hardware output.

The result is consistent with the possibility that physical placement and local hardware error structure can outweigh the benefit of minimizing circuit depth in this regime.

---

## Data Provenance & Tooling
To ensure a mathematically valid A/B test without transient hardware drift, both the SABRE baseline and the Prometheus circuit were batched into a single `SamplerV2` array and submitted simultaneously to `ibm_kingston`.

The execution payload was structured as follows:
* **PUB 0 (Index 0):** Unshielded SABRE Baseline (Optimization Level 3).
* **PUB 1 (Index 1):** Prometheus Mapping.

Reviewers unpacking the `job-info.json` payload can independently verify the compiler attribution by observing the physical gate depths stored in the Base64-encoded QPY circuits.

| Directory/File | Contents |
| :--- | :--- |
| `/base-qasm/` | The 13-qubit OpenQASM 3.0 logical blueprint used for generation. |
| `/data/` | Raw, unmodified `*-info.json` and `*-result.json` payloads downloaded directly from IBM Quantum. |
| `verify_benchmark.py` | Tooling to extract and verify physical depths from the compressed IBM logs, and to recalculate the output distributions. |

### Local Verification
To independently verify the physical payloads and hardware telemetry locally, execute the included extraction script:

    cd 04-topological-mapping-ground-state-avoidance
    python verify_benchmark.py

---

### Benchmark Scope & Limitations

**What this benchmark establishes**
* An 8× depth increase did not monotonically degrade the measured distribution in this specific stress test.
* The deeper physical realization exhibited less ground-state concentration and higher entropy.
* Physical circuit depth is not a sufficient predictor of measured distributional behavior.

**What this benchmark does not establish**
* Additional depth is beneficial in general.
* T1 amplitude decay is explicitly proven as the singular causal mechanism.
* Higher entropy guarantees higher computational correctness outside of this diagnostic context.
* The results scale infinitely to larger circuit depths or other processor architectures.

## Public evidence package

This experiment retains the logical workload(s), public aggregate data/figures supplied in the research archive, and the available IBM returned-result payloads. Routed and translated circuit artifacts are intentionally excluded.

### IBM evidence
- `IBM_Execution_Ledger/job-d971l1gtcv6s73dkc89g-result.json` — returned IBM execution result.

### Logical workloads
1 logical QASM file(s) are retained where supplied.


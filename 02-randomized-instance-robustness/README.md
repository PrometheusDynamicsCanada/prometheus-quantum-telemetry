# Prometheus: Randomized Instance Robustness

### Executive Summary
This repository tests a critical follow-up question from the Prometheus hardware-routing experiments:

> **Does the observed routing-cost/fidelity tradeoff survive when the logical problem instances themselves are randomized?**

A result obtained from a small number of carefully selected circuits can always raise the possibility of selection bias. To address that concern, this benchmark evaluates randomized logical instances spanning QAOA and CrossEnt workloads at $N=6$ through $N=9$. For each instance, the same logical problem is compiled independently by SABRE O3, TKET, and Prometheus and executed on the same IBM Heron processor (`ibm_marrakesh`).

The higher-cost/higher-fidelity regime occurs repeatedly across randomized matched instances, rather than appearing only in a hand-selected example. Across the matched hardware comparisons, Prometheus achieved higher measured Hellinger fidelity than SABRE O3 in 30 of 40 randomized instances (75%), despite generally accepting substantially higher routing cost.

The result does not establish universal superiority. Instead, it strengthens the narrower observation that the routing-cost/fidelity separation is not confined to a small collection of manually selected circuits. 

---

### Results at a Glance
| Benchmark | Instances | Prometheus vs SABRE | Routing tradeoff |
| :--- | :--- | :--- | :--- |
| **QAOA + CrossEnt** | 40 | 30/40 (75%) | Prometheus generally uses higher routing cost |
| **CrossEnt N=9** | 5 | 4/5 (80%) | Up to +971 additional 2Q gates per instance |
| **QAOA N=6–9** | 20 | Instance-dependent | Higher cost can coincide with higher fidelity |

> **Important:** The 75% figure is a matched-instance comparison against SABRE O3. It is not a claim that Prometheus wins 75% of all possible quantum circuits, nor that the result is statistically sufficient by itself to establish universal superiority.

---

### 1. Experimental Question
The benchmark tests whether the following regime occurs repeatedly:

$$
\Delta C_{\mathrm{routing}} > 0 \quad \text{while simultaneously observing} \quad \Delta F_H > 0
$$

where:
* $\Delta C_{\mathrm{routing}}$ is the additional physical routing cost incurred by Prometheus relative to SABRE O3.
* $\Delta F_H$ is the change in measured Hellinger fidelity.
* $F_H$ measures agreement between the experimentally observed logical distribution and the exact ideal distribution.

The interesting region is therefore **Higher routing cost + higher measured fidelity**. 

This does not imply that the additional SWAPs or 2Q gates are individually beneficial. It means that the complete physical implementation, including its qubit placement, coupler selection, routing sequence, and additional operations, can produce a better measured logical distribution than a lower-cost implementation on the tested hardware.

---

### 2. Strongest Randomized Evidence: CrossEnt N=9
The CrossEnt N=9 workload contains some of the clearest examples of the routing-cost/fidelity separation. At $N=9$, Prometheus uses a substantially larger physical circuit than SABRE O3.

For example, the randomized telemetry (Instance 5) illustrates the magnitude of the routing difference:

| Metric | SABRE O3 | Prometheus | $\Delta$ |
| :--- | :--- | :--- | :--- |
| **Physical depth** | 264 | 986 | **+722** |
| **Logical abstract 2Q gates** | 72 | 72 | **0** |
| **Routed abstract 2Q gates** | 193 | 1,164 | **+971** |
| **Unique physical couplers** | 8 | 16 | **+8** |
| **Hellinger fidelity** | 0.6438 | 0.7450 | **+0.1012** |

The Prometheus implementation uses 971 additional routed 2Q operations and substantially greater physical depth, yet produces a higher measured Hellinger fidelity and lower Total Variation Distance (TVD). 

---

### 3. Quadrant Analysis
The primary analysis script included in this repository compares $\Delta C_{\mathrm{routing}}$ against $\Delta F_H$. This produces four conceptually important regions, with the exact counts from the 40 matched instances:

* **Higher cost / higher fidelity (30/40):** Hardware-aware routing tradeoff.
* **Higher cost / lower fidelity (10/40):** Routing penalty dominates.
* **Lower cost / higher fidelity (0/40):** Conventional optimization succeeds (not observed in this subset).
* **Lower cost / lower fidelity (0/40):** Lower routing cost does not guarantee better fidelity.

The higher-cost / higher-fidelity quadrant is the primary target of this experiment. Its existence demonstrates that routing cost alone cannot fully predict which physical realization will produce the best measured result on the tested hardware. 

The higher-cost / lower-fidelity quadrant (10/40 cases) is equally important. It prevents the experiment from being interpreted as evidence that additional routing is intrinsically beneficial. As routing overhead becomes sufficiently large, the physical penalty can dominate.

---

### 4. Repository Structure & Independent Verification
The repository is designed to minimize the amount of trust required in the Prometheus implementation. The per-instance telemetry and verification tooling required to independently reproduce the reported metrics are provided below.

| Component | Description |
| :--- | :--- |
| `verify_benchmark.py` | Unified analysis engine. Recursively parses payloads, calculates routing vs. fidelity yields, and outputs explicit quadrant boundaries. |
| `data/summary.csv` | Contains the complete, matched execution telemetry for all 40 randomized instances. |
| `/data/` | Contains the raw `*-result.json` payload logs. |

**To reproduce the analysis locally:**

    cd 02-randomized-instance-robustness
    python verify_benchmark.py

---

### Benchmark Scope & Limitations

**What this benchmark establishes**
* The higher-cost / higher-fidelity regime occurs repeatedly across randomized logical instances.
* Prometheus achieved higher measured Hellinger fidelity than SABRE O3 in 30/40 matched instances.
* The observed effect is not explained by a simple monotonic relationship between routed 2Q count and measured fidelity.
* The effect is workload- and instance-dependent.

**What this benchmark does not establish**
* Prometheus universally outperforms SABRE O3.
* Additional SWAPs or 2Q gates are intrinsically beneficial.
* Higher routing cost guarantees higher fidelity.
* The observed relationship generalizes automatically to other QPUs, workloads, or compilers.
* The 75% matched-instance win rate constitutes a universal performance probability.

## Public evidence package

This experiment retains the logical workload(s), public aggregate data/figures supplied in the research archive, and the available IBM returned-result payloads. Routed and translated circuit artifacts are intentionally excluded.

### IBM evidence
- `job-da1httsdedkc73er2k70-result.json` — returned IBM execution result.

### Logical workloads
40 logical QASM file(s) are retained where supplied.


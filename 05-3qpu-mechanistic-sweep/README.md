# Prometheus Benchmark: Multi-QPU Mechanistic Sweep (workload-dependent hardware condition analysis)

## Executive Summary
This experiment investigates whether a hardware-aware execution-selection architecture (Prometheus) interacts with the spatial structure of the error landscape across multiple physical quantum processors to achieve a topology-dependent advantage over standard heuristic compilers (SABRE O3 and TKET).

The central finding is that Prometheus can enter a regime in which it uses more physical 2Q operations while incurring lower hardware-derived execution cost, and this regime is highly hardware- and workload-dependent. The same routing philosophy behaves differently on different QPUs, proving that a global hardware-quality statistic can fail to predict the quality of a particular physical execution.

---

## Scientific Premise

Heuristic quantum routing algorithms typically optimize for a proxy metric: **minimum physical gate depth and two-qubit (2Q) operation count**. However, on heterogeneous hardware, gate count alone is an incomplete model of physical error exposure.

This benchmark evaluates the conditional relationship across $N \in \{6, 7, 8\}$ qubits:

$$
\mathbb{P}(\Delta \text{Quality} > 0 \mid \Delta C_{2Q} > 0, \Delta A < 0, N)
$$

Where:
* $\Delta C_{2Q} > 0$: Prometheus accepts a larger physical two-qubit gate count.
* $\Delta A < 0$: Prometheus secures a lower protected hardware-derived execution objective by routing through a cleaner physical subgraph.
* $\Delta \text{Quality} > 0$: Measured execution metric exceeds the baseline.

### Workload-Specific Quality Observables
To avoid ambiguous terminology, quality is measured using workload-specific metrics:
* **QAOA:** Expected MaxCut approximation value ($\langle C \rangle$).
* **QFT:** Target distribution top-1 state probability ($P_{\text{top1}}$).

---

## The Median Error Paradox

A global median error statistic provides a useful aggregate description of a QPU, but it does not describe the spatial distribution of error across the physical graph. 

In the calibration snapshot used here, `ibm_fez` had the lower global median 2Q error ($0.0028$) while `ibm_marrakesh` had the higher value ($0.0034$). Yet `ibm_marrakesh` contained physical regions that Prometheus could exploit to reduce hardware-derived execution cost.

* **Uniform Hardware (`ibm_fez`, `ibm_kingston`):** These devices displayed relatively homogeneous calibration profiles. Under uniform conditions, SABRE O3 secured lower execution costs ($\Delta A > 0$) because the hardware lacked a distinct quiet zone strong enough to offset the Prometheus routing overhead.
* **Heterogeneous Hardware (`ibm_marrakesh`):** Despite higher global median error, `ibm_marrakesh` contained contiguous low-error subgraphs. Prometheus isolated these favorable hardware regions, achieving $\Delta A < 0$ in ~48% of trials.

---

## Key Empirical Findings

1. **topology-dependent execution behavior:** On `ibm_marrakesh`, conditional on entering the higher-2Q/lower-execution-cost regime ($\Delta C_{2Q} > 0, \Delta A < 0$), Prometheus won **67% of measured QAOA MaxCut comparisons** for $N \in \{6, 7\}$. For deep QFT workloads, the hardware-selection effect was weaker (38% conditional win rate).
2. **Suboptimal on Uniform Hardware:** On `ibm_fez` and `ibm_kingston`, the topological constraint incurred routing overhead without securing a sufficient regional error advantage, confirming that detour routing is disadvantageous on homogeneous error profiles.
3. **Routing-Dominated Regime at $N=8$:** At $N=8$, the tested workloads entered a routing-dominated regime across the evaluated devices: the additional physical cost exceeded the observed regional execution-cost advantage.

---

## Data Provenance & Tooling

The benchmark comprises 540 paired logical executions totaling ~1.1 million hardware shots across `ibm_fez`, `ibm_kingston`, and `ibm_marrakesh` (IBM Heron Architecture).

| Component | Description |
| :--- | :--- |
| `verify_benchmark.py` | Unified local verifier to extract payloads and calculate the conditional win rates. |
| `data/` | Contains the raw `*-info.json` and `*-result.json` payloads. |

### Local Verification

To run the offline analysis on the local JSON execution records:

    cd 05-3qpu-mechanistic-sweep
    python verify_benchmark.py

---

### Benchmark Scope & Limitations

**What this benchmark establishes**
* A global hardware-quality statistic (like median ECR) can fail to predict execution quality because it obscures spatial error distribution.
* The observed routing-cost/fidelity tradeoff is directly dependent on the specific QPU topology and calibration conditions.
* Detour routing is suboptimal on QPUs with relatively homogeneous error profiles.

**What this benchmark does not establish**
* Prometheus universally outperforms heuristic compilers across all devices.
* The protected execution-cost calculation should not be interpreted as a perfect causal mapping of physical noise.

## Public evidence package

This experiment retains the logical workload(s), public aggregate data/figures supplied in the research archive, and the available IBM returned-result payloads. Routed and translated circuit artifacts are intentionally excluded.

### IBM evidence
- `mechanistic_sweep_fez/job-da2hqsc3jnrc73aduof0-result.json` — returned IBM execution result.
- `mechanistic_sweep_kingston/job-da2i2hbotlns7398iqrg-result.json` — returned IBM execution result.
- `mechanistic_sweep_marrakesh/job-da2ibseaa69c739hhqc0-result.json` — returned IBM execution result.

### Logical workloads
0 logical QASM file(s) are retained where supplied.


# Prometheus Benchmark: Micro-Gradient Scaling Boundaries

## Executive Summary
This repository contains the hardware telemetry and verification artifacts for an experimental study of quantum-computer routing across deterministic scaling gradients.

The central question investigated is:

> **Can a quantum compiler sometimes obtain a better hardware result by accepting additional routing cost in exchange for a different physical placement of the computation?**

Conventional routing strategies commonly place substantial emphasis on minimizing routing cost, as additional operations generally introduce additional opportunities for error. However, a real QPU is not spatially homogeneous.

Prometheus explores this possibility by deliberately allowing higher routing cost when doing so produces a preferred physical placement. The experiments reported here identify both **Topological advantage** regimes (where higher-cost physical realizations produced substantially higher measured Hellinger fidelity) and **Routing penalty dominant** regimes (where the routing cost became dominant and the advantage disappeared).

The result is therefore not *"more gates are better,"* but rather: **"Minimizing routing cost alone may be insufficient to predict hardware execution quality."**

---

### Results at a Glance

| Experiment | Routing cost | $\Delta$ Hellinger fidelity | Interpretation |
|---|---:|---:|---|
| **QFT-9** | +242 2Q gates vs SABRE O3 | +0.1197 | Topological advantage |
| **QAOA-6** | +32 2Q gates vs SABRE O3 | +0.1627 | Topological advantage |
| **QAOA-9** | +65 2Q gates vs SABRE O3 | +0.1461 | Topological advantage |
| **QAOA-10** | +89 2Q gates vs SABRE O3 | -0.0591 | Routing penalty dominant |
| **QFT-10** | +432 2Q gates vs SABRE O3 | -0.0306 | Routing penalty dominant |

*(Note: The fidelity values above are Hellinger fidelities calculated against the exact ideal logical output distribution after inverse physical mapping)*.

Because the physical processor is not spatially uniform, scaling the logical problem changes the physical subgraphs available to the compiler. In the observed data, this produces workload- and scale-dependent transitions between topological-advantage and routing-penalty regimes. An increase in problem size can change the physical subgraph available to a given routing strategy, potentially increasing exposure to less favorable hardware regions. 

Crucially, the sign of the change in measured Hellinger fidelity does not follow the change in routing cost monotonically. This operating envelope demonstrates that the relevant variable is not routing cost in isolation, but the tradeoff between routing overhead and the physical execution environment reached by that routing.

---

### Experimental Design
The principal benchmark job contains **96 compiled circuit instances** spanning multiple compiler pipelines (SABRE O3, TKET, Prometheus), circuit families (QFT, QAOA MaxCut, CrossEnt, GHZ), and problem sizes ($N=3$ through $N=10$). 

With 10,000 shots per circuit, the benchmark represents 960,000 total hardware shots. The circuits were submitted through a single, unified Qiskit Runtime SamplerV2 execution job (`job-da1do46g52gs73clh7c0`) on `ibm_marrakesh` to reduce the possibility that differences between independently scheduled jobs were simply caused by temporal calibration drift. 

Dynamical decoupling and Pauli twirling were disabled for this benchmark.

---

### Repository Structure & Independent Verification
The proprietary routing heuristics are not required to reproduce the reported hardware observations. The repository instead provides the resulting compiled circuits, the raw hardware payloads, and the python scripts needed to audit the measurements locally.

| Component | Description |
| :--- | :--- |
| `verify_benchmark.py` | Analyzes the data payload and outputs the specific routing costs and Hellinger fidelity $\Delta$ for each topological structure. |
| `data/summary.csv` | Contains the complete, matched execution telemetry for all 96 scaling instances. |
| `/data/` | Contains the raw `*-result.json` payload logs. |

**To reproduce the analysis locally:**
```bash
cd 03-micro-gradient-scaling
python verify_benchmark.py

## Public evidence package

This experiment retains the logical workload(s), public aggregate data/figures supplied in the research archive, and the available IBM returned-result payloads. Routed and translated circuit artifacts are intentionally excluded.

### IBM evidence
- `job-da1do46g52gs73clh7c0-result.json` — returned IBM execution result.

### Logical workloads
32 logical QASM file(s) are retained where supplied.


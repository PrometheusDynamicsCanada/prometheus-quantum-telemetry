# Public disclosure boundary

This repository is intended to provide substantial primary evidence without publishing the protected execution-selection mechanism.

## Included
- logical workloads
- experimental descriptions
- aggregate results and measurements
- figures
- IBM job IDs and safe provenance
- returned IBM result payloads supplied in the source archive
- decoded counts where already present

## Excluded
- routed/translated QASM
- physical layouts and execution trajectories
- internal scoring equations and coefficients
- proprietary feature construction and weighting
- mechanistic manifests containing intermediate protected calculations
- serialized IBM request payloads and account identifiers
- job ZIP bundles where the request payload is embedded

Removal of request metadata does not alter returned result payloads. The purpose is to remove unnecessary implementation/account material while preserving the measurement evidence.

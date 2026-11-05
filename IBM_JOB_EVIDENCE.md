# IBM job evidence

The files under the experiment directories are the returned IBM execution result payloads supplied in the original research archive. These are retained as primary measurement evidence.

The accompanying `*-metadata.json` files contain only safe provenance fields such as backend, job ID, timestamp, status, and runtime estimate. Serialized request/circuit payloads and account identifiers are omitted.

`IBM_JOB_EVIDENCE_INDEX.csv` provides SHA-256 hashes for every retained result payload so the public evidence can be checked for alteration after publication.

Experiment 04 is explicitly represented under `04-topological-mapping-ground-state-avoidance/IBM_Execution_Ledger/`.

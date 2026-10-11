# Resource Pool Redeployment

This local Frontier-Engineering package contains a deterministic engineering
workflow, synthetic input fixture, editable solver, and an executable verifier.
The candidate may edit only `scripts/init.py`; input data and verification code
are copied into the benchmark sandbox as read-only files.

## Local checks

```bash
python verification/evaluator.py scripts/init.py
python -m frontier_eval task=unified task.benchmark=ScientificComputing/ResourcePoolRedeployment algorithm.iterations=0
```

The objective is recomputed from the provided synthetic inputs and the official constraint
checker. A score printed by the candidate is never trusted. The input is a synthetic fixture generated for this benchmark. It contains no user records, credentials, or external private data.

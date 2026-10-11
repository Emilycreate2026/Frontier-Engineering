# Stacked Freight Campaign

This local Frontier-Engineering package contains a deterministic engineering
workflow, public input fixture, editable solver, and an executable verifier.
The candidate may edit only `scripts/init.py`; input data and verification code
are copied into the benchmark sandbox as read-only files.

## Local checks

```bash
python verification/evaluator.py scripts/init.py
python -m frontier_eval task=unified task.benchmark=FreightOperations/StackedFreightCampaign algorithm.iterations=0
```

The objective is recomputed from the public inputs and the official constraint
checker. A score printed by the candidate is never trusted. The source is a
competition-derived fixture; the provenance and redistribution review are
recorded in `references/source.txt` and must be completed before publication.

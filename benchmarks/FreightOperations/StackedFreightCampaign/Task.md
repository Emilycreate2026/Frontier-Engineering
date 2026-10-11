# Multi-truck freight loading

Load all item quantities into compatible stacks and trucks while preserving
delivery windows, route and plant compatibility, stackability, nesting,
orientation, non-overlap, unloading order, vehicle weight and axle limits.
The complete public ROADEF-derived instance is under `environment/data` and
the full constraints are in `environment/RULES.txt`.

The candidate writes `output_items.csv`, `output_stacks.csv`, and
`output_trucks.csv` under `/app/results` using the exact semicolon-separated
schemas in `instruction.md`. The official Java checker verifies every physical
item, geometric and vehicle constraint and computes transportation plus
inventory cost. The disclosed authoring baseline is 2,457,693; lower is better.
This is a reproducible baseline for calibration, not a claim of global optimum.

# Scientific-computing resource-pool redeployment

Two public campaign files describe hosts, capacity pools, services,
dependencies, locations and workloads in a scientific-computing facility.
Assign every workload to one host while respecting resource capacities,
transient migration usage, service anti-collocation, minimum locations and
dependency neighbourhood coverage. Minimize load imbalance, safety-capacity
penalties and weighted migration cost.

For each input filename write the same filename under `/app/results` as
`{"placements": {workload_id: host_id}}`. The evaluator rejects duplicate or
missing workloads, unknown identifiers and every hard-constraint violation.
It then invokes the bundled official checker and recomputes the integer
objective. The two-campaign acceptance ceiling is 1,635,682,324. This is a
public diagnostic engineering target, not an Oracle implementation value or a
floating-point tolerance.

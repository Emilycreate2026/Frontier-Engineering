# Reassign scientific computing workloads across resource pools

Read both JSON campaign files under `/app/data/`. All inputs are public; there are no hidden additional instances.

Assign every workload in each campaign to exactly one host. The input includes capacity_pools, hosts, services, workloads, balance_costs, migration_weights and stable neighborhood/location orders. Per-resource arrays follow capacity_pools order; each host's migration_costs follows hosts order. Each workload identifies its service, demand vector, initial_host and migration_cost.

Hard constraints: total demand assigned to a host cannot exceed any resource capacity. For resources marked transient, a moved workload also consumes its demand on its original host during migration. Workloads of the same service must be on distinct hosts. Each service must occupy at least min_locations distinct host locations. If service A depends_on service B, every neighborhood containing an A workload must also contain a B workload.

Let U[h,r] be final usage and A[h,r]=capacity[h,r]-U[h,r]. Load cost sums load_weight[r]*max(0,U[h,r]-safety_capacity[h,r]). Each balance record adds weight*max(0,target*A[h,first]-A[h,second]) on every host. Migration cost is migration_weights[0] times the sum of migration_cost for moved workloads, plus migration_weights[1] times the maximum number of moved workloads in any one service, plus migration_weights[2] times the sum of initial-host-to-final-host migration_costs over all workloads (including unchanged assignments). Minimize the sum of these three cost categories across both campaigns. All objective arithmetic is integer; there is no numerical tolerance.

For each input filename, write the same filename under `/app/results/`, containing `{"placements": {"workload-id": "host-id", ...}}`. Include every workload exactly once. Unknown identifiers, duplicate JSON keys and missing workloads are rejected.

A solution receives reward 1 only if both campaigns are feasible and their summed objective is at most **1635682324**. Otherwise reward is 0. Any method is allowed. The optional `/app/tools/format.py` converts the public representation to a standard numeric interchange format and back; it contains no optimized answers.

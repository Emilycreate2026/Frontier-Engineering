# Optimize a complete multi-truck loading plan
Read the complete public competition instance in /app/data/campaign:
input_items.csv, input_trucks.csv, input_parameters.csv. These are semicolon-separated
CSV files; numeric decimal commas may occur. Do not modify these input files.
The full public problem specification is /app/RULES.txt (also RULES.pdf). Read it,
including constraints I1-I5, S1-S7, P1-P4 and all weight/axle restrictions, before coding.
This is the full ROADEF 2022 loading problem, not just a 2D packing subproblem.
Deliver every input item quantity by assigning items to compatible stacks and trucks;
respect delivery windows, route/supplier/plant compatibility, stackability and nesting,
orientation, dimensions, nonoverlap, unloading order, vehicle weight and axle loads.
Do not omit items. The original public instance and source attribution are retained
for this diagnostic pilot; it is not a finalized transformed benchmark release.

Write three semicolon-separated CSV files under /app/results, with one header row:
output_items.csv:
Item ident;Id truck;Id stack;Item code;X origin;Y origin;Z origin;X extremity;Y extremity;Z extremity
output_stacks.csv:
Id truck;Id stack;Stack code;X origin;Y origin;Z origin;X extremity;Y extremity;Z extremity
output_trucks.csv:
Id truck;Loaded length;Weight of loaded items;Volume of loaded items;EMm;EMr

Include one item row per physical unit (so Item ident repeats for input quantities).
Use unique stack identifiers and consistent truck/stack references. Item code and
Stack code are display labels; they do not replace the input Item ident.
Coordinates/dimensions are integer millimeters. Loaded length is integer millimeters,
weight/axle loads are kg, and volume is cubic meters. Numerical fields can use decimal
points or commas. Compute the truck summaries consistently with the specified formulas.
A planned truck keeps its input identifier P<suffix>. An extra copy uses Q<suffix>_<unique-copy-number>,
referring to the matching P<suffix>. Extra trucks are permitted by the original rules;
their transportation and inventory costs count toward the objective.

The official Java checker 1.11.4 validates the full output. Its constraint errors
are checked by the official verifier. Minimize the total transportation plus inventory cost.
No saved solution CSVs or commercial solver is supplied.


## Continuous source optimization
Improve the supplied reproducible solver. Minimize the sum of objective across the released instances, preserving every hard constraint. The current authoring baseline is 2457693. Continue reducing the raw objective even when reward is 1. This ceiling is provisional authoring bookkeeping, not a calibrated scientific quality standard.

Keep complete source under solution/ and an executable solve.sh that reads /app/data and freshly generates all outputs in /app/results. Build binaries in /tmp. No saved answers, instance-specific answer tables, hardcoded input identifiers, network dependencies, or private data. Use fixed seeds, deterministic work budgets, stable ordering and tie breaking. A candidate is retained only after two fresh legal generations with identical artifact hashes and metrics and a strictly smaller objective. Public helper libraries are in /app/tools when provided. Clean generation budget: 18000 seconds, 1 CPU, 24 GiB memory.

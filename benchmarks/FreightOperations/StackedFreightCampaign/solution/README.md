# multi-stage truck loading: deterministic feasibility solver

Run: `bash /app/submission/solve.sh`. It compiles `solver.cpp` into a temporary directory under /tmp,
which is deleted afterwards. It reads `/app/data/campaign/input_*.csv` and writes
`/app/results/output_{items,stacks,trucks}.csv`. The solver is single-threaded and uses no randomness
or wall-clock time, so clean runs produce byte-identical outputs.
`verify.py` is an optional independent checker for all rules (I1-I5, S1-S7, P1-P4, W1-W2, geometry, truck summaries).

How the solver works:
* Compatibility (I2-I5): the item's supplier, product and plant dock must appear in the truck rows,
  the plant must match, and IDE <= arrival time <= IDL.
* Trucks are processed in order of (arrival time, id). The candidates for a truck are its compatible
  unassigned items, sorted by earliest deadline first (index of the last compatible planned truck,
  then IDL). Items are added greedily; after each addition the stacks and layout are rebuilt and
  fully checked. A binary search finds the largest feasible partial quantity of an item.
* When a truck is the last compatible planned truck for some items that are still unassigned, extra
  copies `Q<suffix>_<n>` of that truck are filled until those items are all placed.
* Stacks (S1-S7): items are grouped by supplier, supplier dock, plant dock, stackability code, size
  and forced orientation, so every stack has a single dock. Stacks are filled first-fit by decreasing
  height under the height, max-stackability, density and weight-above-bottom limits. The bottom item
  is chosen so these limits hold.
* Layout (P1-P4): stacks are placed in columns that share the same x-length. Columns follow the
  supplier, supplier-dock and plant-dock loading orders (P4). Y positions are chosen so that every
  stack overlaps a stack in the previous column with positive length and meets the literal P3
  formula. If a column cannot satisfy this, it is split; a single-stack column can always be placed.
  Three column orders are tried (heavier toward the back, as formed, heavier toward the front).
  The first one that passes W1 and W2 (checked for each supplier pickup prefix) is used.
* Safety margins: 1 g for weight limits and 1 kg for axle limits.

Output conventions (confirmed with the trusted checker):
* The item z coordinates form a contiguous chain. The bottom item occupies [0, H]; each item above
  it occupies [prev_ze, prev_ze + H - nesting height]. The top item therefore ends at the stack height.
* Truck "Volume of loaded items" is the sum of stack volumes (length x width x stack height) in m^3.
* Stack code and item code are labels only (A, B, ... and A1, A2, ...). Stack ids are `<truck>_<k>`.

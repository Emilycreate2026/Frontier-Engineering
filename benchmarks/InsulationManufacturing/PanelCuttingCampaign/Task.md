# Insulation-panel production campaign

An insulation plant must cut six ordered batches of rectangular panels from
stock sheets with excluded regions. Parts can rotate by 90 degrees. The plan
is a complete staged guillotine-cut forest: every requested part appears once,
queue order is respected, exclusion rectangles and cut-stage limits are
respected, and unused material is classified as scrap or one retained offcut.

Inputs are the six JSON files in `environment/data`. For each input file write
the same filename under `/app/results` with a `panel-cut-tree-v1` JSON object
and a `nodes` array. Each node has `id`, `sheet`, integer `x/y/width/height`,
`stage`, `parent`, `role`, and `part_id` fields. A root covers a complete stock
sheet; part leaves must match the requested dimensions. The verifier rebuilds
the trees, checks all geometry and queue/exclusion rules, then computes the
exact integer loss from used stock area, retained offcut and part area.

The six public loss ceilings are 2,661,318; 11,931,095; 15,786,803;
21,951,533; 9,365,303; and 10,882,914 respectively. These are disclosed
engineering acceptance targets from the fixture, not a floating-point Oracle
value. A submission is accepted only when all six files are legal and each
loss is at or below its listed ceiling.

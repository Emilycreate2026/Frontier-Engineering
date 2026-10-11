# Insulation-panel production campaign

Plan six batches of rectangular insulation panels from ordered stock sheets with excluded regions. For each batch, produce every requested part exactly once, respect its production queue, and minimize unrecoverable material. The geometric and cutting constraints model a staged guillotine process.

Read the six JSON files in `/app/data`. Write one corresponding JSON file per batch under `/app/results`, with the same filename. All dimensions and coordinates are integers. Coordinates use the translated origin stored in each input; subtracting that origin is allowed, but submitted coordinates must use the input coordinate system. Stock sheets cannot rotate. Parts may rotate by 90 degrees.

## Input

- `stock_order`: ordered sheet identifiers. Use a prefix of this list, in that order. Every sheet has `stock_width` and `stock_height` and the same `coordinate_origin`.
- `parts`: each part has a unique `id`, `width`, `height`, `queue`, and `sequence`. Parts within each queue must emerge in increasing sequence order when the cutting trees are traversed depth first, with cuts processed in increasing coordinate order and sheets processed in stock order. Different queues may interleave. `queue_order` supplies a deterministic enumeration of queue identifiers; it does not impose production order between queues.
- `exclusions`: rectangular unusable regions, each attached to one sheet. Parts must not overlap their interiors; cut lines must not cross their interiors. Boundary contact is permitted.
- `cut_limits`: `first_min`, `first_max`, `second_min`, and `scrap_min` as described below.

## Cutting constraints

Each used sheet is the root of a rectangular partition tree. Every subdivision partitions its entire rectangle into adjacent, nonoverlapping children, with no gaps. Children at stages 1 and 3 are produced by vertical guillotine cuts, ordered from left to right; stages 2 and 4 are horizontal, ordered from bottom to top. A stage is the distance from the root (stage 0).

Each part must be a leaf with dimensions equal to its requested dimensions, allowing rotation. Parts may finish before stage 3. Stage 4 is allowed only as a single trimming cut of a stage-3 rectangle, producing two parts or one part and one scrap rectangle; no further cut is permitted. Each used sheet must contain a first-stage cut.

Non-scrap first-stage strips must have width at least `first_min` and at most `first_max`; the retained final offcut is exempt from the maximum. Non-scrap second-stage strips have height at least `second_min`. Every scrap rectangle has width and height at least `scrap_min`. All part rectangles and cut lines must satisfy the exclusion constraints. Only one retained offcut may be credited: the full-height, rightmost first-stage region of the last used sheet. Other unused material counts as scrap.

## Output

Each file is an object with `schema: "panel-cut-tree-v1"` and a `nodes` array. Each node contains:

- `id`: a unique nonempty string; `sheet`: an input sheet identifier.
- `x`, `y`, `width`, `height`: integer rectangle coordinates and dimensions.
- `stage`: integer 0 through 4.
- `parent`: the parent node identifier, or JSON `null` for a sheet root.
- `role`: `subdivision`, `part`, `scrap`, or `retained_offcut`.
- `part_id`: the input part identifier for a part; otherwise JSON `null`.

A root covers its entire sheet and has role `subdivision`. Node array order is irrelevant; the verifier reconstructs geometric cutting order. Nodes must form complete, connected trees. There may be no extra or missing parts, duplicated roots, unknown identifiers, or disconnected nodes.

`/app/tools/panel_format.py` provides answer-free helpers to convert inputs and solutions to or from a normalized CSV representation. It is optional and contains no solver or target solution.

## Objective and acceptance

For each batch minimize the exact integer loss:

`used_sheet_count * stock_width * stock_height - retained_offcut_width * stock_height - sum(part_width * part_height)`.

The last term uses the requested parts. If no retained offcut is declared, its width is zero. All constraints must pass and **every** batch must meet its listed loss ceiling:

| Batch | Maximum loss |
|---|---:|
| panel-campaign-01 | 2,661,318 |
| panel-campaign-02 | 11,931,095 |
| panel-campaign-03 | 15,786,803 |
| panel-campaign-04 | 21,951,533 |
| panel-campaign-05 | 9,365,303 |
| panel-campaign-06 | 10,882,914 |

Reward is 1 only if all six outputs are valid and meet these ceilings; otherwise it is 0. These are expert-achieved optimization targets. The evaluator uses exact integer objectives, with no floating-point tolerance. Improve the algorithm from the supplied inputs; do not retrieve stored solutions.

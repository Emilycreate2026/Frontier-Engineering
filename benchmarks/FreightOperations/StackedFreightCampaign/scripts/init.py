#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
# EVOLVE-BLOCK-START
exec "$ROOT/solution/solve.sh" "$ROOT/environment/data/campaign" "$ROOT/results"
# EVOLVE-BLOCK-END

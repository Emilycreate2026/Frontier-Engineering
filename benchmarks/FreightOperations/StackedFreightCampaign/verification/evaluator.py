#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
UP = ROOT / "verification" / "upstream-tests"
sys.path.insert(0, str(UP))
from check import evaluate
candidate = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "scripts" / "init.py"
subprocess.run([str(candidate)], cwd=str(ROOT), env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
               check=True, timeout=1800)
submission = ROOT / "results"
result = evaluate(ROOT / "environment" / "data", submission)
(ROOT / "metrics.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, sort_keys=True))
raise SystemExit(0 if result.get("valid") else 1)

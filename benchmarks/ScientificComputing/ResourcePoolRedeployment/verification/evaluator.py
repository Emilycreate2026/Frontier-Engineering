#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "environment" / "data"
UP = ROOT / "verification" / "upstream-tests"
sys.path.insert(0, str(UP))
from evaluate import evaluate
with tempfile.TemporaryDirectory(prefix="resource-eval-") as td:
    candidate = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "scripts" / "init.py"
    subprocess.run([str(candidate)], cwd=str(ROOT), env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                   check=True, timeout=1800)
    checker = Path(td) / "checker"
    off = UP / "official"
    subprocess.run(["g++", "-std=c++11", "-O2", str(off / "solution_checker.cc"),
                    str(off / "solution_checker_run.cc"), "-o", str(checker)], check=True)
    submission = ROOT / "results"
    result = evaluate(DATA, submission, UP / "official")
    (ROOT / "metrics.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result.get("reward") == 1 else 1)

#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys

# EVOLVE-BLOCK-START
def main() -> None:
    root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, str(root / 'solution' / 'solve.py')],
                   cwd=str(root / 'solution'), check=True)
# EVOLVE-BLOCK-END

if __name__ == '__main__':
    main()

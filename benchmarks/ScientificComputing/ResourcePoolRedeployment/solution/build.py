import subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
(R/'classes').mkdir(exist_ok=True)
subprocess.run(['javac','-encoding','UTF-8','-d',str(R/'classes')]+[str(p) for p in sorted((R/'src').rglob('*.java'))],check=True)

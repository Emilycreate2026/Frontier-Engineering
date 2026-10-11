#!/usr/bin/env python3
import argparse,json,os,subprocess,sys,tempfile
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',default='/app/data');p.add_argument('--output',default='/app/results');p.add_argument('--tools',default='/app/tools');p.add_argument('--solver',default=str(Path(__file__).parent/'solver'));p.add_argument('--budget',type=int,default=4000000);a=p.parse_args()
    sys.path.insert(0,a.tools);from panel_format import export_input,import_plan
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,SOLVER_NODE_BUDGET=str(a.budget),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONHASHSEED='0')
    for path in sorted(Path(a.data).glob('*.json')):
        data=json.loads(path.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp);export_input(data,work);sol=work/'case_solution.csv'
            subprocess.run([str(Path(a.solver).resolve()),'-p',str(work/'case'),'-g',str(work/'global_param.csv'),'-o',str(sol),'-i',str(work/'metrics.json')],env=env,cwd=work,check=True,timeout=7200)
            (out/path.name).write_text(json.dumps(import_plan(data,sol),sort_keys=True,separators=(',',':'))+'\n')
if __name__=='__main__':main()

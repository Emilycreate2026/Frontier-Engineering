import json,os,sys,subprocess,tempfile
from pathlib import Path
sys.path.insert(0,'/app/tools')
from format import maintenance_native,deployment_native,encode
R=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(R/'build.py')],check=True)
Path('/app/results').mkdir(exist_ok=True)
for case in sorted(Path('/app/data').glob('*.json')):
    d=json.loads(case.read_text())
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)
        if d['kind']=='maintenance':
            (p/'input.json').write_text(json.dumps(maintenance_native(d)))
            command=[str(R/'expert'),'-p',str(p/'input.json'),'-o',str(p/'answer'),'-s','0','-x','1','-y','1']
        else:
            model,initial=deployment_native(d);(p/'model').write_text(model);(p/'initial').write_text(initial)
            command=['java','-Xmx4g','-XX:ActiveProcessorCount=1','-cp',str(R/'classes'),'be.kahosl.roadef2012.Main','-p',str(p/'model'),'-i',str(p/'initial'),'-o',str(p/'answer'),'-s','20261006']
        subprocess.run(command,cwd=p,env=dict(os.environ,SOLVER_NODES='1000',SOLVER_ITERATIONS='100000',OMP_NUM_THREADS='1'),check=True,timeout=7200)
        encode(case,p/'answer',Path('/app/results')/case.name)

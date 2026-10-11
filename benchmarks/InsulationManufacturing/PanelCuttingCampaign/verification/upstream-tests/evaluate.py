#!/usr/bin/env python3
"""Validate submitted trees with the archived official checker and exact integer loss."""
import argparse,csv,json,subprocess,tempfile
from pathlib import Path
from panel_format import export_input,export_plan

# Published benchmark targets, from independently checked saved expert certificates.
# Reproducing the expert program at these targets remains a release gate.
TARGETS = {'panel-campaign-01':2661318,'panel-campaign-02':11931095,
           'panel-campaign-03':15786803,'panel-campaign-04':21951533,
           'panel-campaign-05':9365303,'panel-campaign-06':10882914}

def evaluate(data_dir,submission,checker):
    results={}
    for key,target in TARGETS.items():
        try:
            source=Path(submission)/(key+'.json')
            if source.stat().st_size>32*1024*1024:raise ValueError('Oversized submission')
            data=json.loads((Path(data_dir)/(key+'.json')).read_text())
            plan=json.loads(source.read_text())
            with tempfile.TemporaryDirectory() as tmp:
                p=Path(tmp);inp=p/'instances_checker';export_input(data,inp);(p/'logs').mkdir()
                export_plan(data,plan,inp/'case_solution.csv')
                q=subprocess.run([str(Path(checker).resolve()),'case','0'],cwd=p,capture_output=True,timeout=60)
                if q.returncode:raise ValueError('Official checker did not complete successfully')
                with (p/'logs/case_statistics.csv').open() as f:stats=next(csv.DictReader(f,delimiter=';'))
                if stats['validSolution']!='1':raise ValueError('Official constraints violated')
                area=sum(x['width']*x['height'] for x in data['parts'])
                loss=int(stats['nPlates'])*data['stock_width']*data['stock_height']-int(stats['widthResidual'])*data['stock_height']-area
                if loss<0:raise ValueError('Inconsistent negative loss')
                results[key]={'valid':True,'loss':loss,'target':target,'gap':loss-target,'passed':loss<=target}
        except Exception as e:
            results[key]={'valid':False,'passed':False,'error':str(e)}
    return {'reward':int(all(x['passed'] for x in results.values())),'cases':results,
            'total_loss':sum(x['loss'] for x in results.values()) if all(x['valid'] for x in results.values()) else None}

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',default='/tests/data');p.add_argument('--submission',default='/app/results');p.add_argument('--checker',default='/tests/checker');p.add_argument('--logs',default='/logs/verifier');a=p.parse_args()
    out=evaluate(a.data,a.submission,a.checker);d=Path(a.logs);d.mkdir(parents=True,exist_ok=True)
    (d/'report.json').write_text(json.dumps(out,indent=2)+'\n');(d/'reward.txt').write_text(str(out['reward'])+'\n');print(json.dumps(out))
if __name__=='__main__':main()

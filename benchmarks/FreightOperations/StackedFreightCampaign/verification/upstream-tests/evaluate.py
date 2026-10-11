import argparse,json,math
from pathlib import Path
from check import evaluate
p=argparse.ArgumentParser();p.add_argument('--solution',default='/app/results');p.add_argument('--out',default='/logs/verifier');a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
try:
 r=evaluate(Path(__file__).parent/'data',a.solution)
 if r.get('valid'):
  r['objective']=sum(c['objective'] for c in r['cases'].values())
  if not math.isfinite(r['objective']):r['valid']=False
 r['reward']=int(r.get('valid') is True and r['objective']<=2457693)
except Exception as e:r={'valid':False,'reward':0,'error':repr(e)}
r['baseline_ceiling']=2457693
r['threshold_scope']='internal authoring baseline, not an independently calibrated scientific acceptance criterion'
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
(out/'reward.txt').write_text(str(r['reward'])+'\n')
print(json.dumps(r))

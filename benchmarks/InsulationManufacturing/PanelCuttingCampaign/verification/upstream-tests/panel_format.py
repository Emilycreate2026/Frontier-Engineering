"""Public, answer-free conversion between panel JSON and normalized cutting CSV."""
import csv
from pathlib import Path


def integer(x):
    if type(x) is not int or not -(2**30) < x < 2**30:
        raise ValueError('Coordinates and dimensions must be bounded JSON integers')
    return x


def unique(values):
    if any(not isinstance(x, str) or not x for x in values) or len(set(values)) != len(values):
        raise ValueError('Identifiers must be unique nonempty strings')
    return {x: i for i, x in enumerate(values)}


def write_csv(path, fields, rows):
    with Path(path).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields.split(';'), delimiter=';', lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def read_csv(path):
    with Path(path).open(newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def mappings(data):
    return (unique([v['id'] for v in data['parts']]),
            unique(data['queue_order']), unique(data['stock_order']))


def export_input(data, folder):
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    parts, queues, sheets = mappings(data)
    ox, oy = data['coordinate_origin']
    write_csv(folder/'case_batch.csv', 'ITEM_ID;LENGTH_ITEM;WIDTH_ITEM;STACK;SEQUENCE', [
        dict(ITEM_ID=parts[v['id']], LENGTH_ITEM=v['width'], WIDTH_ITEM=v['height'],
             STACK=queues[v['queue']], SEQUENCE=v['sequence']) for v in data['parts']])
    # Defect order has no semantic meaning; use a stable public ordering.
    zones = sorted(data['exclusions'], key=lambda v: (sheets[v['sheet']], v['x'], v['y'], v['id']))
    write_csv(folder/'case_defects.csv', 'DEFECT_ID;PLATE_ID;X;Y;WIDTH;HEIGHT', [
        dict(DEFECT_ID=i, PLATE_ID=sheets[v['sheet']], X=v['x']-ox, Y=v['y']-oy,
             WIDTH=v['width'], HEIGHT=v['height']) for i,v in enumerate(zones)])
    limits = data['cut_limits']
    params = dict(nPlates=len(sheets), widthPlates=data['stock_width'], heightPlates=data['stock_height'],
                  min1Cut=limits['first_min'], max1Cut=limits['first_max'], min2Cut=limits['second_min'], minWaste=limits['scrap_min'])
    write_csv(folder/'global_param.csv', 'NAME;VALUE', [dict(NAME=k, VALUE=v) for k,v in params.items()])


def import_plan(data, path):
    rows = read_csv(path); ox,oy = data['coordinate_origin']; roles = {'-1':'scrap','-2':'subdivision','-3':'retained_offcut'}
    return {'schema':'panel-cut-tree-v1','nodes':[
        dict(id='node-'+r['NODE_ID'], sheet=data['stock_order'][int(r['PLATE_ID'])],
             x=int(r['X'])+ox, y=int(r['Y'])+oy, width=int(r['WIDTH']), height=int(r['HEIGHT']),
             role=roles.get(r['TYPE'],'part'),
             part_id=data['parts'][int(r['TYPE'])]['id'] if r['TYPE'] not in roles else None,
             stage=int(r['CUT']), parent='node-'+r['PARENT'] if r['PARENT'] else None) for r in rows]}


def export_plan(data, plan, path):
    if plan.get('schema') != 'panel-cut-tree-v1':
        raise ValueError('Unknown plan schema')
    nodes = plan['nodes']
    if not isinstance(nodes,list) or not 1 <= len(nodes) <= 100000:
        raise ValueError('Invalid node count')
    unique([v['id'] for v in nodes]); by_id={v['id']:v for v in nodes}
    parts, _, sheets = mappings(data); ox,oy=data['coordinate_origin']
    children={v['id']:[] for v in nodes}; roots=[]
    for v in nodes:
        if v['sheet'] not in sheets: raise ValueError('Unknown sheet')
        for key in ['x','y','width','height','stage']:integer(v[key])
        if v['width'] <= 0 or v['height'] <= 0 or not 0 <= v['stage'] <= 4:
            raise ValueError('Invalid rectangle/stage')
        if not (ox <= v['x'] < v['x']+v['width'] <= ox+data['stock_width'] and
                oy <= v['y'] < v['y']+v['height'] <= oy+data['stock_height']):
            raise ValueError('Rectangle outside sheet')
        if v['role'] not in ('part','scrap','subdivision','retained_offcut'):
            raise ValueError('Invalid role')
        if v['role']=='part':
            if v['part_id'] not in parts: raise ValueError('Unknown part')
        elif v.get('part_id') is not None: raise ValueError('Nonpart cannot name a part')
        if v['parent'] is None:
            if v['stage']!=0 or v['role']!='subdivision': raise ValueError('Invalid root')
            roots.append(v)
        else:
            p=by_id.get(v['parent'])
            if p is None or p['sheet']!=v['sheet'] or v['stage']!=p['stage']+1:
                raise ValueError('Invalid parent')
            if p['role']!='subdivision': raise ValueError('Leaf has children')
            children[p['id']].append(v)
    roots.sort(key=lambda v:sheets[v['sheet']])
    if [sheets[v['sheet']] for v in roots] != list(range(len(roots))):
        raise ValueError('Use a prefix of stock_order, once each')
    ordered=[]
    def visit(v):
        ordered.append(v)
        # Vertical stages 1/3 advance x; horizontal stages 2/4 advance y.
        axis='x' if (v['stage']+1)%2 else 'y'
        for child in sorted(children[v['id']],key=lambda c:(c[axis],c['id'])):visit(child)
    for root in roots:visit(root)
    if len(ordered)!=len(nodes):raise ValueError('Disconnected or cyclic tree')
    ids={v['id']:i for i,v in enumerate(ordered)};roles={'scrap':-1,'subdivision':-2,'retained_offcut':-3}
    write_csv(path,'PLATE_ID;NODE_ID;X;Y;WIDTH;HEIGHT;TYPE;CUT;PARENT',[
        dict(PLATE_ID=sheets[v['sheet']],NODE_ID=ids[v['id']],X=v['x']-ox,Y=v['y']-oy,
             WIDTH=v['width'],HEIGHT=v['height'],TYPE=parts[v['part_id']] if v['role']=='part' else roles[v['role']],
             CUT=v['stage'],PARENT=ids[v['parent']] if v['parent'] is not None else '') for v in ordered])

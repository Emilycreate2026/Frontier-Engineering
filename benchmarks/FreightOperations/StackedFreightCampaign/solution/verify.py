#!/usr/bin/env python3
"""Independent verifier for ROADEF 2022 truck loading outputs (literal rule checks)."""
import csv, sys, collections

def rd(path):
    with open(path, newline='', encoding='utf-8-sig') as fh:
        r = csv.reader(fh, delimiter=';')
        hdr = [h.strip() for h in next(r)]
        rows = [row for row in r if any(c.strip() for c in row)]
    return hdr, rows

def fl(s):
    s = s.strip().replace(',', '.')
    return float(s) if s else 0.0

def main(indir, outdir):
    errs = []
    def err(msg):
        if len(errs) < 200: errs.append(msg)
        else: errs.append(msg); 
    hi, irows = rd(f'{indir}/input_items.csv'); ii = {k: i for i, k in enumerate(hi)}
    ht, trows = rd(f'{indir}/input_trucks.csv'); it = {k: i for i, k in enumerate(ht)}
    items = {}
    for r in irows:
        g = lambda c: r[ii[c]].strip()
        items[g('Item ident')] = dict(sup=g('Supplier code'), sdock=g('Supplier dock'), plant=g('Plant code'), pdock=g('Plant dock'),
            prod=g('Product code'), qty=int(fl(g('Number of items'))), L=int(fl(g('Length'))), W=int(fl(g('Width'))), H=int(fl(g('Height'))),
            w=fl(g('Weight')), NH=int(fl(g('Nesting height'))), sc=g('Stackability code'), fo=g('Forced orientation').lower(),
            ide=int(g('Earliest arrival time')), idl=int(g('Latest arrival time')), ism=int(fl(g('Max stackability'))))
    trucks = {}
    for r in trows:
        g = lambda c: r[it[c]].strip()
        tid = g('Id truck')
        if tid not in trucks:
            trucks[tid] = dict(plant=g('Plant code'), tda=int(g('Arrival time')), L=int(fl(g('Length'))), W=int(fl(g('Width'))), H=int(fl(g('Height'))),
                maxw=fl(g('Max weight')), multi=g('Stack with multiple docks') in ('1', 'yes', 'Yes', 'true'), tem=fl(g('Max density')),
                EMmm=fl(g('EMmm')), EMmr=fl(g('EMmr')), CM=fl(g('CM')), CJfm=fl(g('CJfm')), CJfc=fl(g('CJfc')), CJfh=fl(g('CJfh')),
                EM=fl(g('EM')), EJhr=fl(g('EJhr')), EJcr=fl(g('EJcr')), EJeh=fl(g('EJeh')),
                supord={}, sdockord={}, pdockord={}, prods=set(), sups=set(), tmm={})
        t = trucks[tid]
        t['supord'][g('Supplier code')] = int(g('Supplier loading order'))
        if g('Supplier dock'): t['sdockord'][(g('Supplier code'), g('Supplier dock'))] = int(g('Supplier dock loading order'))
        t['pdockord'][g('Plant dock')] = int(g('Plant dock loading order'))
        t['prods'].add(g('Product code')); t['sups'].add(g('Supplier code'))
        t['tmm'][g('Product code')] = fl(g('Max weight on the bottom item in stacks'))
    # outputs
    hoi, oi = rd(f'{outdir}/output_items.csv')
    hos, os_ = rd(f'{outdir}/output_stacks.csv')
    hot, ot = rd(f'{outdir}/output_trucks.csv')
    exp_hi = 'Item ident;Id truck;Id stack;Item code;X origin;Y origin;Z origin;X extremity;Y extremity;Z extremity'.split(';')
    exp_hs = 'Id truck;Id stack;Stack code;X origin;Y origin;Z origin;X extremity;Y extremity;Z extremity'.split(';')
    exp_ht = 'Id truck;Loaded length;Weight of loaded items;Volume of loaded items;EMm;EMr'.split(';')
    if hoi != exp_hi: err(f'items header {hoi}')
    if hos != exp_hs: err(f'stacks header {hos}')
    if hot != exp_ht: err(f'trucks header {hot}')
    def base(tid):
        if tid.startswith('P'): return tid
        if tid.startswith('Q'):
            b = 'P' + tid[1:].rsplit('_', 1)[0]
            return b
        return None
    # stacks
    stacks = {}
    for r in os_:
        tid, sid, scode = r[0].strip(), r[1].strip(), r[2].strip()
        xo, yo, zo, xe, ye, ze = (int(fl(x)) for x in r[3:9])
        if sid in stacks: err(f'duplicate stack id {sid}')
        stacks[sid] = dict(tid=tid, xo=xo, yo=yo, zo=zo, xe=xe, ye=ye, ze=ze, items=[])
        if zo != 0: err(f'stack {sid} zo != 0')
        if base(tid) not in trucks: err(f'stack {sid} unknown truck {tid}')
    cnt = collections.Counter()
    for r in oi:
        ident, tid, sid = r[0].strip(), r[1].strip(), r[2].strip()
        xo, yo, zo, xe, ye, ze = (int(fl(x)) for x in r[4:10])
        cnt[ident] += 1
        if ident not in items: err(f'unknown item {ident}'); continue
        if sid not in stacks: err(f'item {ident} unknown stack {sid}'); continue
        s = stacks[sid]
        if s['tid'] != tid: err(f'item {ident} truck mismatch {tid} vs {s["tid"]}')
        s['items'].append(dict(ident=ident, xo=xo, yo=yo, zo=zo, xe=xe, ye=ye, ze=ze))
    for k, v in items.items():
        if cnt[k] != v['qty']: err(f'I1 item {k} count {cnt[k]} != {v["qty"]}')
    # per truck
    bytruck = collections.defaultdict(list)
    for sid, s in stacks.items(): bytruck[s['tid']].append(sid)
    tsum = {}
    for r in ot:
        tsum[r[0].strip()] = [fl(x) for x in r[1:6]]
    for tid in bytruck:
        if tid not in tsum: err(f'truck {tid} missing in output_trucks')
    for tid in tsum:
        if tid not in bytruck: err(f'truck {tid} listed but has no stacks')
    total_cost = 0.0
    for tid, sids in bytruck.items():
        T = trucks[base(tid)]
        multidock_codes = collections.Counter()
        W_tot = 0.0; vol = 0.0; maxx = 0
        sinfo = []
        for sid in sids:
            s = stacks[sid]
            its = sorted(s['items'], key=lambda d: d['zo'])
            if not its: err(f'stack {sid} empty'); continue
            I = [items[d['ident']] for d in its]
            # S1
            for key in ('sup', 'plant', 'sc', 'sdock'):
                if len(set(x[key] for x in I)) > 1: err(f'S1 stack {sid} differs in {key}')
            docks = set(x['pdock'] for x in I)
            if not T['multi'] and len(docks) > 1: err(f'S2 stack {sid} multiple docks')
            if T['multi'] and len(docks) > 1:
                if len(docks) > 2: err(f'S3 stack {sid} >2 docks')
                o = sorted(T['pdockord'].get(d, -99) for d in docks)
                if o[1] - o[0] != 1: err(f'S3 stack {sid} non consecutive docks')
                multidock_codes[I[0]['sc']] += 1
            # I2-I5
            for x in I:
                if x['plant'] != T['plant']: err(f'I2 {sid}')
                if x['prod'] not in T['prods']: err(f'I3 {sid} product {x["prod"]}')
                if x['sup'] not in T['sups']: err(f'I4 {sid}')
                if not (x['ide'] <= T['tda'] <= x['idl']): err(f'I5 {sid} {x["ide"]} {T["tda"]} {x["idl"]}')
                if x['pdock'] not in T['pdockord']: err(f'dock {x["pdock"]} not in truck {tid}')
            dx = s['xe'] - s['xo']; dy = s['ye'] - s['yo']
            L, Wd = I[0]['L'], I[0]['W']
            if (dx, dy) == (L, Wd): orient = 'lengthwise'
            elif (dx, dy) == (Wd, L): orient = 'widthwise'
            else: orient = None; err(f'stack {sid} dims {dx}x{dy} vs item {L}x{Wd}')
            for x in I:
                if (x['L'], x['W']) != (L, Wd): err(f'stack {sid} item dims differ')
                if x['fo'] in ('lengthwise', 'widthwise') and orient != x['fo']: err(f'S4 stack {sid} orient {orient} forced {x["fo"]}')
            # geometry of items
            z = 0
            for lvl, (d, x) in enumerate(zip(its, I)):
                if (d['xo'], d['yo'], d['xe'], d['ye']) != (s['xo'], s['yo'], s['xe'], s['ye']): err(f'item xy mismatch in {sid}')
                exp_zo = 0 if lvl == 0 else z   # contiguous z chain (checker convention)
                if d['zo'] != exp_zo: err(f'item zo {sid} lvl {lvl} {d["zo"]} exp {exp_zo}')
                exp_h = x['H'] if lvl == 0 else x['H'] - x['NH']
                if d['ze'] - d['zo'] != exp_h: err(f'item height {sid}')
                z = d['ze']
            if z != s['ze']: err(f'top item ze {z} != stack ze {s["ze"]} in {sid}')
            sh = sum(x['H'] for x in I) - sum(x['NH'] for x in I[1:])
            if s['ze'] != sh: err(f'stack height {sid} {s["ze"]} vs {sh}')
            sm = sum(x['w'] for x in I)
            # S5
            above = sm - I[0]['w']
            if above > T['tmm'][I[0]['prod']] + 1e-9: err(f'S5 {sid} above {above} > {T["tmm"][I[0]["prod"]]}')
            # S6
            if len(I) > min(x['ism'] for x in I): err(f'S6 {sid}')
            # S7
            if sm / ((L / 1000) * (Wd / 1000)) > T['tem'] + 1e-9: err(f'S7 {sid}')
            # P1
            if s['xo'] < 0 or s['yo'] < 0 or s['xe'] > T['L'] or s['ye'] > T['W'] or s['ze'] > T['H']: err(f'P1 {sid}')
            W_tot += sm; vol += dx * dy * s['ze'] / 1e9; maxx = max(maxx, s['xe'])  # stack volume
            sup = I[0]['sup']
            key1 = T['supord'][sup]
            key2 = T['sdockord'].get((sup, I[0]['sdock']), None)
            gds = [T['pdockord'][d] for d in docks]
            sinfo.append(dict(sid=sid, xo=s['xo'], xe=s['xe'], yo=s['yo'], ye=s['ye'], w=sm, sup=sup, so=key1, ko=key2, gds=gds))
        for sc, c in multidock_codes.items():
            if c > 1: err(f'S3 truck {tid} code {sc} has {c} multidock stacks')
        # P2
        n = len(sinfo)
        srt = sorted(sinfo, key=lambda d: d['xo'])
        for a in range(n):
            for b in range(a + 1, n):
                s1, s2 = srt[a], srt[b]
                if s2['xo'] >= s1['xe']: break
                if not (s2['yo'] >= s1['ye'] or s2['ye'] <= s1['yo']): err(f'P2 overlap {s1["sid"]} {s2["sid"]}')
        # P3 literal and strict
        for s1 in sinfo:
            if s1['xo'] > 0:
                lit = any(s2['xe'] == s1['xo'] and (s1['yo'] <= s2['yo'] <= s1['ye'] or s1['yo'] <= s2['ye'] <= s1['ye']) for s2 in sinfo)
                strict = any(s2['xe'] == s1['xo'] and s2['yo'] < s1['ye'] and s2['ye'] > s1['yo'] and (s1['yo'] <= s2['yo'] <= s1['ye'] or s1['yo'] <= s2['ye'] <= s1['ye']) for s2 in sinfo)
                if not lit: err(f'P3 literal fail {s1["sid"]}')
                elif not strict: err(f'P3 strict fail {s1["sid"]}')
        # P4
        for s1 in sinfo:
            for s2 in sinfo:
                if s1['so'] < s2['so'] and not s1['xo'] <= s2['xo']: err(f'P4(1) {s1["sid"]} {s2["sid"]}')
                if s1['sup'] == s2['sup'] and s1['ko'] is not None and s2['ko'] is not None and s1['ko'] < s2['ko'] and not s1['xo'] <= s2['xo']: err(f'P4(2) {s1["sid"]} {s2["sid"]}')
                if s1['sup'] == s2['sup'] and s1['ko'] == s2['ko'] and all(g1 < g2 for g1 in s1['gds'] for g2 in s2['gds']) and not s1['xo'] <= s2['xo']:
                    err(f'P4(3) {s1["sid"]} {s2["sid"]}')
        # W1
        if W_tot > T['maxw'] + 1e-9: err(f'W1 {tid} {W_tot}')
        # W2 per supplier prefix
        def axle(sub):
            tm = sum(d['w'] for d in sub)
            if tm <= 0: return 0, 0
            eje = sum((d['xo'] + (d['xe'] - d['xo']) / 2) * d['w'] for d in sub) / tm
            ejr = T['EJeh'] + T['EJhr'] - eje
            emh = (tm * ejr + T['EM'] * T['EJcr']) / T['EJhr']
            emr = tm + T['EM'] - emh
            emm = (T['CM'] * T['CJfc'] + emh * T['CJfh']) / T['CJfm']
            return emm, emr
        for o in sorted(set(d['so'] for d in sinfo)):
            emm, emr = axle([d for d in sinfo if d['so'] <= o])
            if emm > T['EMmm'] + 1e-9 or emr > T['EMmr'] + 1e-9: err(f'W2 {tid} prefix {o} emm {emm} emr {emr}')
        emm, emr = axle(sinfo)
        if tid in tsum:
            ll, ww, vv, em1, em2 = tsum[tid]
            if int(ll) != maxx: err(f'truck {tid} loaded length {ll} vs {maxx}')
            if abs(ww - W_tot) > 1e-6: err(f'truck {tid} weight {ww} vs {W_tot}')
            if abs(vv - vol) > 1e-6: err(f'truck {tid} volume {vv} vs {vol}')
            if abs(em1 - emm) > 1e-4: err(f'truck {tid} EMm {em1} vs {emm}')
            if abs(em2 - emr) > 1e-4: err(f'truck {tid} EMr {em2} vs {emr}')
    print(f'trucks used: {len(bytruck)} (extra {sum(1 for t in bytruck if t.startswith("Q"))}), stacks {len(stacks)}, item rows {len(oi)}')
    if errs:
        print(f'{len(errs)} ERRORS (first 50):')
        for e in errs[:50]: print('  ', e)
        return 1
    print('ALL CHECKS PASSED')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '/app/data/campaign', sys.argv[2] if len(sys.argv) > 2 else '/app/results'))

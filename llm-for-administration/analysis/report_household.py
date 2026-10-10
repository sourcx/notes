"""Huishoudens-cashflow: wat komt binnen (zzp, Tessa, overig), wat gaat uit, en wat komt uit sparen/beleggen.
Huishouden = Frank-rek, Samen-rek, Frank-sparen, Samen-sparen."""
import collections
from categorize import rows, OWN

HH = {'NL52SNSB0926827723','NL11SNSB0706257057','NL57SNSB8822509390','NL68SNSB8811784387'}

def flow_bucket(r):
    t = r['tegen']
    if t in HH: return None  # intern huishouden
    if t == 'NL61SNSB8839326014': return 'zzp -> privé (loon)'
    if t in OWN: return 'zzp-potje -> privé' if r['bedrag']>0 else 'privé -> zzp-potje'
    if r['groep']=='transfer' and r['cat']=='Tessa': return 'Tessa (netto)'
    if r['groep']=='transfer' and r['cat'].startswith('beleggen'): return 'beleggen/crypto (netto, +=opname)'
    if r['groep']=='transfer' and r['cat']=='eigen rekeningen':
        return 'ext. eigen rek (LPLN/overig) (netto)'
    if r['groep']=='inkomen': return 'overig inkomen'
    if r['cat']=='belasting (privé)': return 'uit: belasting privé'
    if r['cat']=='wonen: hypotheek/huur': return 'uit: wonen'
    return 'uit: overige uitgaven'

def run(periods):
    R = [r for r in rows() if r['rek'] in HH]
    out = collections.defaultdict(lambda: collections.defaultdict(float))
    for r in R:
        k = flow_bucket(r)
        if not k: continue
        for n,(a,z) in periods.items():
            if a <= r['maand'] <= z: out[n][k] += r['bedrag']
    return out

if __name__ == '__main__':
    P = {'24 jan-sep': ('2024-01','2024-09'), '25 jan-sep': ('2025-01','2025-09'), '26 jan-sep': ('2026-01','2026-09'),
         '25 okt-dec': ('2025-10','2025-12')}
    o = run(P)
    keys = sorted({k for p in o.values() for k in p})
    print(f"{'':42s}" + ''.join(f"{k:>12s}" for k in P))
    for k in keys:
        print(f"{k:42s}" + ''.join(f"{o[p][k]:12.0f}" for p in P))
    print(f"{'SALDO verandering huishouden':42s}" + ''.join(f"{sum(o[p].values()):12.0f}" for p in P))

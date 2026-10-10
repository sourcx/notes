"""Vergelijk uitgaven per categorie over perioden (huishouden = privé rekeningen)."""
import collections, sys
from categorize import rows

def table(periods, groep='uitgave'):
    R = rows()
    s = collections.defaultdict(lambda: collections.defaultdict(float))
    for r in R:
        if r['groep'] != groep: continue
        for name, (a, b) in periods.items():
            if a <= r['maand'] <= b:
                s[r['cat']][name] += -r['bedrag'] if groep=='uitgave' else r['bedrag']
    return s

if __name__ == '__main__':
    P = {'24 jan-sep': ('2024-01','2024-09'), '25 jan-sep': ('2025-01','2025-09'), '26 jan-sep': ('2026-01','2026-09'),
         '25 q4': ('2025-10','2025-12')}
    for g in ('uitgave','inkomen'):
        t = table(P, g)
        print('=====', g)
        print(f"{'':38s}" + ''.join(f"{k:>12s}" for k in P) + f"{'Δ26-25':>10s}")
        tot = collections.defaultdict(float)
        for cat, d in sorted(t.items(), key=lambda x: -x[1]['26 jan-sep']):
            print(f"{cat:38s}" + ''.join(f"{d[k]:12.0f}" for k in P) + f"{d['26 jan-sep']-d['25 jan-sep']:10.0f}")
            for k in P: tot[k]+=d[k]
        print(f"{'TOTAAL':38s}" + ''.join(f"{tot[k]:12.0f}" for k in P) + f"{tot['26 jan-sep']-tot['25 jan-sep']:10.0f}")

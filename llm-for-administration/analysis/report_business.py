"""Zakelijke cashflow: omzet, kosten, belasting, naar privé, en saldo van de potjes."""
from load import conn
import collections
c = conn()
Z = 'NL61SNSB8839326014'
POT = {'NL13SNSB8839767452':'ib1','NL35SNSB8839767444':'btw','NL60SNSB8839767479':'ib2','NL88SNSB8839767460':'buffer'}
PRIVE = 'NL52SNSB0926827723'
ZAK = set(POT)|{Z}

def bucket(r):
    rek, tegen, naam, b, om = r
    if rek != Z: return None
    if tegen in POT: return 'potje_heen' if b < 0 else 'potje_terug'
    if tegen == PRIVE: return 'naar_prive' if b < 0 else 'van_prive'
    if 'belastingdienst' in naam.lower(): return 'belastingdienst'
    if b > 0 and not naam.lower().startswith('hiscox'):
        return 'omzet'
    return 'kosten' if b < 0 else 'overig_in'

def period_table(periods):
    rows = c.execute("select rek,tegen,naam,bedrag,omschr,maand from tx where bron='zakelijk'").fetchall()
    out = collections.defaultdict(lambda: collections.defaultdict(float))
    for rek, tegen, naam, b, om, m in rows:
        k = bucket((rek, tegen, naam, b, om))
        if not k: continue
        for name, (a, z) in periods.items():
            if a <= m <= z: out[name][k] += b
    return out

if __name__ == '__main__':
    P = {'24 jan-sep': ('2024-01','2024-09'), '25 jan-sep': ('2025-01','2025-09'), '26 jan-sep': ('2026-01','2026-09'),
         '25 okt-dec': ('2025-10','2025-12'), 'jaar 2024': ('2024-01','2024-12'), 'jaar 2025': ('2025-01','2025-12')}
    t = period_table(P)
    keys = ['omzet','kosten','belastingdienst','naar_prive','van_prive','potje_heen','potje_terug']
    print(f"{'':20s}" + ''.join(f"{k:>12s}" for k in P))
    for k in keys:
        print(f"{k:20s}" + ''.join(f"{t[p][k]:12.0f}" for p in P))
    print(f"{'omzet ex btw (/1.21)':20s}" + ''.join(f"{t[p]['omzet']/1.21:12.0f}" for p in P))
    print(f"{'netto verandering hoofdrek':20s}" + ''.join(f"{sum(t[p][k] for k in keys+['overig_in']):12.0f}" for p in P))
    # saldi
    print('\nSaldo per rekening (cumulatief, start 0) op einddatum:')
    for rek in sorted(ZAK):
        for d in ('2024-12-31','2025-12-31','2026-09-30'):
            s = c.execute("select sum(bedrag) from tx where rek=? and datum<=?",(rek,d)).fetchone()[0] or 0
            print(f"  {rek} {d} {s:10.0f}", end='')
        print()
    print('\nTotaal alle zakelijke rekeningen:')
    for d in ('2024-12-31','2025-06-30','2025-12-31','2026-03-31','2026-06-30','2026-09-30'):
        s = c.execute("select sum(bedrag) from tx where bron='zakelijk' and datum<=?",(d,)).fetchone()[0]
        print(' ',d,round(s))

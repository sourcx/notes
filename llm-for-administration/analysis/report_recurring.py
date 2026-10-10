"""Vaste lasten: bedrag per maand per tegenpartij, vergelijking H2 2025 vs 2026."""
import collections, statistics
from categorize import rows

def key(r):
    return (r['naam'] or r['omschr'][:25]).strip().lower()

if __name__ == '__main__':
    R = [r for r in rows() if r['groep']=='uitgave' and r['type'] in ('EIC','IDE','IOI','NGI','OVS','IDM')]
    d = collections.defaultdict(lambda: collections.defaultdict(float))
    cnt = collections.defaultdict(lambda: collections.defaultdict(int))
    for r in R:
        d[key(r)][r['maand']] += -r['bedrag']; cnt[key(r)][r['maand']] += 1
    months = sorted({m for v in d.values() for m in v})
    print("Terugkerend (>=9 maanden met een betaling sinds 2025-01); gemiddelde per maand in:")
    print(f"{'tegenpartij':45s}{'2025 H1':>9s}{'2025 H2':>9s}{'2026 Q1':>9s}{'2026 Q2-3':>10s}{'  Δ(26Q2-3 vs 25H2)':>20s}")
    rowsout = []
    for k, v in d.items():
        ms = [m for m in v if m >= '2025-01']
        if len(ms) < 9: continue
        def avg(a, z, div):
            return sum(x for m, x in v.items() if a <= m <= z) / div
        a1, a2, a3, a4 = avg('2025-01','2025-06',6), avg('2025-07','2025-12',6), avg('2026-01','2026-03',3), avg('2026-04','2026-09',6)
        rowsout.append((k, a1, a2, a3, a4))
    for k,a1,a2,a3,a4 in sorted(rowsout, key=lambda x: -x[4]):
        print(f"{k[:45]:45s}{a1:9.0f}{a2:9.0f}{a3:9.0f}{a4:10.0f}{a4-a2:20.0f}")

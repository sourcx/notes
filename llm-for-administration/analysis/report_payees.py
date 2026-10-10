"""Top stijgers/dalers per tegenpartij (Jan-Sep 2026 vs Jan-Sep 2025) en nieuwe tegenpartijen in 2026."""
import collections, re
from categorize import rows

def name(r):
    if r['naam']: return r['naam'].strip()
    return re.split(r'\s{2,}|>', r['omschr'])[0].strip()

if __name__ == '__main__':
    R = [r for r in rows() if r['groep']=='uitgave']
    a = collections.defaultdict(float); b = collections.defaultdict(float); first = {}
    for r in R:
        n = name(r).lower()
        first.setdefault(n, r['maand'])
        if '2025-01' <= r['maand'] <= '2025-09': a[n] += -r['bedrag']
        if '2026-01' <= r['maand'] <= '2026-09': b[n] += -r['bedrag']
    keys = set(a)|set(b)
    d = sorted(keys, key=lambda k: b[k]-a[k])
    print("TOP STIJGERS (26 vs 25, jan-sep)")
    for k in d[::-1][:25]: print(f"  {b[k]-a[k]:9.0f}  25:{a[k]:8.0f}  26:{b[k]:8.0f}  {k[:50]}")
    print("TOP DALERS")
    for k in d[:25]: print(f"  {b[k]-a[k]:9.0f}  25:{a[k]:8.0f}  26:{b[k]:8.0f}  {k[:50]}")
    print("NIEUWE tegenpartijen in 2026 met >=150 euro")
    for k in sorted(keys, key=lambda k: -b[k]):
        if first[k] >= '2026-01' and b[k] >= 150: print(f"  {b[k]:9.0f}  eerst {first[k]}  {k[:50]}")

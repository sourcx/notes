"""Maandreeks: loon (zzp->privé), vaste lasten, variabele uitgaven, beleggen, saldo huishouden."""
import collections, re
from categorize import rows
from report_household import HH

FIXED = [('hypotheek', r'hypothe|^zents'), ('zorgverz.', r'zilveren kruis|aon nl|zorgpolis'), ('overige verz.', r'klaverblad|centraal beheer|hiscox'),
         ('energie/water/net', r'easyenergy|eneco|vitens|delta fiber|liander'), ('telefoon', r'^kpn'), ('DUO', r'duo|dienst uitvoering'),
         ('gemeente', r'gemeente (renkum|wageningen)|gem renkum'), ('kinderopvang', r'kinderopvang|speelboerderij'), ('beleggen (Meesman)', r'meesman')]

def run():
    R = [r for r in rows() if r['rek'] in HH and r['maand']>='2025-01']
    m = collections.defaultdict(lambda: collections.defaultdict(float))
    for r in R:
        mo = r['maand']; low=(r['naam']+' '+r['omschr']).lower(); b=r['bedrag']
        if r['tegen']=='NL61SNSB8839326014': m[mo]['loon']+=b; continue
        if r['groep']=='uitgave' or (r['groep']=='transfer' and 'meesman' in low and b<0):
            for k,rx in FIXED:
                if re.search(rx, low): m[mo][k]+=-b; break
            else:
                if r['cat']=='belasting (privé)': m[mo]['belasting privé']+=-b
                else: m[mo]['variabel']+=-b
        elif r['groep']=='inkomen' and r['cat'] not in ('bankkosten/rente',): m[mo]['overig in']+=b
    return m

if __name__=='__main__':
    m = run()
    cols = ['loon']+[k for k,_ in FIXED]+['variabel','belasting privé','overig in']
    print(f"{'maand':8s}"+''.join(f"{c[:9]:>10s}" for c in cols)+f"{'vast tot':>10s}")
    for mo in sorted(m):
        vast = sum(m[mo][k] for k,_ in FIXED)
        print(f"{mo:8s}"+''.join(f"{m[mo][c]:10.0f}" for c in cols)+f"{vast:10.0f}")

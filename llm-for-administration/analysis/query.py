#!/usr/bin/env python3
"""Snelle vragen aan de data. Alles lokaal, geen netwerk.

  python3 query.py sql "select ... from tx ..."      vrije SQL op tabel tx
  python3 query.py search <tekst> [vanaf-datum]      zoek in naam/omschrijving
  python3 query.py month 2026-05                     alle echte uitgaven/inkomsten in een maand, per categorie
  python3 query.py cat "boodschappen" [jaar-maand]   transacties in een categorie
  python3 query.py payee <naam>                      totaal per maand voor een tegenpartij

Kolommen tx: bron(prive|zakelijk) rek tegen naam datum maand jaar bedrag saldo_voor type volgnr omschr
"""
import sys, collections
from load import conn

def main(a):
    c = conn()
    if not a: print(__doc__); return
    cmd = a[0]
    if cmd == 'sql':
        cur = c.execute(a[1])
        print(' | '.join(d[0] for d in cur.description))
        for r in cur.fetchall(): print(' | '.join(str(x) for x in r))
    elif cmd == 'search':
        t = f"%{a[1]}%"; since = a[2] if len(a) > 2 else '0000'
        for r in c.execute("select datum,rek,naam,round(bedrag,2),substr(omschr,1,90) from tx where (naam like ? or omschr like ?) and datum>=? order by datum", (t, t, since)): print(r)
    elif cmd == 'month':
        from categorize import rows
        s = collections.defaultdict(float)
        for r in rows():
            if r['maand'] == a[1]: s[(r['groep'], r['cat'])] += r['bedrag']
        for (g, k), v in sorted(s.items()): print(f"{g:9s} {k:38s} {v:10.0f}")
    elif cmd == 'cat':
        from categorize import rows
        for r in rows():
            if r['cat'] == a[1] and (len(a) < 3 or r['maand'] == a[2]):
                print(r['datum'], r['rek'][-4:], round(r['bedrag'], 2), (r['naam'] or r['omschr'])[:60])
    elif cmd == 'payee':
        t = f"%{a[1]}%"
        for r in c.execute("select maand,count(*),round(sum(bedrag),2) from tx where naam like ? or omschr like ? group by 1 order by 1", (t, t)): print(r)

if __name__ == '__main__':
    main(sys.argv[1:])

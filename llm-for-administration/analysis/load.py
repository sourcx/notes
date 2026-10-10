"""Laadt alle SNS CSV's in een lokale SQLite DB (analysis/fin.db). Geen externe calls."""
import csv, glob, os, sqlite3
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "analysis", "fin.db")

def build():
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    con.execute("""create table tx(bron text, rek text, tegen text, naam text, datum text, maand text,
        jaar int, bedrag real, saldo_voor real, type text, volgnr text, omschr text)""")
    rows = []
    for kind in ("prive", "zakelijk"):
        for f in sorted(glob.glob(f"{BASE}/{kind}-extracted/*.csv")):
            with open(f, newline="", encoding="utf-8-sig") as fh:
                for r in csv.DictReader(fh):
                    dt = datetime.strptime(r["Datum"], "%d-%m-%Y")
                    om = r["Omschrijving"].strip().strip("'")
                    rows.append((kind, r["Je rekening"], r["Van / naar"], r["Naam"], dt.strftime("%Y-%m-%d"),
                                 dt.strftime("%Y-%m"), dt.year, float(r["Bedrag bij / af"]),
                                 float(r["Saldo voor boeking"] or 0), r["Type"], r["Volgnummer"], om))
    con.executemany("insert into tx values (?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    return con

def conn():
    return sqlite3.connect(DB)

if __name__ == "__main__":
    c = build()
    print(c.execute("select count(*) from tx").fetchone())

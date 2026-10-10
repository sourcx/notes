#!/usr/bin/env python3
"""Herbouwt fin.db uit de CSV's en draait alle rapporten naar analysis/reports/*.txt.
Nieuwe export? Zet de CSV's in ../prive-extracted en ../zakelijk-extracted (oude vervangen) en draai dit."""
import os, subprocess, sys
import load
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(f"{here}/reports", exist_ok=True)
print("tx rijen:", load.build().execute("select count(*) from tx").fetchone()[0])
for name in ("report_compare", "report_business", "report_household", "report_monthly", "report_recurring", "report_payees"):
    out = subprocess.run([sys.executable, f"{here}/{name}.py"], capture_output=True, text=True, cwd=here)
    open(f"{here}/reports/{name}.txt", "w").write(out.stdout + out.stderr)
    print("ok", name)

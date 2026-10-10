# analysis/ — financiële analyse (alleen lokaal, geen netwerk)

Startpunt voor toekomstige vragen. Lees eerst dit bestand, daarna `FINDINGS.md`.

## Gebruik
```
python3 run_all.py                       # herbouw fin.db uit de CSV's + alle rapporten in reports/
python3 query.py sql "select ..."        # vrije SQL, tabel tx
python3 query.py search easyenergy 2026-01-01
python3 query.py month 2026-05           # categorieoverzicht van een maand
python3 query.py cat boodschappen 2026-04
python3 query.py payee Jumbo
```
Alleen Python 3 stdlib (geen pandas). `fin.db` is afgeleid en genegeerd in git.
Nieuwe export van SNS: vervang de CSV's in `../prive-extracted/` en `../zakelijk-extracted/` en draai `run_all.py`.

## Bestanden
| bestand | doel |
|---|---|
| `load.py` | CSV → SQLite (`fin.db`, tabel `tx`) |
| `categorize.py` | classificatie: `groep` (transfer/uitgave/inkomen) + `cat`; regels in `RULES` en `MCC` |
| `report_compare.py` | uitgaven per categorie, jan–sep 24/25/26 |
| `report_business.py` | zakelijke cashflow (omzet, belasting, loon, potjes, saldi) |
| `report_household.py` | huishoudstromen incl. Tessa, beleggen, sparen |
| `report_monthly.py` | maandreeks loon / vaste lasten / variabel |
| `report_recurring.py` | vaste lasten per tegenpartij, gem./mnd per periode |
| `report_payees.py` | top stijgers/dalers per tegenpartij, nieuwe tegenpartijen |
| `reports/*.txt` | laatste uitvoer van bovenstaande |
| `FINDINGS.md` | conclusies van de vraag "waarom lijkt alles duurder in 2026" |

## Rekeningen
| IBAN | naam | rol |
|---|---|---|
| NL61SNSB8839326014 | zzp-lopend | zakelijke lopende rekening (hier komt omzet binnen, betaalt kosten) |
| NL35SNSB8839767444 | zzp-btw | btw-potje |
| NL13SNSB8839767452 | zzp-ib-1 | inkomstenbelasting-potje (t/m 2025) |
| NL60SNSB8839767479 | zzp-ib-2 | btw/IB-potje (sinds 2023; in 2026 'Inkbel schatting 2026') |
| NL88SNSB8839767460 | zzp-buffer | eerst IB 2023, later "Zakelijk sparen buffer" |
| NL52SNSB0926827723 | frank | persoonlijk betaalrekening (ontvangt loon van zzp, "Eversoft") |
| NL11SNSB0706257057 | samen | gezamenlijke rekening met Tessa (hypotheek, energie, verzekeringen, kinderopvang, boodschappen) |
| NL68SNSB8811784387 | frank-sparen | spaarrekening Frank |
| NL57SNSB8822509390 | samen-sparen | gezamenlijke spaarrekening (vanaf 2025) |
| NL06SNSB8833710122 / NL02SNSB8824033571 | Tessa (T.M. Visser) | extern, niet geëxporteerd |
| NL38LPLN2028309334 | "F. evers" | behandeld als eigen (beleggen/neobank), niet geëxporteerd |

## Geldstromen (model)
klanten → zzp-lopend → (btw → zzp-btw, IB → zzp-ib-*) → Belastingdienst; rest als "loon" (naam "Eversoft") → frank → "Geld" 25e van de maand → samen. Tessa stort ook ~dezelfde bijdrage in samen. Beleggen: Stichting Meesman Beleggingsfondsen (maandelijks €800–1.000), Bitstamp (crypto).

## Tessa (belangrijk)
Frank maakt ~€800/mnd ("Monies", rond de 23e) naar Tessa over om netto-inkomen gelijk te trekken. Tessa's eigen rekening is niet geëxporteerd. Behandel overboekingen naar/van Tessa NIET als inkomen of uitgave; kijk vanuit Franks rekening (zie FINDINGS 3b). Boekingen vanaf samen-sparen naar "Tessa s rekening" (bv. "Ronnie termijn" = klusaannemer bijkeuken) zijn gedeelde kosten die Tessa voorschiet en die 50/50 gedeeld worden; categorie `gedeeld: klus/baby (via Tessa, 50/50)` (uitgave). Stortingen van Tessa op samen-sparen blijven transfer.

## Conventies / valkuilen
- Bedragen: + = bij, − = af. Kolom `bron` = prive|zakelijk.
- Hypotheek: tot jun 2025 incasso door "ASN BANK", daarna "Stichting Hypotheken Incasso" (zelfde lening 267711190).
- BEA/GEA-omschrijving bevat `MCC:xxxx`; `categorize.py` gebruikt dit als fallback.
- `BCK*`/`CCV*`/`SumUp` zijn betaalproviders, niet per se horeca.
- Heen-en-weer boekingen (bijv. Sajovi) tellen netto nul; Tikkie/betaalverzoeken zijn aparte categorie.
- Gegevens lopen t/m 30-09-2026. Vergelijk altijd dezelfde maanden (jan–sep).
- `business_flow.txt`, `personal_flow.txt`, `combined_flow.txt`, `Modelfile.*`, `gas-electra/` horen niet bij deze analyse (energiefacturen in PDF/eml zijn niet verwerkt).

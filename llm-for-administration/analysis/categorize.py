"""Categoriseert transacties. Gebruik: from categorize import rows; elke rij is een dict met o.a. cat, groep.

groep:
  transfer  = verschuiving tussen eigen rekeningen / sparen / beleggen / Tessa (geen echte uitgave of inkomen)
  uitgave   = echte uitgave naar buiten het huishouden
  inkomen   = echte inkomsten van buiten (toeslagen, teruggaves, etc.)
"""
import re
from load import conn

OWN = {
    'NL11SNSB0706257057': 'samen', 'NL52SNSB0926827723': 'frank', 'NL57SNSB8822509390': 'samen-sparen',
    'NL68SNSB8811784387': 'frank-sparen', 'NL61SNSB8839326014': 'zzp-lopend', 'NL13SNSB8839767452': 'zzp-ib-1',
    'NL35SNSB8839767444': 'zzp-btw', 'NL60SNSB8839767479': 'zzp-ib-2', 'NL88SNSB8839767460': 'zzp-buffer',
}
TESSA = {'NL06SNSB8833710122', 'NL02SNSB8824033571'}
OWN_EXTERN = {'NL38LPLN2028309334'}  # 'F. evers' bij andere partij (vermoedelijk beleggingsrekening)

MCC = {
 '5411':'boodschappen','5499':'boodschappen','5422':'boodschappen','5441':'boodschappen','5451':'boodschappen','5462':'boodschappen','5300':'boodschappen',
 '5812':'horeca','5813':'horeca','5814':'horeca','5811':'horeca',
 '5541':'auto','5542':'auto','7523':'auto','7538':'auto','5533':'auto','5511':'auto','5521':'auto','7542':'auto','7549':'auto',
 '5912':'gezondheid','5122':'gezondheid','8011':'gezondheid','8021':'gezondheid','8099':'gezondheid','8043':'gezondheid','8062':'gezondheid',
 '4111':'ov/reizen','4112':'ov/reizen','4121':'ov/reizen','4131':'ov/reizen','4511':'vakantie','7011':'vakantie','4722':'vakantie','7512':'vakantie',
 '5200':'huis/tuin/klus','5211':'huis/tuin/klus','5251':'huis/tuin/klus','5261':'huis/tuin/klus','5712':'huis/tuin/klus','5719':'huis/tuin/klus','5713':'huis/tuin/klus',
 '5651':'kleding','5691':'kleding','5621':'kleding','5661':'kleding','5611':'kleding','5631':'kleding','5699':'kleding','5641':'kleding',
 '7994':'vrije tijd','7991':'vrije tijd','7997':'vrije tijd','7999':'vrije tijd','7832':'vrije tijd','7922':'vrije tijd','5941':'vrije tijd','5942':'vrije tijd','5945':'vrije tijd','5732':'vrije tijd','5735':'vrije tijd','5815':'vrije tijd','5816':'vrije tijd',
 '5311':'winkelen','5310':'winkelen','5399':'winkelen','5945':'vrije tijd','5964':'winkelen','5965':'winkelen','5999':'winkelen','5732':'winkelen','5734':'winkelen','5045':'winkelen','5651':'kleding',
 '6011':'contant','6010':'contant','6012':'overig',
 '7230':'verzorging','7298':'verzorging','5977':'verzorging',
 '5993':'overig','5921':'boodschappen','5992':'huis/tuin/klus','5995':'winkelen','5047':'gezondheid',
}

# (regex op naam+omschrijving lowercase, categorie) - eerste match wint
RULES = [
 (r'hypotheek|stichting hypotheken|asn bank$', 'wonen: hypotheek/huur'),
 (r'^zents|huur deze maand', 'wonen: hypotheek/huur'),
 (r'easyenergy|eneco|vitens|stedin|liander|delta fiber|ziggo', 'wonen: energie/water/internet'),
 (r'^kpn', 'telefoon'),
 (r'gemeente (renkum|wageningen)|waterschap|belastingsamenwerking|bsgr', 'wonen: gemeentebelasting'),
 (r'zilveren kruis|klaverblad|aon nl|zorgpolis|centraal beheer|nationale-nederlanden|a\.s\.r|univé|unive|vgz|ohra|inshared|reaal|avero|fbto|ditzo|hiscox|schadeverz', 'verzekeringen'),
 (r'kinderopvang|speelboerderij|kinderdagverblijf|bso', 'kinderopvang'),
 (r'duo hoofdrekening|dienst uitvoering onderwijs|^duo', 'studieschuld (DUO)'),
 (r'belastingdienst', 'belasting (privé)'),
 (r'meesman|bitstamp|lightyear|degiro|bux|binck', 'beleggen'),
 (r'int card|international card|icc ', 'creditcard (ICS)'),
 (r'albert heijn|jumbo|lidl|aldi|plus |ah to go|zuivelhoekje|ekoplaza|ekomarkt|kruidvat|etos|gall|bakker|slager|vishandel|boerderij|dirk|spar ', 'boodschappen'),
 (r'thuisbezorgd|uber ?eats|deliveroo|cafe|café|restaurant|bar |pizz|sushi|kater|wijnbar|brasserie|lunch|koffie|coffee|bubbel|gieterij', 'horeca'),
 (r'total|tinq|shell|bp |esso|tango|tamoil|q8|texaco|brandstof|laadpaal|allego|fastned|nuon|xtra car|lehmann|van pars|autoservice|garage|anwb|parkeer|q-park|yellowbrick|parkmobile', 'auto'),
 (r'klm|transavia|airbnb|booking|easyjet|ryanair|vueling|expedia|tui|hotel|camping|ns groep|ns reizigers|tls bv|ov-chip|flixbus|eurostar|sncf|trainline', 'vakantie/reizen/ov'),
 (r'health club|sportcentrum|fitness|basic-fit|sportschool|muziek|columbus|steampowered|valve|nuvei|spotify|netflix|disney|nrc|volkskrant|youtube|google|apple|microsoft|playstation|nintendo|bioscoop|pathe|steam', 'abonnementen/vrije tijd'),
 (r'coolblue|bol\.com|bol b\.v\.|amazon|ikea|hornbach|gamma|praxis|karwei|bouwmarkt|colorstore|vermeulen woning|woninginrichting|kwantum|leen bakker|jysk|action|hema|blokker|wehkamp|zalando|decathlon|canyon|breet bikes|brenet|fiets|kleding|sezane|mantel|tuincentrum|ommuurde tuin', 'winkelen/huis/spullen'),
 (r'geldmaat|opname|cash', 'contant'),
 (r'promovendum', 'promovendum (?)'),
 (r'tikkie|betaalverzoek|betaalverzoek', 'tikkie/betaalverzoeken'),
 (r'apotheek|huisarts|tandarts|tandheelkunde|fysio|ziekenhuis|zorg|dokter|opticien|specsavers|pearle', 'gezondheid'),
 (r'multisafepay|transip|azerty|hosting|domein|online payments foundation|boekhoud|kvk|google workspace|mollie', 'zakelijk-achtig (privé betaald)'),
]

def classify(r):
    rek, tegen, naam, om, b, typ = r['rek'], r['tegen'], r['naam'], r['omschr'], r['bedrag'], r['type']
    low = (naam + ' ' + om).lower()
    if tegen in OWN or tegen in OWN_EXTERN:
        return 'transfer', 'eigen rekeningen'
    if rek == 'NL57SNSB8822509390' and tegen in TESSA and b < 0:
        return 'uitgave', 'gedeeld: klus/baby (via Tessa, 50/50)'
    if tegen in TESSA or re.search(r'visser t m|t\.m\. visser|tessa', low):
        if re.search(r'kinderopvangtoeslag', low):
            return 'inkomen', 'kinderopvangtoeslag'
        return 'transfer', 'Tessa'
    if re.search(r'^(f\.? ?evers|evers f|samen|betalen|frank|zzp buffer|zzp buffer|regenachtig|spaarrekening|samen sparen|gezamelijke|gezamenlijke|sns zzp|eversoft)', naam.lower()) or re.search(r'^f\.? ?evers', naam.lower()):
        return 'transfer', 'eigen rekeningen'
    if re.search(r'rente over|creditrente|debetrente|kostenoverzicht|provisie|bijschrijving rente', low) or typ in ('RTI','AFB'):
        return ('uitgave' if b<0 else 'inkomen'), 'bankkosten/rente'
    if b > 0:
        if re.search(r'kadaster|headfirst|bergler|spotinfo|rewilding|sofysio|sajovi|inbo', low):
            return 'inkomen', 'zakelijke omzet'
        if re.search(r'politie', low): return 'inkomen', 'salaris (politie, t/m 2022)'
        if re.search(r'belastingdienst', low): return 'inkomen', 'belastingteruggave/toeslag'
        if re.search(r'meesman|bitstamp', low): return 'transfer', 'beleggen (uitkering)'
        if re.search(r'toeslag', low): return 'inkomen', 'toeslagen'
        return 'inkomen', 'overige inkomsten'
    # uitgaven
    if typ in ('BEA','GEA'):
        m = re.search(r'MCC:(\d{4})', om)
        for rx, cat in RULES:
            if re.search(rx, low): break
        else:
            cat = None
        if cat and cat not in ('tikkie/betaalverzoeken',):
            return 'uitgave', cat
        if m and m.group(1) in MCC:
            return 'uitgave', MCC[m.group(1)]
        return 'uitgave', 'pinbetaling overig'
    for rx, cat in RULES:
        if re.search(rx, low):
            return ('transfer' if cat == 'beleggen' else 'uitgave'), cat
    return 'uitgave', 'overig'

def rows(only_prive=True):
    c = conn()
    cur = c.execute("select bron,rek,tegen,naam,datum,maand,jaar,bedrag,saldo_voor,type,volgnr,omschr from tx")
    cols = [d[0] for d in cur.description]
    out = []
    for t in cur.fetchall():
        r = dict(zip(cols, t))
        if only_prive and r['bron'] != 'prive':
            continue
        if only_prive and r['rek'] in ('NL57SNSB8822509390','NL68SNSB8811784387'):
            pass
        r['groep'], r['cat'] = classify(r)
        out.append(r)
    return out

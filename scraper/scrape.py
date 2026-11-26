#!/usr/bin/env python3
"""Legge i calendari delle prove libere moto e scrive data.json.

Usa solo la libreria standard di Python: nessuna installazione necessaria.
Se un sito non risponde o cambia struttura, le date gia' salvate di quel sito
restano nel calendario e la fonte viene segnalata come "da controllare".
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import unicodedata
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data.json")
UA = "Mozilla/5.0 (compatible; CalendarioProveLibere/1.0)"

MESI_IT = {"gen": 1, "feb": 2, "mar": 3, "apr": 4, "mag": 5, "giu": 6,
           "lug": 7, "ago": 8, "set": 9, "ott": 10, "nov": 11, "dic": 12}
MESI_EN = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
           "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}

# id, nome mostrato, paese, parole che lo identificano nel testo
CIRCUITS = [
    ("mugello", "Mugello", "IT", ["mugello"]),
    ("misano", "Misano", "IT", ["misano"]),
    ("cremona", "Cremona", "IT", ["cremona"]),
    ("imola", "Imola", "IT", ["imola"]),
    ("monza", "Monza", "IT", ["monza"]),
    ("vallelunga", "Vallelunga", "IT", ["vallelunga"]),
    ("tazio-nuvolari", "Tazio Nuvolari", "IT", ["nuvolari", "cervesina"]),
    ("magione", "Magione", "IT", ["magione"]),
    ("jerez", "Jerez", "ES", ["jerez"]),
    ("valencia", "Valencia", "ES", ["valencia", "cheste", "ricardo tormo"]),
    ("siviglia", "Siviglia", "ES", ["siviglia", "sevilla"]),
    ("almeria", "Almeria", "ES", ["almeria"]),
    ("aragon", "Aragon", "ES", ["aragon", "motorland"]),
    ("barcellona", "Barcellona", "ES", ["barcellona", "barcelona", "catalunya"]),
    ("cartagena", "Cartagena", "ES", ["cartagena"]),
    ("portimao", "Portimão", "PT", ["portimao", "algarve"]),
    ("brno", "Brno", "CZ", ["brno", "brunn", "bruenn"]),
    ("rijeka", "Rijeka", "HR", ["rijeka"]),
    ("monteblanco", "Monteblanco", "ES", ["monteblanco"]),
    ("anneau-du-rhin", "Anneau du Rhin", "FR", ["anneau du rhin", "anneau-du-rhin"]),
    ("hockenheim", "Hockenheim", "DE", ["hockenheim"]),
    ("assen", "Assen", "NL", ["assen"]),
    ("calafat", "Calafat", "ES", ["calafat"]),
    ("most", "Most", "CZ", ["most"]),
    ("ledenon", "Ledenon", "FR", ["ledenon"]),
]
ALWAYS_SHOW = ["mugello", "misano", "cremona", "vallelunga"]

ORGS = {
    "rf": "Racing Factory",
    "gully": "Gully Racing",
    "promo": "Promo Racing",
    "rosso": "Rosso Corsa",
    "cremona": "Cremona Circuit",
    "rehm": "Rehm Race Days",
    "speer": "Speer Racing",
    "vallelunga": "Autodromo di Vallelunga",
    "pistard": "Pistard Racing",
    "altro": "Altro organizzatore",
}


# ---------------------------------------------------------------- utilita'

def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def month_num(name):
    k = fold(name)[:3]
    return MESI_IT.get(k) or MESI_EN.get(k)


def alias_re(a):
    # parole corte ("most") solo come parola intera; le altre anche come inizio di parola
    return r"\b" + re.escape(a) + (r"\b" if len(a) <= 5 else "")


def find_circuit(text):
    """Il circuito nominato per primo nel testo, o None."""
    t = fold(text)
    best = None
    for cid, name, country, aliases in CIRCUITS:
        for a in aliases:
            m = re.search(alias_re(a), t)
            if m and (best is None or m.start() < best[0]):
                best = (m.start(), (cid, name, country))
    return best[1] if best else None


def canon(text):
    t = fold(text)
    for cid, name, country, aliases in CIRCUITS:
        if any(re.search(alias_re(a), t) for a in aliases):
            return cid, name, country
    name = clean(re.sub(r"[-|·,]+", " ", text))[:40].title() or "Altro"
    slug = re.sub(r"[^a-z0-9]+", "-", fold(name)).strip("-") or "altro"
    return slug, name, ""


def safe_date(y, m, d):
    try:
        return dt.date(y, m, d)
    except (ValueError, TypeError):
        return None


def infer_year(month, day, today):
    for y in (today.year, today.year + 1):
        d = safe_date(y, month, day)
        if d and d >= today - dt.timedelta(days=30):
            return y
    return today.year + 1


def make_range(d1, m1, d2, m2, today, year=None):
    y = year or infer_year(m1, d1, today)
    a = safe_date(y, m1, d1)
    b = safe_date(y, m2, d2)
    if not a or not b:
        return None
    if b < a:
        b = safe_date(y + 1, m2, d2)
    return a, b


def money(s):
    """'759,00' -> '759'; '1.100' -> '1.100'."""
    s = s.strip()
    if "," in s:
        s = s.split(",")[0]
    return s


def event(org, a, b, circuit, price="", note="", url="", uid=""):
    cid, cname, country = circuit
    e = {
        "id": "%s-%s-%s%s" % (org, cid, a.isoformat(), "-" + uid if uid else ""),
        "start": a.isoformat(),
        "end": b.isoformat(),
        "circuit": cid,
        "circuit_name": cname,
        "country": country,
        "org": org,
        "price": price,
        "note": note,
        "url": url,
    }
    if uid:
        e["uid"] = uid
    return e


class Page(HTMLParser):
    """Trasforma l'HTML in testo con marcatori per link e immagini."""

    BLOCK = {"p", "div", "li", "tr", "br", "h1", "h2", "h3", "h4", "h5", "h6",
             "section", "article", "table", "td", "th", "ul", "ol", "header",
             "footer", "main", "nav"}
    SKIP = {"script", "style", "noscript"}

    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.parts = []
        self.skip = 0
        self.anchors = []
        self._a = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self.skip += 1
            return
        if tag in self.BLOCK:
            self.parts.append("\n")
        if tag == "a" and a.get("href"):
            href = urljoin(self.base, a["href"])
            self._a = {"href": href, "text": []}
            self.parts.append("⟦" + href + "⟧")
        if tag == "img" and a.get("src"):
            self.parts.append("⟦IMG " + urljoin(self.base, a["src"]) + "⟧")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if tag == "a" and self._a is not None:
            self._a["text"] = clean(" ".join(self._a["text"]))
            self.anchors.append(self._a)
            self._a = None
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip:
            return
        self.parts.append(data)
        if self._a is not None:
            self._a["text"].append(data)

    def text(self):
        t = "".join(self.parts)
        t = re.sub(r"[ \t\r\f\v]+", " ", t)
        return re.sub(r"\n\s*\n+", "\n", t)


class Cells(HTMLParser):
    """Raccoglie il testo di ogni cella <td> di una tabella."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cells = []
        self.cur = None
        self.all = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag == "td":
            self.cur = []

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        elif tag == "td" and self.cur is not None:
            self.cells.append(self.cur)
            self.cur = None

    def handle_data(self, data):
        if self.skip:
            return
        self.all.append(data)
        if self.cur is not None and data.strip():
            self.cur.append(clean(data))


def page(html, base):
    p = Page(base)
    p.feed(html)
    return p


# ---------------------------------------------------------------- parser

def parse_rf(html, today):
    url = "https://www.racingfactory.it/"
    text = page(html, url).text()
    out, seen, prev = [], set(), 0
    for m in re.finditer(r"⟦([^⟧]*/prodotto/prove-libere[^⟧]*)⟧", text):
        href = m.group(1)
        seg = text[prev:m.start()]
        prev = m.end()
        if href in seen:
            continue
        seen.add(href)
        slug = href.rstrip("/").rsplit("/", 1)[-1]
        s = re.search(r"(\d{1,2})(?:-(\d{1,2}))?-([a-z]+)-(20\d\d)", slug)
        if not s:
            continue
        mo = month_num(s.group(3))
        if not mo:
            continue
        r = make_range(int(s.group(1)), mo, int(s.group(2) or s.group(1)), mo, today, int(s.group(4)))
        if not r:
            continue
        prices = re.findall(r"(\d[\d\.]*(?:,\d+)?)\s*€", seg)
        price = "%s € IVA incl." % money(prices[-1]) if prices else ""
        out.append(event("rf", r[0], r[1], canon(slug), price, "", href))
    return out


def parse_gully(html, today):
    url = "https://www.gullyracing.it/calendario"
    text = page(html, url).text()
    ym = re.search(r"PROVE CRONOMETRATE IN PISTA\s+(20\d\d)", text)
    year = int(ym.group(1)) if ym else None
    blocks = re.split(r"(?=\bdal\s+\d{1,2}\s+[A-Za-zì]+\s+al\s+\d{1,2}\s+[A-Za-zì]+)", text)
    out = []
    for b in blocks:
        m = re.match(r"dal\s+(\d{1,2})\s+([A-Za-zì]+)\s+al\s+(\d{1,2})\s+([A-Za-zì]+)(.*)", b, re.S)
        if not m:
            continue
        m1, m2 = month_num(m.group(2)), month_num(m.group(4))
        if not m1 or not m2:
            continue
        r = make_range(int(m.group(1)), m1, int(m.group(3)), m2, today, year)
        if not r:
            continue
        rest = m.group(5)
        head = re.split(r"PREZZO", rest)[0]
        img = re.search(r"⟦IMG [^⟧]*/piste/([a-z0-9_-]+)\.", head + rest)
        circ = canon(img.group(1) if img else clean(re.sub(r"⟦[^⟧]*⟧", " ", head)))
        prices = [float(p.replace(".", "").replace(",", ".")) for p in re.findall(r"(\d[\d\.]*,\d{2})\s*€", rest)]
        link = re.search(r"⟦([^⟧]*/prodotto\?id=\d+)⟧", rest)
        price = ""
        if prices:
            lo, hi = min(prices), max(prices)
            price = "%d € promo, %d € intero" % (lo, hi) if hi > lo else "%d €" % lo
        out.append(event("gully", r[0], r[1], circ, price, "", link.group(1) if link else url))
    return out


def parse_promo(html, today):
    url = "https://www.promoracing.it/it/calendario/moto"
    p = page(html, url)
    groups = {}
    for a in p.anchors:
        m = re.search(r"calendario/moto\.(\d+)/", a["href"])
        if not m:
            continue
        t = re.sub(r"^(Disponibile|Esaurito|Ultimi posti|Non disponibile)\s*", "", a["text"], flags=re.I)
        d = re.match(r"(\d{1,2})\s+([A-Za-zì]{3})\w*\s+(.*)", t)
        if not d or not month_num(d.group(2)):
            continue
        g = groups.setdefault(m.group(1), {"days": [], "text": d.group(3), "href": a["href"].split("#")[0]})
        g["days"].append((month_num(d.group(2)), int(d.group(1))))
    out = []
    for g in groups.values():
        first_m, first_d = g["days"][0]
        year = infer_year(first_m, first_d, today)
        dates = [safe_date(year if (mo, dd) >= (first_m, first_d) else year + 1, mo, dd) for mo, dd in g["days"]]
        dates = [d for d in dates if d]
        if not dates:
            continue
        out.append(event("promo", min(dates), max(dates), canon(g["text"]), "", "", g["href"]))
    return out


def parse_rosso(html, today):
    url = "https://www.rossocorsaonline.com/prove"
    p = page(html, url)
    out, seen = [], set()
    tail = r"\|\s*(.+?)\s+(?:a partire da|da)\s+([\d\.,]+)\s*€"
    for a in p.anchors:
        if not re.search(r"/prove/detail/\d+", a["href"]) or a["href"] in seen:
            continue
        seen.add(a["href"])
        t = a["text"]
        if re.search(r"buon[io] regalo", t, re.I):
            continue
        m = re.match(r"(\d{1,2})\s+([A-Za-zì]+)\s*-\s*(\d{1,2})\s+([A-Za-zì]+)\s*" + tail, t)
        if m:
            d1, m1, d2, m2, cname, price = int(m.group(1)), month_num(m.group(2)), int(m.group(3)), month_num(m.group(4)), m.group(5), m.group(6)
        else:
            m = re.match(r"(\d{1,2})(?:\s*-\s*(\d{1,2}))?\s+([A-Za-zì]+)\s*" + tail, t)
            if not m:
                continue
            d1, m1 = int(m.group(1)), month_num(m.group(3))
            d2, m2 = int(m.group(2) or m.group(1)), m1
            cname, price = m.group(4), m.group(5)
        if not m1 or not m2:
            continue
        r = make_range(d1, m1, d2, m2, today)
        if r:
            out.append(event("rosso", r[0], r[1], canon(cname), "da %s €" % money(price), "", a["href"]))
    return out


def parse_cremona(html, today):
    url = "https://cremonacircuit.it/en/booking/"
    c = Cells()
    c.feed(html)
    alltext = clean(" ".join(c.all))
    m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December|"
                  r"gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(20\d\d)",
                  alltext, re.I)
    if not m:
        raise ValueError("mese del calendario non trovato")
    mo, year = month_num(m.group(1)), int(m.group(2))
    out = []
    for cell in c.cells:
        if not cell or not cell[0].isdigit():
            continue
        if not any(re.search(r"PROVE LIBERE (IN )?MOTO", x, re.I) for x in cell[1:]):
            continue
        d = safe_date(year, mo, int(cell[0]))
        if d:
            out.append(event("cremona", d, d, canon("cremona"), "", "Prove libere moto del circuito", url))
    return out


def parse_mugello(html, today):
    base = "https://mugellocircuit.com/en/events/bike-free-practices"
    p = page(html, base)
    text = p.text()
    texts = {a["href"]: a["text"] for a in p.anchors}
    out, prev = [], 0
    for m in re.finditer(r"⟦([^⟧]*/bike-free-practices/details/[^⟧]*)⟧", text):
        href = m.group(1)
        seg = text[prev:m.start()]
        prev = m.end()
        dates = re.findall(r"(\d{2})\.(\d{2})\.(\d{4})(?:\s*-\s*(\d{2})\.(\d{2})\.(\d{4}))?", seg)
        if not dates:
            continue
        d1, m1, y1, d2, m2, y2 = dates[-1]
        a = safe_date(int(y1), int(m1), int(d1))
        b = safe_date(int(y2 or y1), int(m2 or m1), int(d2 or d1))
        if not a or not b:
            continue
        label = texts.get(href, "")
        f = fold(label)
        org = "altro"
        for key, oid in (("promo", "promo"), ("gully", "gully"), ("rosso", "rosso"), ("racing factory", "rf")):
            if key in f:
                org = oid
        note = label if org == "altro" else ""
        out.append(event(org, a, b, canon("mugello"), "", note, href))
    return out


DATE_RE = re.compile(
    r"(\d{1,2})\.(?:(\d{1,2})\.)?(?:(20\d\d))?\s*[–-]\s*(\d{1,2})\.(\d{1,2})\.(20\d\d)"
    r"|(\d{1,2})\.(\d{1,2})\.(20\d\d)")


def parse_official(org, base, skip_words=(), need_circuit=True):
    """Sito ufficiale di Rehm o Speer: ogni data (GG.MM.AAAA o intervallo) apre un evento.

    Il circuito e' il primo nominato dopo la data e prima della data successiva;
    il prezzo e' il primo importo nello stesso tratto. Corsi di sicurezza, coaching
    e simili si scartano con skip_words.
    """
    def parse(html, today):
        text = re.sub(r"⟦[^⟧]*⟧", " ", page(html, base).text())
        hits = list(DATE_RE.finditer(text))
        out = []
        for i, m in enumerate(hits):
            seg = text[m.end(): hits[i + 1].start() if i + 1 < len(hits) else len(text)][:260]
            if m.group(7):
                a = safe_date(int(m.group(9)), int(m.group(8)), int(m.group(7)))
                b = a
            else:
                y2, m2, d1, d2 = int(m.group(6)), int(m.group(5)), int(m.group(1)), int(m.group(4))
                m1 = int(m.group(2) or m2)
                a = safe_date(int(m.group(3) or y2), m1, d1)
                b = safe_date(y2, m2, d2)
            if not a or not b or b < a or (b - a).days > 10:
                continue
            f = fold(seg)
            if any(w in f for w in skip_words):
                continue
            circ = find_circuit(seg)
            if not circ:
                if need_circuit:
                    continue
                circ = canon("")
            pr = re.search(r"€\s*(\d[\d\.]*,\d{2})|(\d[\d\.]*,\d{2})\s*€", seg)
            price = "da %s €" % money(pr.group(1) or pr.group(2)) if pr else ""
            out.append(event(org, a, b, circ, price, "", base))
        return out
    return parse


SPEER_DATE = re.compile(
    r"(\d{1,2})\.(?: ([A-Z][a-z]{2,4}))?(?: - (\d{1,2})\.(?: ([A-Z][a-z]{2,4}))?)? (20\d\d)")
SPEER_SKIP = ("instruktor", "instructor", "coaching", "schraglagen", "slt ")


def parse_speer(html, today):
    """speer-racing.de: ogni scheda inizia con la data ("03. - 05. Jan 2027"), poi titolo,
    categoria, "speerkompass", circuito, prezzo ("€ 741.60"). Ogni scheda compare due volte
    (la seconda con "On-site services", senza prezzo): si scarta."""
    base = "https://www.speer-racing.de/en/"
    text = clean(re.sub(r"⟦[^⟧]*⟧", " ", page(html, base).text()))
    hits = list(SPEER_DATE.finditer(text))
    out = []
    for i, m in enumerate(hits):
        seg = text[m.end(): hits[i + 1].start() if i + 1 < len(hits) else len(text)][:400]
        if re.match(r".{0,120}?speerkompass On-site", seg):
            continue
        d1, mon1, d2, mon2, y = int(m.group(1)), m.group(2), m.group(3), m.group(4), int(m.group(5))
        m2 = month_num(mon2 or mon1 or "")
        m1 = month_num(mon1) if mon1 else m2
        if not m1 or not m2:
            continue
        a = safe_date(y, m1, d1)
        b = safe_date(y, m2, int(d2)) if d2 else a
        if not a or not b or b < a or (b - a).days > 10:
            continue
        head = fold(seg[:140])
        if any(w in head for w in SPEER_SKIP):
            continue
        circ = find_circuit(seg[:140])
        if not circ:
            continue
        pr = re.search(r"€\s*(\d[\d\.]*)", seg)
        price = ""
        if pr and re.fullmatch(r"\d+(?:\.\d{3})*\.\d{2}", pr.group(1)):
            price = "da %d €" % int(pr.group(1).rsplit(".", 1)[0].replace(".", ""))
        out.append(event("speer", a, b, circ, price, "", base))
    return out


def merge_overlaps(events):
    """Uno stesso organizzatore sullo stesso circuito con date che si sovrappongono
    (turno intero, formula compatta, corsi) diventa un'unica voce con l'intervallo piu' largo."""
    groups = {}
    for e in events:
        groups.setdefault((e["org"], e["circuit"]), []).append(e)
    out = []
    for lst in groups.values():
        lst.sort(key=lambda e: e["start"])
        cur = [lst[0]]
        for e in lst[1:]:
            if e["start"] <= max(x["end"] for x in cur):
                cur.append(e)
            else:
                out.append(_merge(cur))
                cur = [e]
        out.append(_merge(cur))
    return out


def _merge(cur):
    if len(cur) == 1:
        return cur[0]
    pr = lambda e: PRIORITY.index(e.get("src")) if e.get("src") in PRIORITY else 99
    base = dict(sorted(cur, key=pr)[0])
    base["start"] = min(x["start"] for x in cur)
    base["end"] = max(x["end"] for x in cur)
    base["id"] = "%s-%s-%s" % (base["org"], base["circuit"], base["start"])
    base.pop("uid", None)
    prices = []
    for x in cur:
        n = re.search(r"(\d[\d\.]*)", x["price"] or "")
        if n:
            prices.append(int(n.group(1).replace(".", "")))
    base["price"] = "da %d €" % min(prices) if prices else ""
    return base


def parse_racing4fun(org, base):
    """Pagina di un organizzatore sul portale Racing4Fun: una scheda per evento.

    Si tengono le categorie "Renntrainings" (prove in pista) e quelle senza categoria;
    si scartano corsi di sicurezza, pitbike e simili.
    """
    def parse(html, today):
        text = page(html, base).text()
        out, seen, prev = [], set(), 0
        for m in re.finditer(r"⟦([^⟧]*/event/(\d+)/?)⟧", text):
            href, eid = m.group(1), m.group(2)
            seg = text[prev:m.start()]
            prev = m.end()
            if eid in seen:
                continue
            seen.add(eid)
            d = re.search(r"(\d{1,2})\.(\d{1,2})\.\s*[–-]\s*(\d{1,2})\.(\d{1,2})\.(\d{2,4})", seg)
            if not d:
                continue
            yy = int(d.group(5))
            year = yy + 2000 if yy < 100 else yy
            r = make_range(int(d.group(1)), int(d.group(2)), int(d.group(3)), int(d.group(4)), today, year)
            if not r:
                continue
            cat = re.search(r"Kategorie:?\s*([^\n⟦]*)", seg)
            cat = fold(clean(cat.group(1))) if cat else ""
            if cat and "renntraining" not in cat:
                continue
            tr = re.search(r"⟦[^⟧]*/track/([^⟧/]*)/?⟧\s*([^\n⟦]*)", seg)
            circ = canon(clean(tr.group(2)) + " " + tr.group(1)) if tr else canon("")
            title = ""
            for line in seg.split("\n"):
                if re.search(r"\d{2}\.\d{2}\.(20\d\d)?\s*$", line.strip()) and " - " in line:
                    title = clean(re.sub(r"⟦[^⟧]*⟧", " ", line))
            note = re.sub(r"\s*-\s*\d{1,2}\.[\d\.\s-]*$", "", title)
            if re.match(r"^\d+ Tage? Sportfahrertraining", note) or re.match(r"^1 Tag Instruktoren- & Sportfahrertraining", note):
                note = ""
            note = re.sub(r"\s*-\s*" + re.escape(circ[1]) + r"\s*$", "", note) if note and circ[1] else note
            out.append(event(org, r[0], r[1], circ, "", note, href, uid=eid))
        return out
    return parse


def parse_vallelunga(html, today):
    """Calendario prove libere moto del sito dell'autodromo: un link per giorno con data-date."""
    base = "https://motorsport.vallelunga.it/pl-moto-2/"
    days = []
    for m in re.finditer(r'<a\b[^>]*\bdata-date="(\d{4})-(\d{2})-(\d{2})"[^>]*>([\s\S]*?)</a>', html):
        d = safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if not d:
            continue
        pm = re.search(r'class="partner[^"]*"[^>]*>([^<]+)<', m.group(4))
        mm = re.search(r'class="meta"[^>]*>([^<]+)<', m.group(4))
        days.append((d, clean(pm.group(1)) if pm else "", clean(mm.group(1)) if mm else ""))
    days.sort()
    price = ""
    i = html.find('id="prezzi"')
    if i >= 0:
        nums = [int(x) for x in re.findall(r"(\d{2,3})\s*(?:€|&euro;|&#8364;)", re.sub(r"<[^>]+>", " ", html[i:i + 3000]))]
        nums = [n for n in nums if n >= 100][:2]
        if nums:
            price = "da %d €" % min(nums)
    out, cur = [], []
    for item in days:
        if cur and (item[0] - cur[-1][0]).days > 1:
            out.append(cur)
            cur = []
        cur.append(item)
    if cur:
        out.append(cur)
    res = []
    for grp in out:
        notes = []
        for _, partner, meta in grp:
            if partner and partner not in notes:
                notes.append(partner)
        res.append(event("vallelunga", grp[0][0], grp[-1][0], canon("vallelunga"), price, ", ".join(notes), base))
    return res


def parse_pistard(html, today):
    """Elenco eventi di Pistard Racing: ogni evento ha un link /circuito/titolo/numero/ e una data in italiano."""
    base = "https://www.pistard-racing.it/prove-libere-moto/"
    p = page(html, base)
    text = p.text()
    out, prev = [], 0
    for m in re.finditer(r"⟦(https?://[^⟧]*pistard-racing\.it/[a-z0-9-]+/[a-z0-9-]+/\d+/?)⟧", text):
        href = m.group(1)
        seg = text[prev:m.start()]
        prev = m.end()
        ds = list(re.finditer(r"(\d{1,2})(?:\s*[-–/e]\s*(\d{1,2}))*\s+([A-Za-zÀ-ù]{3,})\.?\s*(20\d\d)?", seg))
        found = None
        for d in reversed(ds):
            mon = month_num(d.group(3))
            if mon:
                found = (d, mon)
                break
        if not found:
            continue
        d, mon = found
        nums = [int(x) for x in re.findall(r"\d{1,2}", re.sub(r"\s+[A-Za-zÀ-ù].*$", "", d.group(0)))]
        y = int(d.group(4)) if d.group(4) else infer_year(mon, nums[0], today)
        a = safe_date(y, mon, nums[0])
        b = safe_date(y, mon, nums[-1])
        if not a or not b:
            continue
        circ = find_circuit(href.split("pistard-racing.it/")[1].split("/")[0].replace("-", " ")) or find_circuit(seg) or canon("vallelunga")
        pm = re.search(r"(\d[\d\.]*(?:,\d+)?)\s*€", seg)
        price = (pm.group(1) + " €") if pm else ""
        out.append(event("pistard", a, b, circ, price, "", href))
    return out


SOURCES = [
    {"id": "rf", "name": "Racing Factory", "urls": ["https://www.racingfactory.it/"], "parse": parse_rf, "zero_ok": False},
    {"id": "gully", "name": "Gully Racing", "urls": ["https://www.gullyracing.it/calendario"], "parse": parse_gully, "zero_ok": False},
    {"id": "promo", "name": "Promo Racing", "urls": ["https://www.promoracing.it/it/calendario/moto"], "parse": parse_promo, "zero_ok": False},
    {"id": "rosso", "name": "Rosso Corsa", "urls": ["https://www.rossocorsaonline.com/prove"], "parse": parse_rosso, "zero_ok": False},
    {"id": "rehm", "name": "Rehm Race Days (sito ufficiale)", "urls": ["https://www.rehmracedays.com/it/rehm-race-calendario/"],
     "parse": parse_official("rehm", "https://www.rehmracedays.com/it/rehm-race-calendario/"), "zero_ok": False},
    {"id": "speer", "name": "Speer Racing (sito ufficiale)", "urls": ["https://www.speer-racing.de/en/"],
     "parse": parse_speer, "zero_ok": False},
    {"id": "rehm4f", "name": "Rehm Race Days (via Racing4Fun)", "urls": ["https://www.racing4fun.de/veranstalter/rehm-race-days/"],
     "parse": parse_racing4fun("rehm", "https://www.racing4fun.de/veranstalter/rehm-race-days/"), "zero_ok": True},
    {"id": "speer4f", "name": "Speer Racing (via Racing4Fun)", "urls": ["https://www.racing4fun.de/veranstalter/speer-racing-gmbh/"],
     "parse": parse_racing4fun("speer", "https://www.racing4fun.de/veranstalter/speer-racing-gmbh/"), "zero_ok": True},
    {"id": "pistard", "name": "Pistard Racing (sito ufficiale)", "urls": ["https://www.pistard-racing.it/prove-libere-moto/"],
     "parse": parse_pistard, "zero_ok": True},
    {"id": "vallelunga", "name": "Autodromo di Vallelunga (sito ufficiale)", "urls": ["https://motorsport.vallelunga.it/pl-moto-2/"],
     "parse": parse_vallelunga, "zero_ok": True},
    {"id": "cremona", "name": "Cremona Circuit (sito ufficiale)", "urls": ["https://cremonacircuit.it/en/booking/"], "parse": parse_cremona, "zero_ok": True},
    {"id": "mugello", "name": "Mugello Circuit (sito ufficiale)",
     "urls": ["https://mugellocircuit.com/en/events/bike-free-practices",
              "https://mugellocircuit.com/en/events/bike-free-practices?start=10",
              "https://mugellocircuit.com/en/events/bike-free-practices?start=20"],
     "parse": parse_mugello, "zero_ok": True},
]
FALLBACK = {"rehm4f": "rehm", "speer4f": "speer"}
# Gli eventi dei siti degli organizzatori hanno la precedenza su quelli del Mugello.
PRIORITY = ["rf", "gully", "promo", "rosso", "rehm", "speer", "rehm4f", "speer4f", "pistard", "vallelunga", "cremona", "mugello"]


# ---------------------------------------------------------------- raccolta

def fetch(url):
    req = Request(url, headers={"User-Agent": UA, "Accept-Language": "it,en;q=0.8"})
    with urlopen(req, timeout=40) as r:
        raw = r.read()
        ctype = r.headers.get_content_charset() or "utf-8"
    return raw.decode(ctype, errors="replace")


def load_previous():
    try:
        with open(DATA, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"events": [], "sources": []}


def collect(today, fetcher=fetch, previous=None):
    previous = previous or {"events": [], "sources": []}
    prev_by_source = {}
    for e in previous.get("events", []):
        prev_by_source.setdefault(e.get("src", e["org"]), []).append(e)

    events, statuses = [], []
    for s in SOURCES:
        found, error = [], None
        try:
            for i, u in enumerate(s["urls"]):
                try:
                    html = fetcher(u)
                except Exception:
                    if i == 0:
                        raise
                    continue
                found.extend(s["parse"](html, today))
        except Exception as ex:  # rete, struttura cambiata, ecc.
            error = "%s: %s" % (type(ex).__name__, ex)

        found = [e for e in found if e["end"] >= today.isoformat()]
        for e in found:
            e["src"] = s["id"]
        old = [e for e in prev_by_source.get(s["id"], []) if e["end"] >= today.isoformat()]

        if error:
            status, msg, keep = "errore", "Sito non letto (%s). Tengo le date precedenti." % error, old
        elif not found and old and not s["zero_ok"]:
            status, msg, keep = "da_controllare", "Nessuna data letta, forse il sito e' cambiato. Tengo le date precedenti.", old
        elif not found:
            status, msg, keep = "vuoto", "Nessuna prova libera moto pubblicata.", []
        else:
            status, msg, keep = "ok", "", found
        events.extend(keep)
        statuses.append({"id": s["id"], "name": s["name"], "url": s["urls"][0], "status": status,
                         "count": len(keep), "message": msg, "checked": today.isoformat()})

    # niente doppioni: vale la prima fonte in ordine di priorita'
    events.sort(key=lambda e: (PRIORITY.index(e["src"]) if e["src"] in PRIORITY else 99, e["start"]))
    # il portale Racing4Fun serve solo se il sito ufficiale non e' stato letto
    primary_ok = {x["id"] for x in statuses if x["status"] == "ok"}
    events = [e for e in events if not (e["src"] in FALLBACK and FALLBACK[e["src"]] in primary_ok)]
    merged = [e for e in events if e["org"] in ("rehm", "speer")]
    events = [e for e in events if e["org"] not in ("rehm", "speer")] + merge_overlaps(merged)
    events.sort(key=lambda e: (PRIORITY.index(e["src"]) if e["src"] in PRIORITY else 99, e["start"]))
    seen, uniq = set(), []
    for e in events:
        k = e["id"] if e.get("uid") else (e["org"], e["circuit"], e["start"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(e)
    uniq.sort(key=lambda e: (e["start"], e["circuit"]))

    shown = {e["circuit"] for e in uniq} | set(ALWAYS_SHOW)
    names = {c[0]: (c[1], c[2]) for c in CIRCUITS}
    for e in uniq:
        names.setdefault(e["circuit"], (e["circuit_name"], e["country"]))
    order = [c[0] for c in CIRCUITS if c[0] in shown] + sorted(k for k in shown if k not in {c[0] for c in CIRCUITS})
    circuits = [{"id": k, "name": names[k][0], "country": names[k][1]} for k in order]
    return {"checked": today.isoformat(), "orgs": ORGS, "circuits": circuits, "sources": statuses, "events": uniq}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--today", help="data di oggi AAAA-MM-GG (per prove)")
    ap.add_argument("--out", default=DATA)
    args = ap.parse_args(argv)
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    result = collect(today, previous=load_previous())
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for s in result["sources"]:
        print("%-34s %-14s %3d date  %s" % (s["name"], s["status"], s["count"], s["message"]))
    print("Totale: %d date" % len(result["events"]))
    return 1 if all(s["status"] == "errore" for s in result["sources"]) else 0


if __name__ == "__main__":
    sys.exit(main())

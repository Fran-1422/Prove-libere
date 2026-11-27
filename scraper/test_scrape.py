"""Prove del programma su pagine ricostruite dal testo letto dai siti il 20/11/2026.

Sono approssimazioni: i siti veri possono avere un HTML diverso. Servono a
verificare la logica (date, circuiti, prezzi, errori), non la struttura reale.
Esegui:  python3 scraper/test_scrape.py
"""
import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape  # noqa: E402

TODAY = dt.date(2026, 11, 20)

RF = """<html><body><h2>DATE PROVE LIBERE MOTO 2027</h2>
<div class="d"><img src="/logo-sevilla.png"><p>18-20 feb 2027</p><p>Circuito de Sevilla, Spagna</p><p>Posti disponibili</p><p>1.100 € IVA inclusa</p>
<a href="https://www.racingfactory.it/prodotto/prove-libere-siviglia-18-20-febbraio-2027/">Prenota</a></div>
<div class="d"><p>22 mar 2027</p><p>Cremona Circuit</p><p>189 € IVA inclusa</p>
<a href="https://www.racingfactory.it/prodotto/prove-libere-cremona-22-marzo-2027/">Prenota</a></div>
<div class="d"><p>29 mar 2027</p><p>Cremona Circuit</p><p>219 € IVA inclusa</p>
<a href="https://www.racingfactory.it/prodotto/prove-libere-cremona-29-marzo-2027/">Prenota</a></div>
<div class="d"><p>25 apr 2027</p><p>Cremona Circuit</p><p>219 € IVA inclusa</p>
<a href="https://www.racingfactory.it/prodotto/prove-libere-moto-cremona-circuit-25-aprile-2027/">Prenota</a></div>
<div class="d"><p>1 giu 2027</p><p>Misano World Circuit Marco Simoncelli</p><p>249 € IVA inclusa</p>
<a href="https://www.racingfactory.it/prodotto/prove-libere-moto-misano-circuit-1-giugno-2027/">Prenota</a></div>
<div class="d"><p>29 ago 2027</p><p>Misano World Circuit Marco Simoncelli</p><p>249 € IVA inclusa</p>
<a href="https://www.racingfactory.it/prodotto/prove-libere-moto-misano-circuit-29-agosto-2027-domencia/">Prenota</a></div>
<div class="d"><p>20 set 2027</p><p>Misano World Circuit Marco Simoncelli</p><p>249 € IVA inclusa</p>
<a href="https://www.racingfactory.it/prodotto/prove-libere-moto-misano-circuit-20-settembre-2027/">Prenota</a></div>
</body></html>"""

GULLY = """<html><body><h1>PROVE CRONOMETRATE IN PISTA 2027</h1>
<div class="ev"><span>dal</span> <b>26</b> <span>Febbraio</span> <span>al</span> <b>28</b> <span>Febbraio</span>
<span>Valencia</span><img src="/common/assets/img/piste/valencia.png">
<p>PREZZO PROMOZIONALE 3 GIORNI:</p><p>759,00 €</p><a href="/prodotto?id=219">/prodotto?id=219</a>
<p>PREZZO INTERO 3 GIORNI:</p><p>779,00 €</p></div>
<div class="ev"><span>dal</span> <b>05</b> <span>Novembre</span> <span>al</span> <b>07</b> <span>Novembre</span>
<span>Jerez</span><img src="/common/assets/img/piste/jerez.png">
<p>PREZZO SCONTATO 3 GIORNI:</p><p>719,00 €</p><a href="/prodotto?id=221">/prodotto?id=221</a>
<p>PREZZO INTERO 3 GIORNI:</p><p>759,00 €</p></div></body></html>"""

PROMO = """<html><body><h1>Prove libere moto</h1><ul>
<li><a href="/it/calendario/moto.690/prove-moto#08">Disponibile 08 Feb PROVE MOTO Autódromo Internacional do Algarve - Portimao</a></li>
<li><a href="/it/calendario/moto.690/prove-moto#09">Disponibile 09 Feb PROVE MOTO Autódromo Internacional do Algarve - Portimao</a></li>
<li><a href="/it/calendario/moto.690/prove-moto#10">Disponibile 10 Feb PROVE MOTO Autódromo Internacional do Algarve - Portimao</a></li>
<li><a href="/it/calendario/moto.691/prove-moto-#19">Disponibile 19 Mar Prove moto Circuito di Jerez</a></li>
<li><a href="/it/calendario/moto.691/prove-moto-#20">Disponibile 20 Mar Prove moto Circuito di Jerez</a></li>
<li><a href="/it/calendario/moto.691/prove-moto-#21">Disponibile 21 Mar Prove moto Circuito di Jerez</a></li></ul></body></html>"""

ROSSO = """<html><body><h1>Calendario prove</h1>
<a href="/prove/detail/391"><span>05-07 FEBBRAIO</span> | <b>VALENCIA</b> <i>a partire da</i> <b>759,00€</b> PRENOTA!</a>
<a href="/prove/detail/393">05-07 MARZO | JEREZ a partire da 759,00€ PRENOTA!</a>
<a href="/prove/detail/362">03-31 DICEMBRE | BUONI REGALO PRENOTA!</a></body></html>"""

CREMONA_VUOTO = """<html><body><table><tr><td>November 2026</td></tr>
<tr><td>20<br>PROVE LIBERE KART<br>PROVE LIBERE KART</td><td>21<br>CLUB LOTUS ITALIA<br>PROVE LIBERE KART</td></tr></table></body></html>"""

CREMONA_MOTO = """<html><body><table><tr><td>December 2026</td></tr>
<tr><td>3<br>PROVE LIBERE KART</td><td>5<br>PROVE LIBERE MOTO<br>PROVE LIBERE KART</td></tr></table></body></html>"""

MUGELLO = """<html><body><h4>12.12.2026 - 13.12.2026</h4><h2><a href="/en/events/bike-free-practices/details/2026-12-12/1900-promo-racing-9">Promo Racing</a></h2>
<h4>20.12.2026</h4><h2><a href="/en/events/bike-free-practices/details/2026-12-20/1901-pistenclub">Pistenclub</a></h2></body></html>"""


def card(org, title, date, place, slug, cat, eid):
    return ('<div class="event"><img src="/logo.png"><a href="/veranstalter/%s/">%s</a>'
            '<h3>%s</h3><span>%s</span><a href="/track/%s/">%s</a><span>%s</span>'
            '<img src="/i1.png"><img src="/i2.png">'
            '<p>Veranstalter: <a href="/veranstalter/%s/">%s</a></p><p>Kategorie: <span>%s</span></p>'
            '<a href="https://www.racing4fun.de/event/%s/">Details</a></div>') % (org, org, title, date, slug, place, cat, org, org, cat, eid)


SPEER_ROWS = [
    ("3 Tage Sportfahrertraining - Valencia - 03.01. - 05.01.2027", "03.01. – 05.01.27 (So - Di)", "Valencia", "valencia", "Renntrainings", "94817"),
    ("2 Tage Sportfahrertraining - Anneau du Rhin - 26.-27.03.2027", "26.03. – 27.03.27 (Fr - Sa)", "Anneau du Rhin", "anneau-du-rhin", "Renntrainings", "92339"),
    ("Instruktorentraining light - Anneau du Rhin - 27.03.2027", "27.03. – 27.03.27 (Sa - Sa)", "Anneau du Rhin", "anneau-du-rhin", "Sicherheitstrainings", "92341"),
    ("Anneau du Rhin goes Classic - 27.03.2027", "27.03. – 27.03.27 (Sa - Sa)", "Anneau du Rhin", "anneau-du-rhin", "Renntrainings", "92343"),
    ("1 Tag Instruktoren- & Sportfahrertraining - Hockenheimring GP - 29.03.2027", "29.03. – 29.03.27 (Mo - Mo)", "Hockenheimring GP", "hockenheimring-gp", "Renntrainings", "94531"),
    ("2 Tage Sportfahrertraining - Anneau du Rhin - 30.04. - 01.05.2027", "30.04. – 01.05.27 (Fr - Sa)", "Anneau du Rhin", "anneau-du-rhin", "Renntrainings", "92347"),
    ("1 Tag Instruktorentraining - Anneau du Rhin - 30.04.2027", "30.04. – 30.04.27 (Fr - Fr)", "Anneau du Rhin", "anneau-du-rhin", "Sicherheitstrainings", "92353"),
    ("Instruktorentraining light - Anneau du Rhin - 01.05.2027", "01.05. – 01.05.27 (Sa - Sa)", "Anneau du Rhin", "anneau-du-rhin", "Sicherheitstrainings", "92351"),
    ("2 Tage Sportfahrertraining - Assen - 03.07. - 04.07.2027", "03.07. – 04.07.27 (Sa - So)", "Assen", "assen", "Renntrainings", "94514"),
    ("1 Tag Instruktorentraining - Assen - 03.07.2027", "03.07. – 03.07.27 (Sa - Sa)", "Assen", "assen", "Sicherheitstrainings", "94517"),
    ("3 Tage Sportfahrertraining - Anneau du Rhin - 22.07. - 24.07.2027", "22.07. – 24.07.27 (Do - Sa)", "Anneau du Rhin", "anneau-du-rhin", "Renntrainings", "92355"),
    ("2 Tage RookieCamp - Anneau du Rhin - 22.07. - 23.07.2027", "22.07. – 23.07.27 (Do - Fr)", "Anneau du Rhin", "anneau-du-rhin", "Renntrainings", "92357"),
    ("2 Tage GirlsCamp - Anneau du Rhin - 22.07. - 23.07.2027", "22.07. – 23.07.27 (Do - Fr)", "Anneau du Rhin", "anneau-du-rhin", "Renntrainings", "92359"),
    ("Anneau du Rhin goes Classic - 24.07.2027", "24.07. – 24.07.27 (Sa - Sa)", "Anneau du Rhin", "anneau-du-rhin", "Renntrainings", "92363"),
    ("3 Tage Sportfahrertraining - Brünn - 30.07. - 01.08.2027", "30.07. – 01.08.27 (Fr - So)", "Brünn", "bruenn", "Renntrainings", "94524"),
]
REHM_ROWS = [
    ("Barcelona", "26.11. – 27.11.26 (Do - Fr)", "Barcelona", "barcelona", "Renntrainings", "75310"),
    ("Cartagena III", "22.12. – 25.12.26 (Di - Fr)", "Cartagena", "cartagena", "Renntrainings", "75311"),
    ("Cartagena IV", "27.12. – 31.12.26 (So - Do)", "Cartagena", "cartagena", "Renntrainings", "75312"),
    ("Valencia II", "27.12. – 31.12.26 (So - Do)", "Valencia", "valencia", "Renntrainings", "75313"),
    ("Cartagena I", "02.01. – 05.01.27 (Sa - Di)", "Cartagena", "cartagena", "Renntrainings", "75314"),
    ("Monteblanco", "18.01. – 20.01.27 (Mo - Mi)", "Monteblanco", "monteblanco", "Renntrainings", "89058"),
    ("Jerez I", "22.01. – 24.01.27 (Fr - So)", "Jerez", "jerez", "", "89059"),
    ("Cartagena II", "26.02. – 28.02.27 (Fr - So)", "Cartagena", "cartagena", "Renntrainings", "91944"),
    ("Rijeka I", "26.03. – 28.03.27 (Fr - So)", "Rijeka", "rijeka", "", "89063"),
    ("Portimao I", "03.04. – 05.04.27 (Sa - Mo)", "Portimao", "portimao", "Renntrainings", "92654"),
    ("Aragon I", "22.04. – 24.04.27 (Do - Sa)", "Aragon", "aragon", "Renntrainings", "94754"),
    ("Barcelona", "27.04. – 29.04.27 (Di - Do)", "Barcelona", "barcelona", "Renntrainings", "94755"),
]
SPEER = "<html><body><h1>Speer Racing GmbH</h1>" + "".join(card("speer-racing-gmbh", *r[:1], *r[1:]) for r in SPEER_ROWS) + "</body></html>"
REHM = "<html><body><h1>Rehm Race Days</h1>" + "".join(card("rehm-race-days", *r) for r in REHM_ROWS) + "</body></html>"


REHM_OFF_ROWS = [
    ("04.09.2026 – 06.09.2026", "Tazio Nuvolari 5260", ""), ("11.09.2026 – 13.09.2026", "Rijeka II", ""),
    ("18.09.2026 – 20.09.2026", "Most", ""), ("02.10.2026 – 04.10.2026", "Ledenon", ""),
    ("07.10.2026 – 09.10.2026", "Valencia I", ""), ("04.11.2026 – 06.11.2026", "Aragon II", ""),
    ("18.11.2026 – 20.11.2026", "Jerez II", ""), ("26.11.2026 – 27.11.2026", "Barcelona", "640,00 €"),
    ("22.12.2026 – 25.12.2026", "Cartagena III", "540,00 €"), ("27.12.2026 – 31.12.2026", "Cartagena IV", "760,00 €"),
    ("27.12.2026 – 31.12.2026", "Valencia II", "540,00 € (30-31.12), 790,00 € (27-29.12)"),
    ("02.01.2027 – 05.01.2027", "Cartagena I", "590,00 €"), ("18.01.2027 – 20.01.2027", "Monteblanco", "630,00 €"),
    ("22.01.2027 – 24.01.2027", "Jerez I", "790,00 €"), ("26.02.2027 – 28.02.2027", "Cartagena II", "480,00 €"),
    ("26.03.2027 – 28.03.2027", "Rijeka I", "590,00 €"), ("03.04.2027 – 05.04.2027", "Portimao I", "890,00 €"),
    ("22.04.2027 – 24.04.2027", "Aragon I", "840,00 €"), ("27.04.2027 – 29.04.2027", "Barcelona", "970,00 €"),
]
REHM_OFF = "<html><body>" + "".join(
    '<section><h3>Event</h3><p>%s</p><p>%s</p><p>Briefing, Races, Endurance 2h</p><p>%s</p>'
    '<a href="https://www.rehmracedays.com/wp-content/uploads/2026/09/84_Timetable_Tazio_Nuvolari_04.-06.09.2026.pdf" title="Timetable">Timetable</a>'
    '<a href="https://maps.google.com/?q=Most">Maps</a></section>' % r for r in REHM_OFF_ROWS) + "</body></html>"

SPEER_OFF_ROWS = [
    ("03. - 05. Jan 2027", "Valencia 1 - all inclusive", "Sportfahrertraining", "Valencia - Full Circuit", "1.485.54"),
    ("03. - 05. Jan 2027", "Valencia 1", "Sportfahrertraining", "Valencia - Full Circuit", "741.60"),
    ("04. - 05. Jan 2027", "Valencia 1 - compact", "Sportfahrertraining", "Valencia - Full Circuit", "535.60"),
    ("17. - 20. Mar 2027", "Calafat", "Freies Fahren", "Calafat", "669.49"),
    ("17. - 19. Mar 2027", "Calafat GirlsCamp", "Girls Camp", "Calafat", "617.44"),
    ("20. Mar 2027", "Calafat 20.3.", "Freies Fahren", "Calafat", "174.60"),
    ("26. Mar 2027", "Anneau du Rhin", "Sportfahrertraining", "Anneau du Rhin - 3.0", "264.18"),
    ("27. Mar 2027", "Instructortraining light", "Instruktorentraining light", "Anneau du Rhin - 3.0", "149.99"),
    ("27. Mar 2027", "Anneau du Rhin 1:1 light", "1:1 Coaching", "Anneau du Rhin - 3.0", "350.00"),
    ("29. Mar 2027", "Hockenheim", "Instruktorentraining", "Hockenheim - Grand-Prix-Kurs", "281.30"),
    ("22. May 2027", "SLT 22.5. vormittag", "Schr\u00e4glagentraining", "Hockenheim", "106.70"),
    ("22. May 2027", "Hockenheim", "Sportfahrertraining", "Hockenheim - IDM-Kurs", "271.60"),
    ("02. - 04. Jul 2027", "Mugello 1 - 3 days", "Sportfahrertraining", "Mugello - Full Circuit", "999.10"),
    ("03. - 04. Jul 2027", "Assen", "Sportfahrertraining", "Assen - Full Circuit", "599.46"),
    ("10. - 12. Sept 2027", "Mugello 2 - 3 days", "Sportfahrertraining", "Mugello - Full Circuit", "999.10"),
    ("30. Jul - 01. Aug 2027", "Br\u00fcnn", "Sportfahrertraining", "Br\u00fcnn", "799.99"),
]


def _tile(d, title, cat, circ, price):
    shown = d.replace(" - ", "\n -\n ", 1)
    return ('<div class="imia_eventTile"><p class="date">\n%s\n</p><p class="imia_eventTile__name">\n%s\n</p>'
            '<p class="imia_eventTile__trackday">\n%s\n</p><div>speerkompass</div><p>%s</p><p>105 dB</p>'
            '<p>\u20ac\u00a0</p><p>%s</p><a href="https://api.pgm.speer-racing.com/t.pdf">Schedule</a><p>Available</p>'
            '<a href="/en/booking/event/1/">Info</a><a href="/en/booking/event/1/step/1/">Book now</a></div>'
            '<div class="imia_eventTile"><p>%s</p><p>%s</p><p>%s</p><div>speerkompass</div><p>On-site services</p>'
            '<p>55moto Transport \u20ac 160.00</p><a href="#">Info</a><a href="#">Book now</a></div>') % (shown, title, cat, circ, price, d, title, cat)


SPEER_OFF = "<html><body><h2>Booking</h2><p>No events found</p>" + "".join(_tile(*r) for r in SPEER_OFF_ROWS) + "</body></html>"



def fake(pages):
    def f(url):
        for k, v in pages.items():
            if k in url:
                if isinstance(v, Exception):
                    raise v
                return v
        raise OSError("pagina non prevista: " + url)
    return f


def full(**over):
    pages = {"racingfactory": RF, "gullyracing": GULLY, "promoracing": PROMO, "rossocorsa": ROSSO,
             "racing4fun.de/veranstalter/rehm": REHM, "racing4fun.de/veranstalter/speer": SPEER,
             "rehmracedays": REHM_OFF, "speer-racing.de": SPEER_OFF,
             "cremonacircuit": CREMONA_VUOTO, "mugellocircuit": "<html><body>nessun evento</body></html>"}
    pages.update(over)
    return pages


VALL = """<div id="calendario"><a class="plmoto-day is-disabled" href="#" data-date="2027-02-05"><span class="num">05</span><span class="meta">9 &#8211; 13</span><span class="partner">THE BIKE</span></a>
<a class="plmoto-day" href="x.pdf" data-date="2027-02-06"><span class="meta">4 gruppi</span></a>
<a class="plmoto-day" href="x.pdf" data-date="2027-03-20"><span class="meta">3 gruppi</span><span class="partner">DUCATI APPIA</span></a></div>
<div id="prezzi" class="plmoto-section"><h2>Prezzi</h2><p>Feriale 180 &euro;</p><p>210 €</p></div>"""

PIST = """<html><body><div class="ev"><h3>Sabato 13 Marzo 2027</h3><p>Vallelunga</p><p>190 €</p><a href="https://www.pistard-racing.it/vallelunga/prove-libere-open-pit-4-ore/90/">Prenota</a></div>
<div class="ev"><h3>10-11-12 Maggio 2027</h3><a href="https://www.pistard-racing.it/vallelunga/prove-libere-moto/91/">Prenota</a></div></body></html>"""


class Parsers(unittest.TestCase):
    def test_vallelunga_raggruppa_giorni_consecutivi(self):
        ev = scrape.parse_vallelunga(VALL, TODAY)
        self.assertEqual([(e["start"], e["end"], e["circuit"]) for e in ev], [("2027-02-05", "2027-02-06", "vallelunga"), ("2027-03-20", "2027-03-20", "vallelunga")])
        self.assertEqual(ev[0]["note"], "THE BIKE")
        self.assertEqual(ev[0]["price"], "da 180 €")

    def test_pistard(self):
        ev = scrape.parse_pistard(PIST, TODAY)
        self.assertEqual([(e["start"], e["end"], e["circuit"], e["org"]) for e in ev], [("2027-03-13", "2027-03-13", "vallelunga", "pistard"), ("2027-05-10", "2027-05-12", "vallelunga", "pistard")])
        self.assertEqual(ev[0]["price"], "190 €")

    def test_racing_factory(self):
        ev = scrape.parse_rf(RF, TODAY)
        self.assertEqual(len(ev), 7)
        self.assertEqual((ev[0]["start"], ev[0]["end"], ev[0]["circuit"], ev[0]["price"]), ("2027-02-18", "2027-02-20", "siviglia", "1.100 € IVA incl."))
        self.assertEqual([e["circuit"] for e in ev].count("cremona"), 3)
        self.assertEqual(ev[-2]["start"], "2027-08-29")
        self.assertEqual(ev[3]["price"], "219 € IVA incl.")

    def test_gully(self):
        ev = scrape.parse_gully(GULLY, TODAY)
        self.assertEqual(len(ev), 2)
        self.assertEqual((ev[0]["start"], ev[0]["end"], ev[0]["circuit"]), ("2027-02-26", "2027-02-28", "valencia"))
        self.assertEqual(ev[0]["price"], "759 € promo, 779 € intero")
        self.assertEqual((ev[1]["start"], ev[1]["circuit"]), ("2027-11-05", "jerez"))
        self.assertTrue(ev[1]["url"].endswith("/prodotto?id=221"))

    def test_promo_raggruppa_i_giorni(self):
        ev = scrape.parse_promo(PROMO, TODAY)
        self.assertEqual(len(ev), 2)
        self.assertEqual((ev[0]["start"], ev[0]["end"], ev[0]["circuit"]), ("2027-02-08", "2027-02-10", "portimao"))
        self.assertEqual((ev[1]["start"], ev[1]["end"], ev[1]["circuit"]), ("2027-03-19", "2027-03-21", "jerez"))
        self.assertNotIn("#", ev[0]["url"])

    def test_rosso_salta_i_buoni_regalo(self):
        ev = scrape.parse_rosso(ROSSO, TODAY)
        self.assertEqual(len(ev), 2)
        self.assertEqual((ev[0]["start"], ev[0]["end"], ev[0]["circuit"], ev[0]["price"]), ("2027-02-05", "2027-02-07", "valencia", "da 759 €"))
        self.assertEqual(ev[1]["circuit"], "jerez")

    def test_cremona_ufficiale(self):
        self.assertEqual(scrape.parse_cremona(CREMONA_VUOTO, TODAY), [])
        ev = scrape.parse_cremona(CREMONA_MOTO, TODAY)
        self.assertEqual([e["start"] for e in ev], ["2026-12-05"])

    def test_mugello_ufficiale(self):
        ev = scrape.parse_mugello(MUGELLO, TODAY)
        self.assertEqual(len(ev), 2)
        self.assertEqual((ev[0]["start"], ev[0]["end"], ev[0]["org"]), ("2026-12-12", "2026-12-13", "promo"))
        self.assertEqual((ev[1]["org"], ev[1]["note"]), ("altro", "Pistenclub"))

    def test_rehm(self):
        ev = scrape.parse_racing4fun("rehm", "https://www.racing4fun.de/veranstalter/rehm-race-days/")(REHM, TODAY)
        self.assertEqual(len(ev), 12)
        self.assertEqual((ev[0]["start"], ev[0]["end"], ev[0]["circuit"]), ("2026-11-26", "2026-11-27", "barcellona"))
        self.assertEqual(ev[0]["url"], "https://www.racing4fun.de/event/75310/")
        self.assertEqual([e["circuit"] for e in ev][5:9], ["monteblanco", "jerez", "cartagena", "rijeka"])

    def test_speer_scarta_i_corsi_di_sicurezza(self):
        ev = scrape.parse_racing4fun("speer", "https://www.racing4fun.de/veranstalter/speer-racing-gmbh/")(SPEER, TODAY)
        self.assertEqual(len(ev), 11)
        self.assertEqual((ev[0]["start"], ev[0]["end"], ev[0]["circuit"]), ("2027-01-03", "2027-01-05", "valencia"))
        self.assertNotIn("92341", [e["uid"] for e in ev])
        self.assertEqual(ev[-1]["circuit"], "brno")
        self.assertEqual({e["circuit"] for e in ev}, {"valencia", "anneau-du-rhin", "hockenheim", "assen", "brno"})
        camp = [e for e in ev if e["uid"] in ("92357", "92359")]
        self.assertEqual([e["note"] for e in camp], ["2 Tage RookieCamp", "2 Tage GirlsCamp"])
        self.assertEqual(ev[1]["note"], "")

    def test_rehm_ufficiale(self):
        ev = scrape.parse_official("rehm", "https://www.rehmracedays.com/it/rehm-race-calendario/")(REHM_OFF, TODAY)
        self.assertEqual(len(ev), 19)
        self.assertEqual((ev[0]["start"], ev[0]["end"], ev[0]["circuit"]), ("2026-09-04", "2026-09-06", "tazio-nuvolari"))
        self.assertEqual([e["circuit"] for e in ev][1:4], ["rijeka", "most", "ledenon"])
        self.assertEqual((ev[7]["price"], ev[10]["price"]), ("da 640 €", "da 540 €"))
        self.assertEqual(ev[3]["price"], "")

    def test_speer_ufficiale_scarta_coaching_e_corsi(self):
        ev = scrape.parse_speer(SPEER_OFF, TODAY)
        self.assertEqual(len(ev), 12)
        self.assertEqual((ev[0]["start"], ev[0]["end"], ev[0]["price"]), ("2027-01-03", "2027-01-05", "da 1485 €"))
        self.assertEqual((ev[-1]["circuit"], ev[-1]["start"], ev[-1]["end"]), ("brno", "2027-07-30", "2027-08-01"))
        self.assertIn(("2027-09-10", "2027-09-12"), [(e["start"], e["end"]) for e in ev])
        self.assertNotIn("1:1", " ".join(e["note"] for e in ev))

    def test_anno_dedotto(self):
        self.assertEqual(scrape.infer_year(2, 5, dt.date(2026, 11, 20)), 2027)
        self.assertEqual(scrape.infer_year(11, 25, dt.date(2026, 11, 20)), 2026)


class Raccolta(unittest.TestCase):
    def test_scarta_prodotti_non_prove(self):
        ev = scrape.event("gully", dt.date(2027, 2, 26), dt.date(2027, 3, 13), scrape.canon("assicurazionesanitariaspagna"), "75 €", "", "https://www.gullyracing.it/prodotto?id=211")
        self.assertFalse(scrape.looks_like_trackday(ev))
        ok = scrape.event("gully", dt.date(2027, 2, 26), dt.date(2027, 2, 28), scrape.canon("valencia"), "759 €", "", "https://www.gullyracing.it/prodotto?id=1")
        self.assertTrue(scrape.looks_like_trackday(ok))

    def test_tutto_ok(self):
        r = scrape.collect(TODAY, fake(full()))
        self.assertEqual(len(r["events"]), 34)
        self.assertEqual([e["start"] for e in r["events"]], sorted(e["start"] for e in r["events"]))
        st = {s["id"]: s for s in r["sources"]}
        self.assertEqual(st["rf"]["status"], "ok")
        self.assertEqual(st["mugello"]["status"], "vuoto")
        self.assertIn("mugello", [c["id"] for c in r["circuits"]])

    def test_sito_non_raggiungibile_conserva_le_date(self):
        prima = scrape.collect(TODAY, fake(full()))
        dopo = scrape.collect(TODAY, fake(full(racingfactory=OSError("timeout"))), previous=prima)
        self.assertEqual(len(dopo["events"]), 34)
        self.assertEqual({s["id"]: s for s in dopo["sources"]}["rf"]["status"], "errore")

    def test_struttura_cambiata_conserva_le_date(self):
        prima = scrape.collect(TODAY, fake(full()))
        dopo = scrape.collect(TODAY, fake(full(gullyracing="<html><body>Nuovo sito</body></html>")), previous=prima)
        self.assertEqual(len(dopo["events"]), 34)
        self.assertEqual({s["id"]: s for s in dopo["sources"]}["gully"]["status"], "da_controllare")

    def test_date_passate_scompaiono(self):
        r = scrape.collect(dt.date(2027, 3, 1), fake(full()))
        self.assertTrue(all(e["end"] >= "2027-03-01" for e in r["events"]))
        self.assertLess(len(r["events"]), 34)

    def test_turni_sovrapposti_diventano_uno(self):
        r = scrape.collect(TODAY, fake(full()))
        sp = [e for e in r["events"] if e["org"] == "speer"]
        starts = [(e["circuit"], e["start"], e["end"]) for e in sp]
        self.assertEqual(len(starts), len(set(starts)))
        val = [e for e in sp if e["circuit"] == "valencia"]
        self.assertEqual(len(val), 1)
        self.assertEqual((val[0]["start"], val[0]["end"], val[0]["price"], val[0]["src"]), ("2027-01-03", "2027-01-05", "da 535 €", "speer"))
        cal = [e for e in sp if e["circuit"] == "calafat"]
        self.assertEqual((len(cal), cal[0]["start"], cal[0]["end"]), (1, "2027-03-17", "2027-03-20"))
        anneau = [e for e in sp if e["circuit"] == "anneau-du-rhin" and e["start"].startswith("2027-03")]
        self.assertEqual((len(anneau), anneau[0]["start"], anneau[0]["end"]), (1, "2027-03-26", "2027-03-26"))

    def test_racing4fun_solo_se_il_sito_ufficiale_non_va(self):
        ok = scrape.collect(TODAY, fake(full()))
        self.assertFalse([e for e in ok["events"] if e["src"] in ("rehm4f", "speer4f")])
        rotto = scrape.collect(TODAY, fake(full(**{"speer-racing.de": "<html>nuovo</html>"})))
        self.assertTrue([e for e in rotto["events"] if e["src"] == "speer4f"])

    def test_doppioni_mugello(self):
        pages = full(mugellocircuit=MUGELLO)
        r = scrape.collect(TODAY, fake(pages))
        mug = [e for e in r["events"] if e["circuit"] == "mugello" and e["org"] in ("promo", "altro")]
        self.assertEqual(len(mug), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)

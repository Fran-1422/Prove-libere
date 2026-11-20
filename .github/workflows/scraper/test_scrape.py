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
             "cremonacircuit": CREMONA_VUOTO, "mugellocircuit": "<html><body>nessun evento</body></html>"}
    pages.update(over)
    return pages


class Parsers(unittest.TestCase):
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

    def test_anno_dedotto(self):
        self.assertEqual(scrape.infer_year(2, 5, dt.date(2026, 11, 20)), 2027)
        self.assertEqual(scrape.infer_year(11, 25, dt.date(2026, 11, 20)), 2026)


class Raccolta(unittest.TestCase):
    def test_tutto_ok(self):
        r = scrape.collect(TODAY, fake(full()))
        self.assertEqual(len(r["events"]), 13)
        self.assertEqual([e["start"] for e in r["events"]], sorted(e["start"] for e in r["events"]))
        st = {s["id"]: s for s in r["sources"]}
        self.assertEqual(st["rf"]["status"], "ok")
        self.assertEqual(st["mugello"]["status"], "vuoto")
        self.assertIn("mugello", [c["id"] for c in r["circuits"]])

    def test_sito_non_raggiungibile_conserva_le_date(self):
        prima = scrape.collect(TODAY, fake(full()))
        dopo = scrape.collect(TODAY, fake(full(racingfactory=OSError("timeout"))), previous=prima)
        self.assertEqual(len(dopo["events"]), 13)
        self.assertEqual({s["id"]: s for s in dopo["sources"]}["rf"]["status"], "errore")

    def test_struttura_cambiata_conserva_le_date(self):
        prima = scrape.collect(TODAY, fake(full()))
        dopo = scrape.collect(TODAY, fake(full(gullyracing="<html><body>Nuovo sito</body></html>")), previous=prima)
        self.assertEqual(len(dopo["events"]), 13)
        self.assertEqual({s["id"]: s for s in dopo["sources"]}["gully"]["status"], "da_controllare")

    def test_date_passate_scompaiono(self):
        r = scrape.collect(dt.date(2027, 3, 1), fake(full()))
        self.assertTrue(all(e["end"] >= "2027-03-01" for e in r["events"]))
        self.assertLess(len(r["events"]), 13)

    def test_doppioni_mugello(self):
        pages = full(mugellocircuit=MUGELLO)
        r = scrape.collect(TODAY, fake(pages))
        mug = [e for e in r["events"] if e["circuit"] == "mugello"]
        self.assertEqual(len(mug), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)

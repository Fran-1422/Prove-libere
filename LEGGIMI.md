# TrackDay Finder: come metterlo online

Dieci minuti, una volta sola. Alla fine avrai un indirizzo web che puoi installare come app su iPhone, Android, Mac e Windows. Ogni giorno un programma legge i siti degli organizzatori e aggiorna le date da solo.

## Cosa c'è in questa cartella

- `index.html`, `manifest.webmanifest`, `sw.js`, le icone `.png`: la web app.
- `data.json`: le date mostrate dall'app. Si aggiorna da solo.
- `scraper/scrape.py`: il programma che legge i siti.
- `scraper/test_scrape.py`: le prove del programma.
- `.github/workflows/aggiorna.yml`: dice a GitHub di far partire il programma ogni giorno.

Su Mac la cartella `.github` è nascosta nel Finder: premi Cmd + Maiusc + `.` per vederla.

## 1. Crea l'archivio su GitHub (gratis)

1. Registrati su github.com se non hai un account.
2. Premi **New repository**. Dai un nome, per esempio `prove-libere`. Scegli **Public** (le pagine gratuite di GitHub richiedono un archivio pubblico) e crea.
3. Nella pagina dell'archivio premi **uploading an existing file**.
4. Trascina dentro **tutto il contenuto** di questa cartella, compresa `.github`, e premi **Commit changes**.

Se il caricamento non accetta la cartella `.github`: premi **Add file → Create new file**, scrivi come nome `.github/workflows/aggiorna.yml`, incolla il contenuto del file `aggiorna.yml` e salva.

## 2. Attiva il sito

1. Nell'archivio vai su **Settings → Pages**.
2. Sotto **Build and deployment** scegli **Deploy from a branch**, ramo **main**, cartella **/ (root)**, poi **Save**.
3. Dopo uno o due minuti la pagina mostra l'indirizzo, di solito `https://TUO-NOME.github.io/prove-libere/`.

## 3. Fai partire il primo aggiornamento

1. Vai sulla scheda **Actions**. Se GitHub chiede di abilitare i workflow, confermalo.
2. Scegli **Aggiorna date** a sinistra, poi **Run workflow**.
3. Dopo circa un minuto deve comparire una spunta verde. Se compare una croce rossa, apri l'esecuzione e mandami il testo dell'errore.

Da quel momento il programma parte da solo ogni mattina. Se le date non cambiano non salva nulla.

## 4. Installa l'app

- **iPhone o iPad**: apri l'indirizzo in Safari, tocca Condividi, poi «Aggiungi alla schermata Home».
- **Android**: apri l'indirizzo in Chrome, tocca «Installa l'app» (o il menu ⋮ → «Installa app»).
- **Mac o Windows**: apri l'indirizzo in Chrome o Edge e premi l'icona di installazione nella barra dell'indirizzo. Su Mac con Safari: File → «Aggiungi al Dock».

## Il pulsante Aggiorna

Il pulsante **Aggiorna** nell'app scarica le ultime date salvate. Non legge direttamente i siti: lo fa il programma ogni mattina. Per una lettura subito, vai su GitHub → Actions → Aggiorna date → Run workflow, poi premi Aggiorna nell'app.

## Diario giornate e account privato

La pagina `diario.html` (scheda «Diario giornate») tiene il consuntivo: giornate acquistate e svolte, tempi per turno, giri, gomme (mescole e giornate fatte) e ricambi come pastiglie, catena, olio (giornate dal montaggio). Senza account funziona subito, ma i dati restano sul dispositivo. Per avere un account privato, uguale su iPhone, Mac e PC, collega Firebase (gratis, circa 10 minuti):

1. Vai su console.firebase.google.com, accedi con un account Google e premi **Crea un progetto** (puoi disattivare Google Analytics).
2. **Build → Authentication → Inizia**. In «Metodo di accesso» attiva **Email/password**. L'app usa username e password: lo username diventa un indirizzo interno che non riceve posta, quindi la password non si recupera.
3. In **Authentication → Impostazioni → Domini autorizzati** aggiungi `fran-1422.github.io`.
4. **Build → Firestore Database → Crea database**, modalità produzione, regione `eur3` (Europa). Poi scheda **Regole**, incolla il contenuto di `firestore.rules` e premi **Pubblica**.
5. **Impostazioni progetto (ingranaggio) → Le tue app → icona web `</>`**: registra un'app e copia l'oggetto `firebaseConfig` (apiKey, authDomain, projectId, appId).
6. Incolla quei valori in `firebase-config.js` al posto di `window.TDF_FIREBASE = null;` e salva su GitHub.

Le chiavi di Firebase sono pubbliche per progetto: a proteggere i dati sono l'accesso con account e le regole del punto 4. L'accesso funziona anche nell'app installata su iPhone. Non c'è accesso con Google.

## Se un sito cambia

Ogni sito ha una struttura diversa e può cambiarla. In quel caso:

- l'app tiene le date che aveva già;
- nella tabella «Fonti controllate» e in un avviso in alto compare «da controllare» o «errore»;
- mandami il nome del sito e riscrivo la lettura di quel sito.

## Limiti da sapere

- Il programma è stato provato su pagine ricostruite dal testo dei siti, non sulle pagine vere, perché dall'ambiente in cui l'ho scritto non potevo raggiungerle. Il primo giorno controlla le date confrontandole con i siti.
- Rehm e Speer sono letti dai loro siti ufficiali; se un sito non risponde si usa come riserva il portale Racing4Fun. Turni sovrapposti dello stesso circuito (formula compatta, camp) diventano una sola voce, con il prezzo più basso. Per Speer sono esclusi corsi istruttori, coaching 1:1 e corsi di piega.
- Il calendario provvisorio 2027 di Rosso Corsa è un PDF immagine e non viene letto.
- Cremona Circuit mostra sul proprio sito solo il mese corrente: le date dei mesi successivi arrivano dagli organizzatori.

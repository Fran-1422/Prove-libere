// Service worker: l'app funziona anche senza rete. Pagina e date si cercano sempre prima
// in rete (cosi' gli aggiornamenti arrivano subito) e, se manca la connessione, si usa
// l'ultima copia salvata.
const CACHE = "prove-libere-v5";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (url.pathname.endsWith("/data.json")) {
    e.respondWith(
      fetch(req, { cache: "no-store" })
        .then((res) => { const copy = res.clone(); caches.open(CACHE).then((c) => c.put("data.json", copy)); return res; })
        .catch(() => caches.match("data.json"))
    );
    return;
  }
  e.respondWith(
    fetch(req, { cache: "no-cache" })
      .then((res) => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
        return res;
      })
      .catch(() => caches.match(req).then((hit) => hit || caches.match("./")))
  );
});

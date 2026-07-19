/* Alora LXP service worker — offline shell + background sync tag */
const CACHE = 'alora-lxp-v1';
const SHELL = ['/', '/static/lxp/manifest.webmanifest'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  event.respondWith(
    caches.match(req).then((cached) => {
      const fetched = fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() => cached || new Response('Offline', { status: 503, statusText: 'Offline' }));
      return cached || fetched;
    })
  );
});

self.addEventListener('sync', (event) => {
  if (event.tag === 'lxp-sync') {
    event.waitUntil(Promise.resolve());
  }
});

self.addEventListener('push', (event) => {
  const data = event.data ? event.data.text() : 'Alora update';
  event.waitUntil(self.registration.showNotification('Alora LXP', { body: data }));
});

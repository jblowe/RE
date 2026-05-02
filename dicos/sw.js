const CACHE = "tamang-dictionary-v3";

const PRECACHE = [
  "/tmg/TamangDictionary.html",
  "/tmg/manifest.json",
  "/tmg/sw.js",
  "/tmg/icons/icon-192.png",
  "/tmg/icons/icon-512.png",
  "/tmg/icons/icon-512-maskable.png",
  "/tmg/icons/apple-touch-icon-180.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(
      cached => cached || fetch(event.request)
    )
  );
});

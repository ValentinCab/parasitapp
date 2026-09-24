const CACHE='atlas-parasitologia-v20';
const CORE=['./','./index.html','./styles.css','./table-colors.css','./image-gallery.css','./app-v5.js?core=20','./data/seed-v2.json','./favicon.svg'];
const CRITICAL=['/index.html','/app-v5.js','/app.js','/styles.css','/table-colors.css','/image-gallery.css','/data/seed-v2.json'];
self.addEventListener('install',event=>{self.skipWaiting();event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(CORE)).catch(()=>{}))});
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('atlas-parasitologia-')&&key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  const url=new URL(event.request.url),critical=url.origin===self.location.origin&&(event.request.mode==='navigate'||CRITICAL.some(path=>url.pathname.endsWith(path)));
  if(critical){event.respondWith(fetch(event.request).then(response=>{if(response.ok)caches.open(CACHE).then(cache=>cache.put(event.request,response.clone()));return response}).catch(()=>caches.match(event.request).then(response=>response||caches.match('./'))));return}
  event.respondWith(caches.match(event.request).then(response=>response||fetch(event.request).then(network=>{if(network.ok&&url.origin===self.location.origin)caches.open(CACHE).then(cache=>cache.put(event.request,network.clone()));return network})));
});

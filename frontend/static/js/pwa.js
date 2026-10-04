// Register PWA Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then((registration) => {
                console.log('MediScan PWA ServiceWorker registered with scope:', registration.scope);
            })
            .catch((error) => {
                console.warn('MediScan PWA ServiceWorker registration failed:', error);
            });
    });
}

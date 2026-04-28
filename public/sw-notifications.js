// Custom Service Worker additions for CS Mastery
// This file is imported by vite-plugin-pwa as additional SW code

// Handle notification click — open app or specific route
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const data = event.notification.data || {}
  const targetUrl = data.url || '/cs-mastery/'

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // If app is already open, focus it and navigate
      for (const client of clientList) {
        if (client.url.includes('/cs-mastery') && 'focus' in client) {
          client.focus()
          if ('navigate' in client) {
            client.navigate(targetUrl)
          }
          return
        }
      }
      // Otherwise open a new window
      if (clients.openWindow) {
        return clients.openWindow(targetUrl)
      }
    })
  )
})

// Handle push events (for real push notifications from a server)
self.addEventListener('push', (event) => {
  let data = { title: '🎯 CS Mastery', body: 'Time to study!', url: '/cs-mastery/' }
  if (event.data) {
    try { data = { ...data, ...event.data.json() } } catch { /* use defaults */ }
  }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/cs-mastery/icon-192.png',
      badge: '/cs-mastery/icon-192.png',
      tag: 'csm-push',
      requireInteraction: false,
      data: { url: data.url },
    })
  )
})


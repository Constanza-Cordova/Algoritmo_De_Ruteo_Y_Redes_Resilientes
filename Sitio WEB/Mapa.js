var map = L.map('map').setView([-33.45, -70.66], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Ejemplo de nodo
L.marker([-33.45, -70.66]).addTo(map).bindPopup("Nodo A");

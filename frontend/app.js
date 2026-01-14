const params = new URLSearchParams(window.location.search);
const topluluk = params.get('topluluk');
const user = JSON.parse(localStorage.getItem('user'));
let map;
let markers = []; // Markerları takip etmek ve temizlemek için

document.addEventListener('DOMContentLoaded', () => {
    if (!user) { location.href = 'index.html'; return; }
    if (!topluluk) { alert("Topluluk seçilmedi!"); return; }

    document.getElementById('topluluk-title').innerText = `${topluluk} Sayfası`;
    initMap();
    fetchEvents();
});

function initMap() {
    // Kampüs odaklı harita (Beytepe Yerleşkesi)
    map = L.map('map').setView([39.8656, 32.7339], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap'
    }).addTo(map);

async function editEv(id, oldName) {
    const newName = prompt("Yeni Etkinlik Adı:", oldName);
    if (newName && newName !== oldName) {
        const res = await fetch(`http://localhost:8000/api/events/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ etkinlik_name: newName })
        });
        if (res.ok) {
            alert("Güncellendi!");
            fetchEvents();
        }
    }
}   

    // Haritaya tıklama olayı
    map.on('click', async (e) => {
        if (user.role === 'STUDENT') return alert("Öğrenci nokta ekleyemez!");
        
        const name = prompt("Etkinlik Adı:");
        if (name) {
            await fetch('http://localhost:8000/api/events', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    topluluk: topluluk,
                    etkinlik_name: name,
                    lat: e.latlng.lat,
                    lng: e.latlng.lng,
                    image_url: `images/${topluluk}.jpeg` 
                })
            });
            fetchEvents(); // Listeyi ve haritayı güncelle
        }
    });
}

// ... dosyanın üstündeki diğer kodlar aynı kalacak ...

async function fetchEvents(q = '') {
    try {
        const res = await fetch(`http://localhost:8000/api/events?topluluk=${topluluk}&q=${q}`);
        const data = await res.json();
        
        markers.forEach(m => map.removeLayer(m));
        markers = [];

        const grid = document.getElementById('eventGrid');
        grid.innerHTML = data.map(ev => `
            <div class="event-card">
                <img src="${ev.image_url}" onerror="this.src='https://via.placeholder.com/300x200?text=Etkinlik'">
                <div class="event-info">
                    <h3>${ev.etkinlik_name}</h3>
                    <div style="display: flex; gap: 5px; margin-top: 10px;">
                        ${user.role === 'ADMIN' ? 
                            `<button class="btn" style="background: #e74c3c;" onclick="deleteEv('${ev.id}')">Sil</button>` : ''}
                        
                        ${user.role === 'ADMIN' || user.role === 'COMMUNITY_LEADER' ? 
                            `<button class="btn" style="background: #f39c12;" onclick="editEv('${ev.id}', '${ev.etkinlik_name}')">Düzenle</button>` : ''}
                    </div>
                </div>
            </div>
        `).join('');

        data.forEach(ev => {
            if (ev.lat && ev.lng) {
                const m = L.marker([ev.lat, ev.lng])
                            .addTo(map)
                            .bindPopup(`<b>${ev.etkinlik_name}</b>`);
                markers.push(m);
            }
        });
    } catch (err) {
        console.error("Hata:", err);
    }
}

// PUT İşlemi: Coğrafi özelliğin özniteliğini günceller 
async function editEv(id, oldName) {
    const newName = prompt("Yeni Etkinlik Adı:", oldName);
    if (newName && newName !== oldName) {
        const res = await fetch(`http://localhost:8000/api/events/${id}`, {
            method: 'PUT', // PUT endpoint kullanımı 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ etkinlik_name: newName })
        });
        if (res.ok) {
            alert("Etkinlik başarıyla güncellendi!");
            fetchEvents();
        }
    }
}

// DELETE İşlemi: Mekansal özelliği siler [cite: 35]
async function deleteEv(id) {
    if (confirm("Bu etkinliği silmek istediğinize emin misiniz?")) {
        await fetch(`http://localhost:8000/api/events/${id}`, { method: 'DELETE' });
        fetchEvents();
    }
}
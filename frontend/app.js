const params = new URLSearchParams(window.location.search);
const topluluk = params.get('topluluk');
const user = JSON.parse(localStorage.getItem('user'));

// Lokal Sunucu Adresi
const API_URL = "http://127.0.0.1:8000/api/events"; 

let map;
let markers = []; 
let tempLatLng; // Tıklanan koordinatları modal için hafızada tutar

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

    // Haritaya tıklama olayı: Modalı açar
    map.on('click', (e) => {
        if (user.role === 'STUDENT') return alert("Öğrenci nokta ekleyemez!");
        
        tempLatLng = e.latlng;
        document.getElementById('eventModal').style.display = 'block';
    });
}

// Modalı Kapatma Fonksiyonu
function closeModal() {
    document.getElementById('eventModal').style.display = 'none';
    document.getElementById('modalEventName').value = "";
    document.getElementById('modalImgUrl').value = "";
}

// Modal Üzerinden Etkinlik Kaydetme
async function saveEventFromModal() {
    const name = document.getElementById('modalEventName').value;
    const inputImg = document.getElementById('modalImgUrl').value;
    
    // MANTIK: Link boşsa 'Hendslogo.jpeg' gibi isimlendirmeyi kullanır
    const img = inputImg.trim() !== "" ? inputImg : `images/${topluluk}logo.jpeg`;

    if (!name) return alert("Lütfen etkinlik adını girin!");

    try {
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                topluluk: topluluk,
                etkinlik_name: name,
                lat: tempLatLng.lat,
                lng: tempLatLng.lng,
                image_url: img
            })
        });

        if (res.ok) {
            fetchEvents(); // Listeyi yenile
            closeModal();  // Paneli kapat
        } else {
            alert("Ekleme işlemi başarısız!");
        }
    } catch (err) {
        alert("Sunucu hatası! Uvicorn çalışıyor mu?");
    }
}

// Etkinlikleri Çekme ve Haritaya Ekleme
async function fetchEvents(q = '') {
    try {
        const res = await fetch(`${API_URL}?topluluk=${topluluk}&q=${q}`);
        const data = await res.json();
        
        // Eski markerları temizle
        markers.forEach(m => map.removeLayer(m));
        markers = [];

        const grid = document.getElementById('eventGrid');
        // Kart yapısı: Resim hatasında yedek logoyu gösterir
        grid.innerHTML = data.map(ev => `
            <div class="event-card">
                <img src="${ev.image_url}" onerror="this.src='images/${topluluk}logo.jpeg'">
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

        // Haritaya markerları yerleştir
        data.forEach(ev => {
            if (ev.lat && ev.lng) {
                const m = L.marker([ev.lat, ev.lng])
                            .addTo(map)
                            .bindPopup(`<b>${ev.etkinlik_name}</b>`);
                markers.push(m);
            }
        });
    } catch (err) {
        console.error("Veri çekme hatası:", err);
    }
}

// Veri Güncelleme (PUT)
async function editEv(id, oldName) {
    const newName = prompt("Yeni Etkinlik Adı:", oldName);
    if (newName && newName !== oldName) {
        try {
            const res = await fetch(`${API_URL}/${id}`, {
                method: 'PUT', 
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ etkinlik_name: newName })
            });
            if (res.ok) {
                alert("Güncellendi!");
                fetchEvents();
            }
        } catch (err) {
            alert("Hata oluştu!");
        }
    }
}

// Veri Silme (DELETE)
async function deleteEv(id) {
    if (confirm("Bu etkinliği silmek istediğinize emin misiniz?")) {
        try {
            const res = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
            if (res.ok) {
                fetchEvents();
            }
        } catch (err) {
            alert("Silme başarısız!");
        }
    }
}
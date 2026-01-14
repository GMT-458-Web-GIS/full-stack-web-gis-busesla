import bcrypt
import os
import random
import smtplib
from datetime import datetime
from email.message import EmailMessage

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from bson import ObjectId
from dotenv import load_dotenv

# Veritabanı bağlantı fonksiyonlarını içe aktar
from database import db, serialize 

# .env dosyasını yükle
load_dotenv()

app = FastAPI(title="Hacettepe Topluluk Portalı API")

# --- 1. CORS AYARLARI (Hata Almamak İçin En Üstte Olmalı) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. AYARLAR VE GÜVENLİK ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# E-posta Ayarları (.env dosyasından veya doğrudan buradan güncelleyin)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "busesla0107@gmail.com") 
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "wllu bfit quie wasj") 

# --- 3. YARDIMCI FONKSİYONLAR ---
def send_otp_email(target_email, otp_code):
    try:
        msg = EmailMessage()
        msg.set_content(f"Hacettepe Topluluk Portalı için doğrulama kodunuz: {otp_code}")
        msg["Subject"] = "E-posta Doğrulama Kodu"
        msg["From"] = SENDER_EMAIL
        msg["To"] = target_email
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"E-posta gönderme hatası: {e}")
        # Geliştirme aşamasında mail gitmezse kodu terminale yazdıralım
        print(f"KOD: {otp_code}")

# --- 4. AUTHENTICATION ENDPOINTLERİ ---

@app.post("/api/signup")
async def signup(data: dict = Body(...)):
    existing = await db.users.find_one({"email": data["email"]})
    if existing:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kayıtlı.")

    otp = str(random.randint(100000, 999999))
    password_bytes = data["password"].encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    new_user = {
        "email": data["email"],
        "username": data["email"].split('@')[0], # Mailin başını kullanıcı adı yap
        "password": hashed_password,
        "role": "STUDENT",
        "is_active": False,
        "otp_code": otp,
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(new_user)
    send_otp_email(data["email"], otp)
    return {"message": "Doğrulama kodu e-postanıza gönderildi."}

@app.post("/api/verify")
async def verify(data: dict = Body(...)):
    user = await db.users.find_one({"email": data["email"], "otp_code": data["code"]})
    if not user:
        raise HTTPException(status_code=400, detail="Doğrulama kodu hatalı!")
    
    await db.users.update_one(
        {"_id": user["_id"]}, 
        {"$set": {"is_active": True}, "$unset": {"otp_code": ""}}
    )
    return {"message": "Hesabınız başarıyla doğrulandı!"}

@app.post("/api/login")
async def login(credentials: dict = Body(...)):
    user = await db.users.find_one({"email": credentials.get("email")})
    
    if not user:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı.")
    
    if not user.get("is_active"):
        raise HTTPException(status_code=401, detail="Lütfen önce hesabınızı doğrulayın.")

    try:
        # Doğrudan bcrypt kullanarak doğrulama (En güvenli ve sorunsuz yol)
        # Şifreleri byte formatına çeviriyoruz
        user_password_bytes = credentials.get("password").encode('utf-8')
        stored_password_bytes = user["password"].encode('utf-8')

        # Bcrypt sınırı kontrolü (72 karakter)
        if len(user_password_bytes) > 72:
            raise HTTPException(status_code=400, detail="Şifre çok uzun!")

        if not bcrypt.checkpw(user_password_bytes, stored_password_bytes):
            raise HTTPException(status_code=401, detail="Hatalı şifre.")
            
    except Exception as err:
        print(f"Bcrypt Hatası: {err}")
        raise HTTPException(status_code=500, detail="Doğrulama sırasında teknik bir hata oluştu.")
    
    return serialize(user)

# --- 5. GIS VE ETKİNLİK ENDPOINTLERİ ---
@app.put("/api/events/{event_id}")
async def update_event(event_id: str, data: dict = Body(...)):
    # Sadece Admin veya ilgili Topluluk Yöneticisi güncelleyebilir (Mantıksal kural)
    update_data = {
        "etkinlik_name": data.get("etkinlik_name"),
        "updated_at": datetime.utcnow()
    }
    result = await db.events.update_one(
        {"_id": ObjectId(event_id)}, 
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Etkinlik bulunamadı")
    return {"message": "Etkinlik başarıyla güncellendi"}

@app.get("/api/events")
async def get_events(topluluk: str, q: str = None):
    query = {"topluluk": topluluk}
    if q:
        query["etkinlik_name"] = {"$regex": q, "$options": "i"}
    
    events = await db.events.find(query).to_list(length=100)
    return [serialize(e) for e in events]

@app.post("/api/events")
async def create_event(event: dict = Body(...)):
    event["created_at"] = datetime.utcnow()
    # MongoDB 2dsphere indeksi için gerekli GeoJSON formatı
    event["location"] = {
        "type": "Point",
        "coordinates": [float(event.get("lng")), float(event.get("lat"))]
    }
    result = await db.events.insert_one(event)
    return {"id": str(result.inserted_id)}

@app.delete("/api/events/{event_id}")
async def delete_event(event_id: str):
    await db.events.delete_one({"_id": ObjectId(event_id)})
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
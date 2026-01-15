import bcrypt
import os
import random
import smtplib
from datetime import datetime
from email.message import EmailMessage
from passlib.context import CryptContext
from bson import ObjectId
from dotenv import load_dotenv

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# .env dosyasını yükle
load_dotenv()

# Veritabanı bağlantı fonksiyonlarını içe aktar
from database import db, serialize 

# 1. FastAPI Tanımı
app = FastAPI(title="Hacettepe Topluluk Portalı API - Lokal Mod")

# 2. CORS AYARLARI (Lokal geliştirme için tüm kökenlere izin veriyoruz)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AYARLAR VE GÜVENLİK ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# E-posta Ayarları (Hala Gmail üzerinden çalışmaya devam eder)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "busesla0107@gmail.com") 
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "wllu bfit quie wasj") 

# --- YARDIMCI FONKSİYONLAR ---
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
        # Lokal çalışırken e-posta gitmezse kodu terminale yazdırıyoruz
        print(f"\n--- DOĞRULAMA KODU (Terminal Log): {otp_code} ---\n")
        print(f"Hata detayı: {e}")

# --- AUTHENTICATION ENDPOINTLERİ ---

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
        "username": data["email"].split('@')[0],
        "password": hashed_password,
        "role": "STUDENT",
        "is_active": False,
        "otp_code": otp,
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(new_user)
    send_otp_email(data["email"], otp)
    return {"message": "Doğrulama kodu gönderildi. Lütfen e-postanızı veya terminali kontrol edin."}

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
        user_password_bytes = credentials.get("password").encode('utf-8')
        stored_password_bytes = user["password"].encode('utf-8')

        if len(user_password_bytes) > 72:
            raise HTTPException(status_code=400, detail="Şifre çok uzun!")

        if not bcrypt.checkpw(user_password_bytes, stored_password_bytes):
            raise HTTPException(status_code=401, detail="Hatalı şifre.")
            
    except Exception as err:
        print(f"Bcrypt Hatası: {err}")
        raise HTTPException(status_code=500, detail="Doğrulama sırasında teknik bir hata oluştu.")
    
    return serialize(user)

# --- GIS VE ETKİNLİK ENDPOINTLERİ ---

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
    event["location"] = {
        "type": "Point",
        "coordinates": [float(event.get("lng")), float(event.get("lat"))]
    }
    result = await db.events.insert_one(event)
    return {"id": str(result.inserted_id)}

@app.put("/api/events/{event_id}")
async def update_event(event_id: str, data: dict = Body(...)):
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

@app.delete("/api/events/{event_id}")
async def delete_event(event_id: str):
    await db.events.delete_one({"_id": ObjectId(event_id)})
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    # Lokal çalışırken host "127.0.0.1" (localhost) olmalıdır
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
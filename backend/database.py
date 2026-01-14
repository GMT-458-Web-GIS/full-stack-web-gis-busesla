from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yükle
load_dotenv()

# MongoDB Bağlantı Ayarları
# .env dosyan yoksa varsayılan olarak yerel hostu kullanır
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "topluluk_event")

# MongoDB Client ve Veritabanı Seçimi
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

def serialize(doc):
    """
    MongoDB dökümanlarını JSON ile uyumlu hale getirir.
    _id (ObjectId) alanını string formatında 'id' olarak değiştirir.
    """
    if doc is None:
        return None
    
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc
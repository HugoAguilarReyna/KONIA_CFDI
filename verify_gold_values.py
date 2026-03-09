
import pymongo
import os

# URI from app.py defaults (or inferred)
MONGO_URI = "mongodb+srv://aguilarhugo55_db_user:c5mfG11QT68ib4my@clusteract1.kpdhd5e.mongodb.net/cfdi_db?authSource=admin&appName=ClusterAct1"
DB_NAME = "cfdi_db"
COLLECTION_NAME = "gold_cfdi"

def check_gold():
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        col = db[COLLECTION_NAME]
        
        doc = col.find_one()
        if doc:
            print("Successfully connected to cfdi_db.gold_cfdi")
            print(f"Sample company_id: {doc.get('company_id')} (Type: {type(doc.get('company_id'))})")
            
            # Check unique company_ids
            ids = col.distinct("company_id")
            print(f"Distinct company_ids: {ids}")
        else:
            print("Connected but collection is empty.")
            
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    check_gold()

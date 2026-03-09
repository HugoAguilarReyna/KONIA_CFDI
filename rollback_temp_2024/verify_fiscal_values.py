
import pymongo
import os

# URI from matriz_resumen_module.py
MONGO_URI = "mongodb+srv://aguilarhugo55_db_user:c5mfG11QT68ib4my@clusteract1.kpdhd5e.mongodb.net/fiscal_reports?authSource=admin&appName=ClusterAct1"
DB_NAME = "fiscal_reports"
COLLECTION_NAME = "matriz_resumen"

def check_values():
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        col = db[COLLECTION_NAME]
        
        # Get 5 documents to see variety
        docs = list(col.find().limit(5))
        if docs:
            print(f"Found {len(docs)} documents.")
            for i, doc in enumerate(docs):
                print(f"--- Document {i+1} ---")
                for k, v in doc.items():
                    print(f"{k}: {v}")
        else:
            print("Connected but collection is empty.")
            
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    check_values()

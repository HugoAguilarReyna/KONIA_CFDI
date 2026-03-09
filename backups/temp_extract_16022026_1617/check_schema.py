from pymongo import MongoClient
import os

MONGO_URI = "mongodb+srv://aguilarhugo55_db_user:c5mfG11QT68ib4my@clusteract1.kpdhd5e.mongodb.net/fiscal_reports?authSource=admin&appName=ClusterAct1"
DB_NAME = "fiscal_reports"
COLLECTION_NAME = "matriz_resumen"

def check_schema():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        col = db[COLLECTION_NAME]
        
        doc = col.find_one()
        if doc:
            print("Keys found in document:")
            for key in doc.keys():
                print(f"- {key}: {type(doc[key])}")
                
            # Check unique values for concept to see if it's aggregated
            count = col.count_documents({})
            print(f"\nTotal documents: {count}")
        else:
            print("Collection is empty.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()

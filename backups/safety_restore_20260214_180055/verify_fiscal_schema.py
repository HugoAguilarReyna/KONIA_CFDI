
import pymongo
import pandas as pd
import os

# URI from matriz_resumen_module.py
MONGO_URI = "mongodb+srv://aguilarhugo55_db_user:c5mfG11QT68ib4my@clusteract1.kpdhd5e.mongodb.net/fiscal_reports?authSource=admin&appName=ClusterAct1"
DB_NAME = "fiscal_reports"
COLLECTION_NAME = "matriz_resumen"

def check_structure():
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        col = db[COLLECTION_NAME]
        
        doc = col.find_one()
        if doc:
            print("Successfully connected to fiscal_reports.matriz_resumen")
            print("Keys found in document:")
            print(list(doc.keys()))
            
            # Check availability of critical columns for procesar_matriz_dinamica
            required = ['fecha_emision', 'total', 'metodo_pago', 'tipo', 'tipo_relacion']
            missing = [r for r in required if r not in doc]
            if missing:
                print(f"WARNING: Missing columns: {missing}")
            else:
                print("All required columns for processing appear to be present.")
        else:
            print("Connected but collection is empty.")
            
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    check_structure()

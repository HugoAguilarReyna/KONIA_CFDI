from pymongo import MongoClient

uri = 'mongodb+srv://aguilarhugo55_db_user:c5mfG11QT68ib4my@clusteract1.kpdhd5e.mongodb.net/?authSource=admin&appName=ClusterAct1'
client = MongoClient(uri)

# Check ALL databases and their collections
print("=== ALL DATABASES ===")
for db_info in client.list_databases():
    db_name = db_info['name']
    db = client[db_name]
    
    try:
        cols = db.list_collection_names()
        for col_name in cols:
            if col_name in ['detalle_uuid', 'gold_cfdi', 'cfdis', 'cfdi']:
                count = db[col_name].count_documents({})
                if count > 0:
                    # Check for nombre_emisor
                    sample = db[col_name].find_one({})
                    fields = list(sample.keys()) if sample else []
                    print(f"  {db_name}.{col_name}: {count} docs | fields: {fields[:8]}")
    except Exception as e:
        print(f"  {db_name}: ERROR {e}")

# Also specifically check cfdi_db
print("\n=== cfdi_db collections ===")
cfdi_db = client['cfdi_db']
try:
    for col_name in cfdi_db.list_collection_names():
        count = cfdi_db[col_name].count_documents({})
        print(f"  cfdi_db.{col_name}: {count} docs")
except Exception as e:
    print(f"  ERROR: {e}")

client.close()

from pymongo import MongoClient
import pprint

client = MongoClient("mongodb+srv://admin:PrQ1122@cluster0.h1194.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["fiscal_reports"]
company_id = 2

pipeline = [
    {"$match": {"company_id": company_id}},
    {"$sort": {"fecha": 1}},
    {"$group": {
        "_id": "$uuid_raiz",
        "ultimo_saldo": {"$last": "$saldo_acumulado"},
        "total_eventos": {"$sum": 1},
        "primer_evento": {"$first": "$fecha"},
        "ultimo_evento": {"$last": "$fecha"},
        "total_monto": {"$sum": "$monto"},
        "periodos": {"$addToSet": "$periodo"}
    }},
    {"$sort": {"ultimo_evento": -1}}
]
uuids = list(db["trazabilidad_uuid"].aggregate(pipeline))
print(f"Total UUIDs found for company_id 2: {len(uuids)}")

if not uuids:
    print("Trying without company_id...")
    pipeline[0]["$match"] = {}
    uuids_all = list(db["trazabilidad_uuid"].aggregate(pipeline))
    print(f"Total UUIDs found without company_id filter: {len(uuids_all)}")
    if uuids_all:
        import random
        sample = random.choice(uuids_all)
        print("Sample UUID without company filter:")
        pprint.pprint(sample)
        # Find raw document for this sample
        raw = db["trazabilidad_uuid"].find_one({"uuid_raiz": sample["_id"]})
        print("Raw document company_id type:", type(raw.get("company_id")), raw.get("company_id"))

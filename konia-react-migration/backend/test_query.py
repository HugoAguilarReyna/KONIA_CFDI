from app.core.database import get_database

db = get_database().client["fiscal_reports"]
filtro = {"company_id": "TENANT_001", "periodo": "2026-02"}

tipo = ["Egreso,Ingreso"]
tipo_list = tipo[0].split(",") if isinstance(tipo[0], str) and "," in tipo[0] else tipo
mapped_flujo = []
for t in tipo_list:
    if t.lower() == "ingreso": mapped_flujo.append("EMITIDOS")
    if t.lower() == "egreso": mapped_flujo.append("RECIBIDOS")
if mapped_flujo:
    filtro["flujo"] = {"$in": mapped_flujo}

print("Filtro:", filtro)

print("Otros count:", db.detalle_uuid.count_documents({**filtro, "segmento": "OTROS"}))
print("PPD count:", db.detalle_uuid.count_documents({**filtro, "segmento": "PPD"}))

dist_flujo = list(db.detalle_uuid.aggregate([
    {"$match": filtro},
    {"$group": {
        "_id": "$flujo",
        "count": {"$sum": 1}
    }}
]))
print("Dist flujo:", dist_flujo)

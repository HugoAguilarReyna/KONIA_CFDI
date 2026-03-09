"""
backfill_emisor_receptor.py
===========================
Parcha los documentos en detalle_uuid que tienen nombre_emisor/rfc_emisor/
nombre_receptor/rfc_receptor = null, obteniendo los datos correctos de BigQuery.

Ejecución:
    python backfill_emisor_receptor.py
"""

import pandas as pd
from google.cloud import bigquery
from pymongo import MongoClient, UpdateOne
import warnings, time

warnings.simplefilter(action='ignore', category=FutureWarning)

# ─── CONFIG ────────────────────────────────────────────────────────────────
CONFIG = {
    "project_id": "csreporter-iso27001",
    "dataset_id": "csmonitor",
    "company_id": 2,
    "mongo_uri": (
        "mongodb+srv://aguilarhugo55_db_user:c5mfG11QT68ib4my"
        "@clusteract1.kpdhd5e.mongodb.net/fiscal_reports?authSource=admin&appName=ClusterAct1"
    ),
    "mongo_db": "fiscal_reports",
    "col_detalle": "detalle_uuid",
}

# ─── CONEXIONES ────────────────────────────────────────────────────────────
bq_client = bigquery.Client(project=CONFIG["project_id"])
mongo_client = MongoClient(CONFIG["mongo_uri"])
db = mongo_client[CONFIG["mongo_db"]]
col = db[CONFIG["col_detalle"]]

# ─── 1. Encontrar UUIDs sin datos de emisor/receptor ──────────────────────
print("🔍 Buscando documentos con nombre_emisor null...")
docs_null = list(col.find(
    {"company_id": CONFIG["company_id"], "nombre_emisor": None},
    {"_id": 0, "uuid": 1, "periodo": 1}
))
print(f"   → {len(docs_null)} documentos encontrados")

if not docs_null:
    print("✅ No hay documentos por actualizar.")
    exit(0)

uuids_null = list({d["uuid"] for d in docs_null})
print(f"   → {len(uuids_null)} UUIDs únicos a consultar en BigQuery")

# ─── 2. Consultar BigQuery para obtener emisor/receptor por UUID ───────────
CHUNK_SIZE = 500   # BigQuery tiene límite en IN clauses muy largas
dataset = f"{CONFIG['project_id']}.{CONFIG['dataset_id']}"

all_rows = []
for i in range(0, len(uuids_null), CHUNK_SIZE):
    chunk = uuids_null[i:i + CHUNK_SIZE]
    # Convertir a mayúsculas en Python y poner como literales SQL ya normalizados
    uuids_upper = [u.upper() for u in chunk]
    uuids_sql = ", ".join(f"'{u}'" for u in uuids_upper)
    query = f"""
        SELECT
            UPPER(c.uuid) AS uuid,
            e.rfc         AS rfc_emisor,
            e.nombre      AS nombre_emisor,
            r.rfc         AS rfc_receptor,
            r.nombre      AS nombre_receptor
        FROM `{dataset}.public_cfdis` c
        LEFT JOIN `{dataset}.public_cfdi_emisors`  e ON c.emisor_id  = e.id
        LEFT JOIN `{dataset}.public_cfdi_receptors` r ON c.receptor_id = r.id
        WHERE UPPER(c.uuid) IN ({uuids_sql})
    """
    # NOTA: Se quitó el filtro AND c.company_id = {CONFIG['company_id']}
    # porque las facturas RECIBIDAS (RECIBIDOS) pertenecen a otros emisores
    # que tienen un company_id diferente en BigQuery.
    try:
        df_chunk = bq_client.query(query).to_dataframe()
        all_rows.append(df_chunk)
        print(f"   ✓ Chunk {i//CHUNK_SIZE + 1}: {len(df_chunk)} resultados")
    except Exception as e:
        print(f"   ❌ Error en chunk {i//CHUNK_SIZE + 1}: {e}")

if not all_rows:
    print("⚠️ No se obtuvieron datos de BigQuery")
    exit(1)

df_info = pd.concat(all_rows, ignore_index=True)
df_info = df_info.dropna(subset=["rfc_emisor"])  # Solo los que sí encontramos
df_info["uuid_upper"] = df_info["uuid"].str.upper()
df_info = df_info.drop_duplicates(subset=["uuid_upper"])

print(f"\n📊 BigQuery devolvió datos para {len(df_info)} / {len(uuids_null)} UUIDs")

# ─── 3. Construir operaciones bulk para MongoDB ────────────────────────────
uuid_to_info = {
    row["uuid_upper"]: {
        "rfc_emisor":    row["rfc_emisor"],
        "nombre_emisor": row["nombre_emisor"],
        "rfc_receptor":  row["rfc_receptor"],
        "nombre_receptor": row["nombre_receptor"],
    }
    for _, row in df_info.iterrows()
}

bulk_ops = []
actualizados = 0
no_encontrados = 0

for d in docs_null:
    uuid_up = d["uuid"].upper()
    if uuid_up in uuid_to_info:
        info = uuid_to_info[uuid_up]
        bulk_ops.append(UpdateOne(
            {"company_id": CONFIG["company_id"], "uuid": d["uuid"]},
            {"$set": info}
        ))
        actualizados += 1
    else:
        no_encontrados += 1

print(f"\n💾 Documentos a actualizar: {actualizados}")
print(f"⚠️  Sin datos en BigQuery:   {no_encontrados}")

# ─── 4. Ejecutar en MongoDB ────────────────────────────────────────────────
if bulk_ops:
    BATCH = 1000
    t0 = time.time()
    for i in range(0, len(bulk_ops), BATCH):
        col.bulk_write(bulk_ops[i:i+BATCH], ordered=False)
        print(f"   ✓ Batch {i//BATCH + 1}/{(len(bulk_ops)-1)//BATCH + 1} guardado")
    print(f"\n✅ Backfill completado en {time.time()-t0:.1f}s")
    print(f"   {actualizados} documentos actualizados con nombre/RFC de emisor y receptor")
else:
    print("⚠️ No hay operaciones para ejecutar")

mongo_client.close()

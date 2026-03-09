import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb+srv://aguilarhugo55_db_user:c5mfG11QT68ib4my@clusteract1.kpdhd5e.mongodb.net/fiscal_reports?authSource=admin&appName=ClusterAct1"
client = MongoClient(MONGO_URI)
db = client["fiscal_reports"]

def _signed_saldo(doc):
    field = doc.get("saldo_acumulado", 0)
    if doc.get("flujo") == "RECIBIDOS":
        return -abs(field)
    return field

def get_stats():
    company_id = 2
    # Periods: 2025-10 to 2026-03
    periods = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"]
    
    print(f"{'Periodo':<10} | {'PPD Total':<20} | {'PUE Total':<20}")
    print("-" * 55)
    
    for p in periods:
        # PPD
        docs_ppd = db.detalle_uuid.find({"company_id": company_id, "periodo": p, "segmento": "PPD"})
        total_ppd = sum(_signed_saldo(d) for d in docs_ppd)
        
        # PUE
        docs_pue = db.detalle_uuid.find({"company_id": company_id, "periodo": p, "segmento": "PUE"})
        total_pue = sum(_signed_saldo(d) for d in docs_pue)
        
        print(f"{p:<10} | {total_ppd:>20,.2f} | {total_pue:>20,.2f}")

if __name__ == "__main__":
    get_stats()

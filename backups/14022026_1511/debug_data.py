import os
from dotenv import load_dotenv
import pandas as pd
from google.cloud import bigquery
import datetime

# Load env vars
load_dotenv()

print("--- DEBUG CONFIG ---")
print(f"Project: {os.getenv('BQ_PROJECT_ID')}")
print(f"Dataset: {os.getenv('BQ_DATASET_ID')}")
print(f"Company ID: {os.getenv('BQ_COMPANY_ID')}")

def load_data_debug():
    bq_project = os.getenv("BQ_PROJECT_ID")
    if not bq_project:
        print("ERROR: No BQ_PROJECT_ID")
        return

    try:
        client = bigquery.Client(project=bq_project)
        dataset = f"{bq_project}.{os.getenv('BQ_DATASET_ID', 'csmonitor')}"
        company_id_bq = int(os.getenv("BQ_COMPANY_ID", "2"))
        
        now = datetime.datetime.now()
        default_periods = [(now - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(12)]
        p_sql = ", ".join([f"'{p}'" for p in default_periods])
        
        print(f"Querying periods: {p_sql}")
        
        # VOLUMETRY CHECK FOR COMPANY_ID=2, FEB 2026
        print("=" * 60)
        print("VOLUMETRY CHECK: company_id=2, Feb 2026")
        print("=" * 60)
        volumetry_query = f"""
            SELECT COUNT(*) as total_registros
            FROM `{dataset}.public_cfdis` 
            WHERE FORMAT_DATE('%Y-%m', fecha_emision) = '2026-02'
              AND company_id = {company_id_bq}
              AND estatus = 'vigente'
              AND tipo IN ('I', 'E')
        """
        try:
            df_vol = client.query(volumetry_query).to_dataframe()
            total = df_vol['total_registros'].iloc[0]
            print(f"✅ TOTAL REGISTROS (company_id={company_id_bq}, Feb 2026): {total:,}")
            print(f"   - Con LIMIT actual (10k): Cargando {min(10000, total):,} / {total:,} ({(min(10000, total)/total*100):.1f}%)")
            if total > 10000:
                print(f"   ⚠️ ADVERTENCIA: Hay {total - 10000:,} registros NO mostrados")
        except Exception as vol_e:
            print(f"❌ VOLUMETRY ERROR: {vol_e}")
        
        print("=" * 60)
        return # STOP HERE FOR DIAGNOSTIC

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    load_data_debug()

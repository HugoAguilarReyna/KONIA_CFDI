import pandas as pd
import os
from dotenv import load_dotenv
import sys

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

try:
    from matriz_resumen_module import load_dim_tiempo, get_fiscal_reports_data
    
    print("--- VERIFICATION START ---")
    
    # 1. Test load_dim_tiempo
    df_t = load_dim_tiempo()
    print(f"Dim Tiempo rows: {len(df_t)}")
    if not df_t.empty:
        print(f"Columns in dim_tiempo: {df_t.columns.tolist()}")
    
    # 2. Test get_fiscal_reports_data (which now includes the join)
    # The default company_id in matriz_resumen_module maps 'comp_default' to 2
    fiscal = get_fiscal_reports_data(2, 2026, 2)
    print(f"Fiscal data (joined) rows: {len(fiscal)}")
    
    if len(fiscal) > 0:
        first_doc = fiscal[0]
        # Check if dim_tiempo columns are present (e.g. nombre_mes_es)
        if 'nombre_mes_es' in first_doc:
            print(f"SUCCESS: 'nombre_mes_es' found in joined data: {first_doc['nombre_mes_es']}")
        else:
            print("WARNING: 'nombre_mes_es' NOT found in joined data.")
            print(f"Available keys: {list(first_doc.keys())}")
    else:
        print("No fiscal data found for company 2, Feb 2026.")

    print("--- VERIFICATION END ---")

except Exception as e:
    print(f"ERROR during verification: {e}")

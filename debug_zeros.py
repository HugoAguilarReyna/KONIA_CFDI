import pandas as pd
import os
from dotenv import load_dotenv
import sys

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

from matriz_resumen_module import get_fiscal_reports_data, process_fiscal_data, load_dim_tiempo

def debug():
    print("--- DEBUG START ---")
    company_id = 2
    year = 2026
    month = 1
    
    print(f"Fetching data for Co:{company_id}, Year:{year}, Month:{month}")
    
    # 1. Step by step fetch
    docs = get_fiscal_reports_data(company_id, year, month)
    print(f"1. get_fiscal_reports_data returned {len(docs)} docs")
    
    if len(docs) > 0:
        d = docs[0]
        print(f"   First doc keys: {list(d.keys())}")
        print(f"   First doc monto: {d.get('monto')} (Type: {type(d.get('monto'))})")
        print(f"   First doc periodo: {d.get('periodo')}")
        
        # 2. Process data
        processed = process_fiscal_data(docs)
        print(f"2. process_fiscal_data returned {len(processed)} items")
        
        if len(processed) > 0:
            p = processed[0]
            print(f"   First processed keys: {list(p.keys())}")
            print(f"   First processed monto: {p.get('monto')} (Type: {type(p.get('monto'))})")
            print(f"   First processed concepto: {p.get('concepto')}")
            
            total_monto = sum(item['monto'] for item in processed)
            print(f"3. Total monto processed: {total_monto}")
            
            if total_monto == 0:
                print("!!! DATA IS ZERO !!!")
            else:
                print("Data is NOT zero in Python. Issue might be in React or JSON injection.")
        else:
            print("!!! PROCESSED LIST IS EMPTY !!!")
    else:
        print("!!! NO DOCUMENTS RETURNED !!!")

    print("--- DEBUG END ---")

if __name__ == "__main__":
    debug()

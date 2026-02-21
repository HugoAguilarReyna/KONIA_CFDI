from datetime import datetime
import pandas as pd
from typing import List, Dict, Any, Optional
from ..core.database import get_database

class FiscalService:
    def __init__(self):
        self.db = get_database()
        self.collection_name = "matriz_resumen"

    def _load_dim_tiempo(self) -> pd.DataFrame:
        """Fetches the time dimension table from MongoDB."""
        try:
            col = self.db["dim_tiempo"]
            docs = list(col.find({}, {"_id": 0}))
            if docs:
                df_tiempo = pd.DataFrame(docs)
                # Ensure proper types for merging
                if 'periodo' in df_tiempo.columns:
                    df_tiempo['periodo'] = df_tiempo['periodo'].astype(str)
                return df_tiempo
            return pd.DataFrame()
        except Exception as e:
            print(f"Error loading dim_tiempo: {e}")
            return pd.DataFrame()

    def get_fiscal_reports(self, company_id: str, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetches pre-aggregated data from fiscal_reports.matriz_resumen and joins with dim_tiempo.
        Adapted from matriz_resumen_module.py
        """
        try:
            # Mapping logic (simplified for API)
            # In existing code: company_map = {"TENANT_001": 2, "comp_default": 2}
            # We will assume company_id is passed correctly or handle mapping here if strict compatibility is needed
            # For now, let's keep it direct, or map if we know the ID scheme.
            
            # Converting string ID to int if the DB expects int (based on observed code)
            cid = 2 
            if company_id == "TENANT_001":
                cid = 2
            elif company_id.isdigit():
                cid = int(company_id)
            
            col = self.db[self.collection_name]
            
            query = {"company_id": cid}
            
            if year:
                if month and month > 0:
                     query["periodo"] = f"{year}-{month:02d}"
                else:
                    query["periodo"] = {"$regex": f"^{year}-"}
            
            docs = list(col.find(query, {"_id": 0}))
            
            if not docs:
                return {
                    "kpis": {"income": 0, "expense": 0, "net": 0, "count": 0},
                    "chart_data": [],
                    "details": []
                }
            
            df_fiscal = pd.DataFrame(docs)
            df_tiempo = self._load_dim_tiempo()
            
            if not df_tiempo.empty and 'periodo' in df_fiscal.columns:
                df_fiscal = df_fiscal.merge(df_tiempo, on='periodo', how='left')
                
            # Process data (Simulating process_fiscal_data)
            # Fill NaNs to avoid JSON serialization errors
            df_fiscal = df_fiscal.fillna("")
            
            # --- AGGREGATION LOGIC ---
            # 1. Total KPIs
            income = 0.0
            expense = 0.0
            
            if 'total' in df_fiscal.columns and 'tipo_comprobante' in df_fiscal.columns:
                 # Ensure total is numeric
                 df_fiscal['total'] = pd.to_numeric(df_fiscal['total'], errors='coerce').fillna(0)
                 
                 # Normalize type to first letter upper case to handle 'Ingreso'/'I', 'Egreso'/'E'
                 # Create a temporary column for calculation
                 df_fiscal['tipo_normalized'] = df_fiscal['tipo_comprobante'].astype(str).str[0].str.upper()
                 
                 income = df_fiscal[df_fiscal['tipo_normalized'] == 'I']['total'].sum()
                 expense = df_fiscal[df_fiscal['tipo_normalized'] == 'E']['total'].sum()
            
            kpis = {
                "income": float(income),
                "expense": float(expense),
                "net": float(income - expense),
                "count": int(len(df_fiscal))
            }
            
            # 2. Chart Data (Daily Aggregation)
            chart_data = []
            if 'fecha' in df_fiscal.columns and not df_fiscal.empty:
                 df_fiscal['dt'] = pd.to_datetime(df_fiscal['fecha'], errors='coerce')
                 df_chart = df_fiscal.dropna(subset=['dt'])
                 if not df_chart.empty:
                     # Group by day and type
                     daily = df_chart.groupby([df_chart['dt'].dt.date, 'tipo_comprobante'])['total'].sum().unstack(fill_value=0).reset_index()
                     
                     # Format for frontend
                     for _, row in daily.iterrows():
                         chart_data.append({
                             "date": str(row['dt']),
                             "income": float(row.get('I', 0)),
                             "expense": float(row.get('E', 0))
                         })
                         
            return {
                "kpis": kpis,
                "chart_data": chart_data,
                "details": df_fiscal.to_dict('records')
            }
            
        except Exception as e:
            print(f"Error in get_fiscal_reports: {e}")
            return {
                "kpis": {"income": 0, "expense": 0, "net": 0, "count": 0},
                "chart_data": [],
                "details": []
            }

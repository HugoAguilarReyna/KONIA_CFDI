from datetime import datetime
import pandas as pd
from typing import Dict, Any, List, Optional
from ..core.database import get_database

class RiskService:
    def __init__(self):
        self.db = get_database()
        self.collection_name = "gold_cfdi" # Assuming master data is here

    def analyze_invoice_risk(self, invoice_uuid: str) -> Dict[str, Any]:
        """
        Calculates forensic risk indicators including Issuer Risk Score.
        Adapted from audit_module.py
        """
        try:
            col = self.db[self.collection_name]
            
            # Fetch target invoice
            target = col.find_one({"uuid": invoice_uuid}, {"_id": 0})
            if not target:
                return {"error": "Invoice not found"}
            
            emisor_rfc = target.get("emisor_rfc")
            
            # Fetch context (all invoices from same issuer) for statistical deviation
            # In a real heavy production app, this should be pre-calculated or aggregated
            # For migration fidelity, we replicate the logic of fetching 'df_master' for the specific issuer
            context_docs = list(col.find({"emisor_rfc": emisor_rfc}, {"total": 1, "fecha": 1, "_id": 0}))
            df_context = pd.DataFrame(context_docs)
            
            return self._calculate_risk_metrics(target, df_context)

        except Exception as e:
            return {"error": str(e)}

    def _calculate_risk_metrics(self, row: Dict, df_context: pd.DataFrame) -> Dict[str, Any]:
        total = row.get('total', 0)
        # Handle date parsing
        fecha_str = row.get('fecha')
        fecha = None
        if isinstance(fecha_str, datetime):
            fecha = fecha_str
        elif fecha_str:
            try:
                fecha = datetime.fromisoformat(str(fecha_str).replace('Z', ''))
            except:
                pass
        
        # 1. Round Number Check
        is_round = (total > 0) and (total % 100 == 0 or total % 1000 == 0)
        
        # 2. Unusual Hour Check (10 PM - 6 AM)
        is_atypical_hour = False
        if fecha:
            is_atypical_hour = fecha.hour >= 22 or fecha.hour <= 6
            
        # 3. Weekend Check
        is_weekend = False
        if fecha:
            is_weekend = fecha.weekday() >= 5 # 5=Saturday, 6=Sunday
            
        # 4. Statistical Deviation (vs Emisor Mean)
        is_anomaly = False
        emisor_avg = 0
        if not df_context.empty:
            emisor_avg = df_context['total'].mean()
            if emisor_avg > 0:
                is_anomaly = total > (emisor_avg * 2.5)
        
        # 5. Calculate Issuer Risk Score (Global context)
        issuer_score = 0
        if not df_context.empty:
             # Ensure date column is datetime
             if 'fecha' in df_context.columns:
                 # Attempt to convert to datetime, coercing errors
                 df_context['dt'] = pd.to_datetime(df_context['fecha'], errors='coerce')
                 
                 total_count = len(df_context)
                 if total_count > 0:
                     round_pct = (df_context['total'].apply(lambda x: x > 0 and x % 100 == 0).sum() / total_count) * 100
                     
                     # Check hours
                     atypical_pct = 0
                     weekend_pct = 0
                     valid_dates = df_context['dt'].dropna()
                     if not valid_dates.empty:
                         atypical_pct = (valid_dates.dt.hour >= 22).sum() / total_count * 100
                         weekend_pct = (valid_dates.dt.dayofweek >= 5).sum() / total_count * 100
                     
                     issuer_score = (round_pct * 0.4 + atypical_pct * 0.3 + weekend_pct * 0.3)

        return {
            "uuid": row.get('uuid'),
            "risk_score": round(issuer_score, 1),
            "flags": {
                "round_number": is_round,
                "atypical_hour": is_atypical_hour,
                "weekend_billing": is_weekend,
                "mean_deviation": is_anomaly
            },
            "metrics": {
                 "total": total,
                 "emisor_avg": round(emisor_avg, 2)
            }
        }

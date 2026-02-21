from datetime import datetime, timedelta
import sys
import os
from typing import Dict, Any, List, Optional
import pandas as pd

# Add parent directory to sys.path to import original modules
# Assuming konia-react-migration/backend/app/services is the current location
# We need to reach d:\antigravity\Dashboard_Leopoldo\pm_dashb-main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

try:
    import trazabilidad_module
    print("Successfully imported trazabilidad_module")
except ImportError as e:
    print(f"Error importing trazabilidad_module: {e}")
    # Fallback or mock for development if module structure is different
    trazabilidad_module = None

from ..core.database import get_database

class TrazabilidadService:
    def __init__(self):
        self.db = get_database()
    
    async def get_details(self, uuid: str):
        """
        Wraps the logic to fetch traceability details for a specific UUID.
        This service adapts raw database queries into a structured response 
        suitable for the new React frontend, independent of legacy session logic.
        
        Analyzing trazabilidad_module.py (from context), it likely has functions 
        to query 'gold_cfdi'.
        """
        collection = self.db["gold_cfdi"]
        
        # 1. Fetch the main UUID
        main_doc = collection.find_one({"uuid": uuid}, {"_id": 0})
        if not main_doc:
            return None
            
        # 2. Traceability Logic (Simplified/Adapted from original)
        # Check if it has 'complemento_pago_uuids' or related documents
        related_docs = []
        
        # Example logic: Find children (Pagos)
        children = list(collection.find({
            "relacionados_padre.uuid": uuid
        }, {"_id": 0, "uuid": 1, "tipo_comprobante": 1, "total": 1, "fecha": 1}))
        
        # Example logic: Find parent (if this is a payment or note)
        parents = []
        if "relacionados_padre" in main_doc and isinstance(main_doc["relacionados_padre"], list):
            for rel in main_doc["relacionados_padre"]:
                 if 'uuid' in rel:
                     parent_doc = collection.find_one({"uuid": rel['uuid']}, {"_id": 0, "uuid": 1, "tipo_comprobante": 1, "total": 1})
                     if parent_doc:
                         parents.append(parent_doc)

        return {
            "node": main_doc,
            "parents": parents,
            "children": children,
            "timeline": self._build_timeline(main_doc, parents, children)
        }

    def _build_timeline(self, main, parents, children):
        events = []
        # Add main event
        events.append({
            "date": main.get("fecha"),
            "type": main.get("tipo_comprobante"),
            "uuid": main.get("uuid"),
            "amount": main.get("total"),
            "status": "main"
        })
        
        for p in parents:
             events.append({
                "date": p.get("fecha"), # Might need fetching if not in projection
                "type": p.get("tipo_comprobante"),
                "uuid": p.get("uuid"),
                "amount": p.get("total"),
                "status": "parent"
            })
            
        for c in children:
            events.append({
                "date": c.get("fecha"),
                "type": c.get("tipo_comprobante"),
                "uuid": c.get("uuid"),
                "amount": c.get("total"),
                "status": "child"
            })
            
        # Sort by date
        # Helper to parse dates considering format variations
        def parse_date(d):
            if not d: return datetime.min
            if isinstance(d, datetime): return d
            try:
                return datetime.fromisoformat(str(d).replace('Z', '+00:00'))
            except:
                return datetime.min

        events.sort(key=lambda x: parse_date(x["date"]))
        return events

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from ..core.auth import decode_token
from ..core.database import get_database
from datetime import datetime
import re

router = APIRouter()

def safe_fecha(fecha_str):
    if not fecha_str or fecha_str == "NaT":
        return None
    try:
        return str(fecha_str)[:10]
    except:
        return None

# --- Dependency ---
async def get_current_user_and_company(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        # Fallback for Dev/Swagger
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
             token = auth_header.replace("Bearer ", "")
        else:
             raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        token = token.replace("Bearer ", "")
        
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    # Ensure company_id is present (it should be int from auth.py mapping)
    company_id = payload.get("company_id")
    if company_id is None:
         raise HTTPException(status_code=403, detail="Company ID missing in token")
         
    return payload

# --- Endpoints ---

@router.get("/matriz-resumen")
async def get_matriz_resumen(
    periodo: str = Query(..., description="Format YYYY-MM"),
    user: dict = Depends(get_current_user_and_company)
):
    db = get_database()
    # Switch to fiscal_reports database
    fiscal_db = db.client["fiscal_reports"]
    
    company_id = user["company_id"]
    
    # 1. Fetch Data
    cursor = fiscal_db["matriz_resumen"].find({
        "company_id": company_id,
        "periodo": periodo
    })
    docs = list(cursor)
    
    # 2. Process Data into Nested Structure
    # matriz[segmento][concepto] = monto
    matriz = {"PPD": {}, "PUE": {}}
    
    for doc in docs:
        seg = doc.get("segmento")
        con = doc.get("concepto")
        if seg in matriz:
            matriz[seg][con] = float(doc.get("monto", 0.0))

    # 3. Calculate Fiscal KPIs (Strict Logic)
    
    # Helpers
    def get_val(seg, con):
        return matriz.get(seg, {}).get(con, 0.0)

    # Base Values
    total_facturado_ppd = get_val("PPD", "1. (+) Total Facturado")
    total_facturado_pue = get_val("PUE", "1. (+) Total Facturado")
    
    saldo_insoluto_ppd = get_val("PPD", "9. (=) Saldo Insoluto PPD")
    saldo_teorico_pue  = get_val("PUE", "9. (=) Saldo Teórico PUE")
    
    notas_credito_ppd = get_val("PPD", "2. (-) Notas de Crédito (01)")
    notas_credito_pue = get_val("PUE", "2. (-) Notas de Crédito (01)")

    # KPI Formulas
    # INGRESOS: (PUE + PPD) -> Actually user said "Ingresos Totales" is sum of Total Facturado both.
    # User: "INGRESOS TOTALES: matriz['PPD']['Total Facturado'] + matriz['PUE']['Total Facturado']"
    ingresos_totales = total_facturado_ppd + total_facturado_pue
    
    # RATIO PPD/PUE: Saldo Insoluto PPD / Total Facturado PUE
    if total_facturado_pue != 0:
        ratio_ppd_pue = (saldo_insoluto_ppd / total_facturado_pue) * 100
    else:
        ratio_ppd_pue = 0.0
        
    # STATUS FISCAL: 
    # Risk = Saldo Insoluto PPD / Total Facturado PPD
    # If Total Facturado PPD > 0, else 0
    if total_facturado_ppd > 0:
        ratio_riesgo = abs(saldo_insoluto_ppd) / total_facturado_ppd
    else:
        ratio_riesgo = 0.0
        
    if ratio_riesgo <= 1.0:
        status = "SALUDABLE"
    elif ratio_riesgo <= 3.0:
        status = "EN RIESGO"
    else:
        status = "EN RIESGO CRÍTICO"

    return {
        "kpis": {
            "ingresos_totales": ingresos_totales,
            "saldo_ppd": saldo_insoluto_ppd,
            "ingreso_pue": total_facturado_pue, # User asked for "INGRESO PUE" based on Total Facturado PUE
            "creditos_nc": notas_credito_ppd + notas_credito_pue,
            "ratio_ppd_pue": ratio_ppd_pue,
            "ratio_riesgo": ratio_riesgo,
            "ratio_valor": ratio_riesgo, # Using ratio_riesgo as the base for the multiplier logic context
            "ratio_formato": f"{ratio_riesgo:.1f}x",
            "ratio_label": "Por cada $1 PUE",
            "status": status
        },
        "matriz": matriz, # Nested structure for frontend to parse
        "total_general": saldo_insoluto_ppd + saldo_teorico_pue,
        "subtotal_ppd": saldo_insoluto_ppd,
        "subtotal_pue": saldo_teorico_pue
    }

@router.get("/matriz-resumen/evolucion")
async def get_matriz_evolucion(
    user: dict = Depends(get_current_user_and_company)
):
    """Returns all historical periods for the company (needed for the Evolution chart)."""
    db = get_database()
    fiscal_db = db.client["fiscal_reports"]
    company_id = user["company_id"]
    
    # 1. Obtain ALL available periods for this company
    periodos_disponibles = fiscal_db["matriz_resumen"].distinct(
        "periodo",
        {"company_id": company_id}
    )
    periodos_disponibles.sort()  # chronological order "2025-10", "2025-11"...
    
    evolucion = []
    for p in periodos_disponibles:
        # Find concepts for this period
        cursor = fiscal_db["matriz_resumen"].find({
            "company_id": company_id,
            "periodo": p,
            "concepto": {"$in": ["9. (=) Saldo Insoluto PPD", "9. (=) Saldo Teórico PUE"]}
        })
        docs = list(cursor)
        
        saldo_ppd = 0.0
        saldo_pue = 0.0
        for doc in docs:
            if doc["segmento"] == "PPD":
                saldo_ppd = float(doc.get("monto", 0.0))
            elif doc["segmento"] == "PUE":
                saldo_pue = float(doc.get("monto", 0.0))
        
        evolucion.append({
            "periodo": p,
            "saldo_ppd": saldo_ppd,
            "saldo_pue": saldo_pue
        })
    
    return {"evolucion": evolucion}

@router.get("/matriz-resumen/tabla")
async def get_tabla_matriz(
    periodo: str, # "2026-02" - selected current month
    user: dict = Depends(get_current_user_and_company)
):
    """Calculates previous month automatically and returns comparative data."""
    db = get_database()
    fiscal_db = db.client["fiscal_reports"]
    company_id = user["company_id"]
    
    # 1. Calculate previous month natively
    try:
        año, mes = map(int, periodo.split("-"))
        if mes == 1:
            periodo_anterior = f"{año-1}-12"
        else:
            periodo_anterior = f"{año}-{mes-1:02d}"
    except Exception:
        periodo_anterior = None

    # 2. Query Current Month
    docs_actual = list(fiscal_db["matriz_resumen"].find({
        "company_id": company_id,
        "periodo": periodo
    }))
    
    # 3. Query Previous Month (if exists)
    docs_anterior = []
    if periodo_anterior:
        docs_anterior = list(fiscal_db["matriz_resumen"].find({
            "company_id": company_id,
            "periodo": periodo_anterior
        }))
    
    # 4. Organize in matrices
    def to_dict(docs):
        m = {"PPD": {}, "PUE": {}}
        for d in docs:
            seg = d.get("segmento")
            con = d.get("concepto")
            if seg in m:
                m[seg][con] = float(d.get("monto", 0.0))
        return m
    
        return m
    
    matriz_actual = to_dict(docs_actual)
    matriz_anterior = to_dict(docs_anterior) # Handles empty docs_anterior correctly

    # 5. Check Data Completeness (Audit)
    def check_completitud(docs):
        if not docs: return False
        conceptos_encontrados = {d.get("concepto") for d in docs}
        conceptos_esperados = {
            "1. (+) Total Facturado",
            "8. (-) Pagos Aplicados (08/09)",
            "9. (=) Saldo Insoluto PPD", # For PPD
            # "9. (=) Saldo Teórico PUE"  # For PUE - maybe too strict if one segment is empty?
        }
        # Relaxed check: at least Total Facturado should be present if there are docs
        return "1. (+) Total Facturado" in conceptos_encontrados

    advertencias = {
        "periodo_actual_completo": check_completitud(docs_actual),
        "periodo_anterior_completo": check_completitud(docs_anterior) if periodo_anterior else True
    }
    
    return {
        "periodo_actual": periodo,
        "periodo_anterior": periodo_anterior,
        "matriz_actual": matriz_actual,
        "matriz_anterior": matriz_anterior,
        "advertencias": advertencias
    }


@router.get("/detalle-uuid")
async def get_detalle_uuid(
    periodo: str = Query(...),
    page: int = 1,
    limit: int = 25,
    flujo: Optional[str] = None,
    segmento: Optional[str] = None,
    uuid_search: Optional[str] = None,
    saldo_min: Optional[float] = None,
    user: dict = Depends(get_current_user_and_company)
):
    db = get_database()
    fiscal_db = db.client["fiscal_reports"]
    
    company_id = user["company_id"]
    
    filtro = {"company_id": company_id, "periodo": periodo}
    if segmento and segmento != "TODOS": 
        filtro["segmento"] = segmento
    if flujo and flujo != "TODOS":    
        filtro["flujo"] = flujo
    if uuid_search:
        filtro["uuid"] = {"$regex": uuid_search, "$options":"i"}
    if saldo_min is not None:
        filtro["saldo_acumulado"] = {"$gte": saldo_min}

    total = fiscal_db["detalle_uuid"].count_documents(filtro)

    # Registros paginados con conceptos
    registros = list(fiscal_db["detalle_uuid"].find(
        filtro,
        {"_id":0, "uuid":1, "segmento":1, "flujo":1,
         "saldo_acumulado":1, "conceptos":1}
    ).sort("saldo_acumulado", -1)
     .skip((page-1)*limit)
     .limit(limit))

    # KPIs sin paginación
    pipeline_kpis = [
        {"$match": filtro},
        {"$group": {
            "_id": None,
            "saldo_total": {"$sum": "$saldo_acumulado"},
            "count": {"$sum": 1},
            "emitidos": {"$sum": {
                "$cond":[{"$eq":["$flujo","EMITIDOS"]},1,0]}},
            "recibidos": {"$sum": {
                "$cond":[{"$eq":["$flujo","RECIBIDOS"]},1,0]}}
        }}
    ]
    kpi_res = list(fiscal_db["detalle_uuid"].aggregate(pipeline_kpis))
    k = kpi_res[0] if kpi_res else {}

    saldo_total = k.get("saldo_total", 0)
    count = k.get("count", 1)
    emitidos = k.get("emitidos", 0)
    recibidos = k.get("recibidos", 0)
    ratio = (emitidos/recibidos*100) if recibidos > 0 else (100 if emitidos > 0 else 0)

    # Distribución por segmento
    pipeline_dist = [
        {"$match": filtro},
        {"$group": {"_id":"$segmento", "count":{"$sum":1}}}
    ]
    dist_raw = list(fiscal_db["detalle_uuid"].aggregate(pipeline_dist))
    distribucion = {d["_id"]: d["count"] for d in dist_raw}

    # Top 10 por saldo_acumulado
    top10 = list(fiscal_db["detalle_uuid"].find(
        filtro,
        {"_id":0, "uuid":1, "segmento":1, "saldo_acumulado":1}
    ).sort("saldo_acumulado", -1).limit(10))

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "registros": registros,
        "kpis": {
            "total_uuids": total,
            "saldo_total": saldo_total,
            "promedio_saldo": saldo_total / count if count else 0,
            "ratio_emit_recib": ratio
        },
        "distribucion": distribucion,
        "top10": top10
    }

@router.get("/test/trazabilidad")
def test_traz():
    db = get_database()
    pid = 2
    fiscal_db = db.client["fiscal_reports"]
    try:
        pipeline = [
            {"$match": {"company_id": pid}},
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
        uuids = list(fiscal_db["trazabilidad_uuid"].aggregate(pipeline))
        result = [{
            "uuid": u["_id"],
            "ultimo_saldo": float(u.get("ultimo_saldo") or 0.0),
            "total_eventos": u.get("total_eventos", 0),
            "primer_evento": safe_fecha(u.get("primer_evento")) or "—",
            "ultimo_evento": safe_fecha(u.get("ultimo_evento")) or "—",
            "total_monto": float(u.get("total_monto") or 0.0),
            "estado": "LIQUIDADO" if abs(float(u.get("ultimo_saldo") or 0.0)) < 0.01
                      else "INSOLUTO" if float(u.get("ultimo_saldo") or 0.0) > 0
                      else "SALDO_NEGATIVO"
        } for u in uuids]
        return {"success": True, "count": len(result)}
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}

@router.get("/test/trazabilidad/{uuid}")
def test_traz_single(uuid: str):
    db = get_database()
    pid = 2
    fiscal_db = db.client["fiscal_reports"]
    try:
        eventos = list(fiscal_db["trazabilidad_uuid"].find(
            {"company_id": pid, "uuid_raiz": uuid},
            {"_id": 0}
        ).sort("fecha", 1))

        if not eventos:
            return {"success": False, "error": "No eventos"}

        primer = eventos[0]
        ultimo = eventos[-1]
        monto_original = float(eventos[0].get("monto", 0.0)) if eventos[0].get("concepto", "").startswith("1.") else 0.0
        saldo_final = float(ultimo.get("saldo_acumulado") or 0.0)
        total_pagos = sum(float(e.get("monto") or 0.0) for e in eventos
                          if e.get("tipo_relacion") == "PAGO")

        estado = ("LIQUIDADO" if abs(saldo_final) < 0.01
                  else "INSOLUTO" if saldo_final > 0
                  else "SALDO_NEGATIVO")

        return {
            "uuid_raiz": uuid,
            "eventos": len(eventos),
            "kpis": {
                "total_eventos": len(eventos),
                "saldo_final": saldo_final,
                "estado": estado
            }
        }
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}


@router.get("/trazabilidad/uuids")
async def get_trazabilidad_uuids(
    periodo: str = None,
    page: int = 1,
    limit: int = 50,
    user: dict = Depends(get_current_user_and_company)
):
    db = get_database().client["fiscal_reports"]
    
    company_id_raw = user["company_id"]
    try:
        company_id_int = int(company_id_raw)
        filtro_company = {"$in": [company_id_raw, company_id_int]}
    except (ValueError, TypeError):
        filtro_company = company_id_raw

    match_filter = {"company_id": filtro_company}
    if periodo:
        match_filter["periodo"] = periodo

    # 1. Agrupar por uuid_raiz para obtener resumen de cada cadena
    pipeline = [
        {"$match": match_filter},
        {"$group": {
            "_id": "$uuid_raiz",
            "ultimo_saldo": {"$sum": "$monto"},
            "total_eventos": {"$sum": 1},
            "primer_evento": {"$min": "$fecha"},
            "ultimo_evento": {"$max": "$fecha"},
            "total_monto": {"$sum": "$monto"},
            "periodos": {"$addToSet": "$periodo"},
            "tiene_pago": {
                "$max": {
                    "$cond": [
                        {"$in": ["$tipo_relacion", ["PAGO", "PAGO_REP"]]},
                        1, 0
                    ]
                }
            }
        }},
        {"$sort": {"ultimo_evento": -1}},
        {"$skip": (page - 1) * limit},
        {"$limit": limit}
    ]
    try:
        uuids = list(db["trazabilidad_uuid"].aggregate(pipeline, allowDiskUse=True))
        
        print(f"DEBUG UUIDS PIPELINE: company_id={company_id_raw} page={page} limit={limit} count={len(uuids)}")

        return [{
            "uuid": u["_id"],
            "ultimo_saldo": float(u.get("ultimo_saldo") or 0.0),
            "total_eventos": u.get("total_eventos", 0),
            "primer_evento": safe_fecha(u.get("primer_evento")) or "—",
            "ultimo_evento": safe_fecha(u.get("ultimo_evento")) or "—",
            "total_monto": float(u.get("total_monto") or 0.0),
            "estado": "LIQUIDADO" if abs(float(u.get("ultimo_saldo") or 0.0)) < 0.01 else ("NEGATIVO" if float(u.get("ultimo_saldo") or 0.0) <= -0.01 else "INSOLUTO"),
            "tiene_pago": bool(u.get("tiene_pago", 0)),
            "periodos": u.get("periodos", [])
        } for u in uuids]
    except Exception as e:
        import traceback
        print(f"ERROR TRAZABILIDAD: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trazabilidad/{uuid_raiz}")
async def get_trazabilidad_detalle(
    uuid_raiz: str,
    user: dict = Depends(get_current_user_and_company)
):
    db = get_database().client["fiscal_reports"]
    
    company_id_raw = user["company_id"]
    try:
        company_id_int = int(company_id_raw)
        filtro_company = {"$in": [company_id_raw, company_id_int]}
    except (ValueError, TypeError):
        filtro_company = company_id_raw

    # Búsqueda insensible a mayúsculas/minúsculas usando regex
    eventos = list(db["trazabilidad_uuid"].find(
        {
            "company_id": filtro_company, 
            "uuid_raiz": {"$regex": f"^{uuid_raiz}$", "$options": "i"}
        },
        {"_id": 0}
    ).sort("fecha", 1))

    if not eventos:
        print(f"DEBUG: UUID {uuid_raiz} not found in trazabilidad_uuid for company {company_id_raw}")
        raise HTTPException(status_code=404, detail=f"UUID no encontrado en el sistema de trazabilidad")

    primer = eventos[0]
    ultimo = eventos[-1]
    monto_original = float(eventos[0].get("monto", 0.0))
    saldo_final = float(ultimo.get("saldo_acumulado") or 0.0)
    
    # Calculate payments as the difference between original amount and final balance
    total_pagos = max(0.0, monto_original - saldo_final)

    estado = ("LIQUIDADO" if abs(saldo_final) < 0.01
              else "INSOLUTO" if saldo_final > 0
              else "SALDO_NEGATIVO")

    # Clean raw events before returning them as JSON to avoid missing keys causing issues in frontend
    for e in eventos:
        e["saldo_acumulado"] = float(e.get("saldo_acumulado") or 0.0)
        e["monto"] = float(e.get("monto") or 0.0)
        e["concepto"] = e.get("concepto", "")
        e["tipo_relacion"] = e.get("tipo_relacion", "")
        e["fecha"] = e.get("fecha", "")

    return {
        "uuid_raiz": uuid_raiz,
        "eventos": eventos,
        "kpis": {
            "total_eventos": len(eventos),
            "saldo_final": saldo_final,
            "primer_evento": primer.get("fecha"),
            "ultimo_evento": ultimo.get("fecha"),
            "monto_original": monto_original,
            "total_pagado": abs(total_pagos),
            "estado": estado,
            "pct_liquidado": (
                abs(total_pagos) / abs(monto_original) * 100
                if monto_original != 0 else 0
            )
        },
        "evolucion_saldo": [
            {"fecha": e.get("fecha", ""), "saldo": float(e.get("saldo_acumulado") or 0.0),
             "concepto": e.get("concepto", ""), "monto": float(e.get("monto") or 0.0)}
            for e in eventos
        ]
    }

@router.get("/dim-tiempo/{periodo}")
async def get_dim_tiempo(
    periodo: str,
    user: dict = Depends(get_current_user_and_company)
):
    db = get_database()
    fiscal_db = db.client["fiscal_reports"]
    
    doc = fiscal_db["dim_tiempo"].find_one({"periodo": periodo}, {"_id": 0})
    if not doc:
        # Return fallback if not found
        return {"periodo": periodo, "nombre_mes_es": periodo}
    return doc

@router.get("/riesgos/{uuid}")
async def get_risk_analysis(
    uuid: str,
    # Risk service likely uses 'cfdi_db' so standard get_database is fine inside wrapper
    current_user: dict = Depends(get_current_user_and_company) 
):
    from ..services.risk_wrapper import RiskService
    service = RiskService()
    data = service.analyze_invoice_risk(uuid)
    if "error" in data:
         if data["error"] == "Invoice not found":
             raise HTTPException(status_code=404, detail="Invoice not found")
         else:
             raise HTTPException(status_code=500, detail=data["error"])
    return data

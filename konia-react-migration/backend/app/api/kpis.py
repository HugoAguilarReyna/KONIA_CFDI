from fastapi import APIRouter, Depends
from ..core.database import get_database
from .dashboard import get_current_user_and_company

router = APIRouter()

@router.get("/periodos-disponibles")
async def get_periodos(user: dict = Depends(get_current_user_and_company)):
    company_id_raw = user["company_id"]
    try:
        company_id_int = int(company_id_raw)
        filtro_company = {"$in": [company_id_raw, company_id_int]}
    except (ValueError, TypeError):
        filtro_company = company_id_raw

    db = get_database().client["fiscal_reports"]
    periodos = db.detalle_uuid.distinct("periodo", {"company_id": filtro_company})
    periodos_ordenados = sorted(periodos, reverse=True)
    return {"periodos": periodos_ordenados}

@router.get("/resumen")
async def get_kpis_resumen(
    periodo: str,
    user: dict = Depends(get_current_user_and_company)
):
    company_id_raw = user["company_id"]
    try:
        company_id_int = int(company_id_raw)
        filtro_company = {"$in": [company_id_raw, company_id_int]}
    except (ValueError, TypeError):
        filtro_company = company_id_raw

    db = get_database().client["fiscal_reports"]
    filtro = {"company_id": filtro_company, "periodo": periodo}

    # ── BLOQUE 1: Salud de Cartera PPD ───────────────
    ppd_filter = {**filtro, "segmento": "PPD"}

    # Aging buckets
    aging = list(db.detalle_uuid.aggregate([
        {"$match": ppd_filter},
        {"$group": {
            "_id":   "$aging_bucket",
            "count": {"$sum": 1},
            "monto": {"$sum": "$saldo_acumulado"}
        }}
    ]))
    aging_map = {
        a["_id"]: {"count": a["count"], "monto": a["monto"]}
        for a in aging if a["_id"]
    }

    # PPD sin REP
    sin_rep = db.detalle_uuid.count_documents(
        {**ppd_filter, "tiene_rep": False, "flujo": "EMITIDOS"}
    )
    sin_rep_monto_agg = list(db.detalle_uuid.aggregate([
        {"$match": {**ppd_filter, "tiene_rep": False, "flujo": "EMITIDOS"}},
        {"$group": {"_id": None, "total": {"$sum": "$saldo_acumulado"}}}
    ]))
    sin_rep_monto = sin_rep_monto_agg[0]["total"] if sin_rep_monto_agg else 0

    # DSO promedio (solo PPD con dias_sin_pago)
    dso_res = list(db.detalle_uuid.aggregate([
        {"$match": {**ppd_filter, "dias_sin_pago": {"$ne": None}}},
        {"$group": {"_id": None, "dso_avg": {"$avg": "$dias_sin_pago"}}}
    ]))
    dso_avg = round(dso_res[0]["dso_avg"], 1) if dso_res else 0

    # Tasa de recuperación PPD
    total_ppd = db.detalle_uuid.count_documents(ppd_filter)
    total_con_rep = db.detalle_uuid.count_documents({**ppd_filter, "tiene_rep": True})
    tasa_recuperacion = round((total_con_rep / total_ppd * 100) if total_ppd else 0, 1)

    # ── BLOQUE 2: Eficiencia Documental ──────────────

    # UUIDs con NC > 30% del monto original
    nc_excesivas = list(db.detalle_uuid.aggregate([
        {"$match": filtro},
        {"$addFields": {
            "total_facturado": {"$ifNull": ["$conceptos.1. (+) Total Facturado", 0]},
            "notas_credito": {"$abs": {"$ifNull": ["$conceptos.2. (-) Notas de Crédito (01)", 0]}}
        }},
        {"$match": {
            "total_facturado": {"$gt": 0},
            "$expr": {
                "$gt": [
                    "$notas_credito",
                    {"$multiply": ["$total_facturado", 0.3]}
                ]
            }
        }},
        {"$count": "total"}
    ]))
    nc_excesivas_count = nc_excesivas[0]["total"] if nc_excesivas else 0

    # Ratio NC / Total Facturado global
    totales = list(db.detalle_uuid.aggregate([
        {"$match": filtro},
        {"$group": {
            "_id": None,
            "sum_facturado": {"$sum": "$conceptos.1. (+) Total Facturado"},
            "sum_nc": {"$sum": {"$abs": {"$ifNull": ["$conceptos.2. (-) Notas de Crédito (01)", 0]}}}
        }}
    ]))
    ratio_nc = 0
    if totales and totales[0].get("sum_facturado", 0):
        ratio_nc = round(totales[0]["sum_nc"] / totales[0]["sum_facturado"] * 100, 1)

    # Anticipos pendientes (concepto 7 != 0)
    anticipos_pendientes = list(db.detalle_uuid.aggregate([
        {"$match": filtro},
        {"$match": {"conceptos.7. (-) Anticipo (07)": {"$lt": 0}}},
        {"$group": {
            "_id": None,
            "count": {"$sum": 1},
            "monto": {"$sum": "$conceptos.7. (-) Anticipo (07)"}
        }}
    ]))
    anticipos = anticipos_pendientes[0] if anticipos_pendientes else {"count": 0, "monto": 0}

    # UUIDs segmento OTROS (sin clasificar)
    otros_count = db.detalle_uuid.count_documents({**filtro, "segmento": "OTROS"})
    otros_monto_agg = list(db.detalle_uuid.aggregate([
        {"$match": {**filtro, "segmento": "OTROS"}},
        {"$group": {"_id": None, "total": {"$sum": "$saldo_acumulado"}}}
    ]))
    otros_monto = otros_monto_agg[0]["total"] if otros_monto_agg else 0

    # ── BLOQUE 3: Riesgo Fiscal SAT ──────────────────

    # Top 5 concentración por RFC receptor (emitidos)
    top5_rfc = list(db.detalle_uuid.aggregate([
        {"$match": {**filtro, "flujo": "EMITIDOS", "rfc_receptor": {"$nin": [None, ""]}}},
        {"$group": {
            "_id": "$rfc_receptor",
            "nombre": {"$first": "$nombre_receptor"},
            "monto": {"$sum": "$saldo_acumulado"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"monto": -1}},
        {"$limit": 5}
    ]))

    # % concentrado en top 5
    total_emitido = list(db.detalle_uuid.aggregate([
        {"$match": {**filtro, "flujo": "EMITIDOS"}},
        {"$group": {"_id": None, "total": {"$sum": "$saldo_acumulado"}}}
    ]))
    total_emit = total_emitido[0]["total"] if total_emitido else 1
    top5_suma = sum(r["monto"] for r in top5_rfc)
    concentracion_pct = round(abs(top5_suma / total_emit * 100) if total_emit else 0, 1)

    # PPD emitidos sin REP después de 30 días
    ppd_criticos = db.detalle_uuid.count_documents({
        **filtro,
        "segmento": "PPD",
        "flujo": "EMITIDOS",
        "tiene_rep": False,
        "dias_sin_pago": {"$gt": 30}
    })
    ppd_criticos_monto_agg = list(db.detalle_uuid.aggregate([
        {"$match": {
            **filtro,
            "segmento": "PPD",
            "flujo": "EMITIDOS",
            "tiene_rep": False,
            "dias_sin_pago": {"$gt": 30}
        }},
        {"$group": {"_id": None, "total": {"$sum": "$saldo_acumulado"}}}
    ]))
    ppd_criticos_monto = ppd_criticos_monto_agg[0]["total"] if ppd_criticos_monto_agg else 0

    # ── BLOQUE 4: Inteligencia de UUIDs ──────────────

    # Top 10 UUIDs mayor impacto negativo
    top10_negativos = list(db.detalle_uuid.find(
        {**filtro, "saldo_acumulado": {"$lt": 0}},
        {"uuid": 1, "segmento": 1, "flujo": 1, "rfc_receptor": 1, "nombre_receptor": 1,
         "saldo_acumulado": 1, "tiene_rep": 1, "dias_sin_pago": 1, "_id": 0}
    ).sort("saldo_acumulado", 1).limit(10))

    # UUIDs con cadena larga (>3 eventos en trazabilidad)
    cadenas_largas = list(db.trazabilidad_uuid.aggregate([
        {"$match": filtro},
        {"$group": {"_id": "$uuid_raiz", "eventos": {"$sum": 1}}},
        {"$match": {"eventos": {"$gt": 3}}},
        {"$sort": {"eventos": -1}},
        {"$limit": 10}
    ]))

    # Distribución emitidos vs recibidos
    dist_flujo = list(db.detalle_uuid.aggregate([
        {"$match": filtro},
        {"$group": {
            "_id": "$flujo",
            "count": {"$sum": 1},
            "monto": {"$sum": "$saldo_acumulado"}
        }}
    ]))

    return {
        "periodo": periodo,
        "bloque1_cartera_ppd": {
            "aging_buckets": aging_map,
            "sin_rep_count": sin_rep,
            "sin_rep_monto": sin_rep_monto,
            "dso_promedio_dias": dso_avg,
            "tasa_recuperacion": tasa_recuperacion,
            "total_ppd": total_ppd,
            "total_con_rep": total_con_rep
        },
        "bloque2_eficiencia": {
            "nc_excesivas_count": nc_excesivas_count,
            "ratio_nc_pct": ratio_nc,
            "anticipos_pendientes": {
                "count": anticipos.get("count", 0),
                "monto": abs(anticipos.get("monto", 0))
            },
            "otros_sin_clasificar": {
                "count": otros_count,
                "monto": otros_monto
            }
        },
        "bloque3_riesgo_sat": {
            "top5_rfc": top5_rfc,
            "concentracion_pct": concentracion_pct,
            "ppd_criticos_count": ppd_criticos,
            "ppd_criticos_monto": ppd_criticos_monto
        },
        "bloque4_inteligencia": {
            "top10_negativos": top10_negativos,
            "cadenas_largas": cadenas_largas,
            "dist_flujo": dist_flujo
        }
    }

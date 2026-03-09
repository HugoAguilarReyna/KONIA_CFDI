from fastapi import APIRouter, Depends, Query
from ..core.database import get_database
from .dashboard import get_current_user_and_company
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _signed_saldo(field="$saldo_acumulado"):
    """Returns a $cond expression that negates saldo for RECIBIDOS (Egresos)."""
    return {
        "$cond": [
            {"$eq": ["$flujo", "RECIBIDOS"]},
            {"$multiply": [field, -1]},
            field
        ]
    }


def _company_filter(company_id_raw):
    try:
        company_id_int = int(company_id_raw)
        return {"$in": [company_id_raw, company_id_int]}
    except (ValueError, TypeError):
        return company_id_raw


def _build_base_filter(company_id_raw, periodo, tipo=None, metodo=None,
                        monto_min=None, monto_max=None):
    """Build the shared MongoDB filter from all query params."""
    filtro = {
        "company_id": _company_filter(company_id_raw),
        "periodo": periodo
    }

    if tipo:
        tipo_list = tipo[0].split(",") if isinstance(tipo[0], str) and "," in tipo[0] else tipo
        mapped_flujo = []
        for t in tipo_list:
            if t.lower() == "ingreso":
                mapped_flujo.append("EMITIDOS")
            if t.lower() == "egreso":
                mapped_flujo.append("RECIBIDOS")
        if mapped_flujo:
            filtro["flujo"] = {"$in": mapped_flujo}

    if metodo:
        metodo_list = metodo[0].split(",") if isinstance(metodo[0], str) and "," in metodo[0] else metodo
        mapped_metodo = [m.split(" ")[0] for m in metodo_list]
        filtro["segmento"] = {"$in": mapped_metodo}

    if monto_min is not None or monto_max is not None:
        expr_conditions = []
        if monto_min is not None:
            expr_conditions.append({
                "$gte": [_signed_saldo(), monto_min]
            })
        if monto_max is not None:
            expr_conditions.append({
                "$lte": [_signed_saldo(), monto_max]
            })
        filtro["$expr"] = expr_conditions[0] if len(expr_conditions) == 1 else {"$and": expr_conditions}

    return filtro


# ─────────────────────────────────────────────────────────────────────────────
#  GET /periodos-disponibles
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/periodos-disponibles")
async def get_periodos(user: dict = Depends(get_current_user_and_company)):
    company_id_raw = user["company_id"]
    db = get_database().client["fiscal_reports"]
    filtro_company = _company_filter(company_id_raw)

    periodos = db.detalle_uuid.distinct("periodo", {"company_id": filtro_company})
    return {"periodos": sorted(periodos, reverse=True)}


# ─────────────────────────────────────────────────────────────────────────────
#  GET /resumen  — full fiscal KPIs
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/resumen")
async def get_kpis_resumen(
    periodo: str,
    tipo: list[str] = Query(None),
    metodo: list[str] = Query(None),
    monto_min: float = Query(None),
    monto_max: float = Query(None),
    user: dict = Depends(get_current_user_and_company)
):
    company_id_raw = user["company_id"]
    db = get_database().client["fiscal_reports"]

    filtro = _build_base_filter(company_id_raw, periodo, tipo, metodo, monto_min, monto_max)
    filtro_company = _company_filter(company_id_raw)

    print("KPIs FILTRO:", filtro)

    # ── PPD-only sub-filter ───────────────────────────────────────────────────
    ppd_filter = {k: v for k, v in filtro.items()}
    if "segmento" in ppd_filter:
        seg_val = ppd_filter["segmento"]
        ppds_in = seg_val.get("$in", []) if isinstance(seg_val, dict) else []
        ppd_filter["segmento"] = "PPD" if (not ppds_in or "PPD" in ppds_in) else "NONE_MATCHED"
    else:
        ppd_filter["segmento"] = "PPD"

    # ══════════════════════════════════════════════════════════════════════
    #  BLOQUE 1 — Salud de Cartera PPD
    # ══════════════════════════════════════════════════════════════════════

    # Aging buckets (array shape for the frontend)
    AGING_ORDER = ["0-30 días", "31-60 días", "61-90 días", "+90 días"]
    aging_raw = list(db.detalle_uuid.aggregate([
        {"$match": ppd_filter},
        {"$group": {
            "_id":   "$aging_bucket",
            "count": {"$sum": 1},
            "monto": {"$sum": _signed_saldo()}
        }}
    ]))
    aging_map = {a["_id"]: {"uuids": a["count"], "monto": a["monto"]} for a in aging_raw if a["_id"]}
    total_aging = sum(v["uuids"] for v in aging_map.values()) or 1
    aging_list = [
        {
            "rango": rango,
            "uuids": aging_map.get(rango, {}).get("uuids", 0),
            "monto": aging_map.get(rango, {}).get("monto", 0),
            "pct":   round(aging_map.get(rango, {}).get("uuids", 0) / total_aging * 100, 1)
        }
        for rango in AGING_ORDER
    ]

    # PPD sin REP
    sin_rep_count = db.detalle_uuid.count_documents(
        {**ppd_filter, "tiene_rep": False, "flujo": "EMITIDOS"}
    )
    sin_rep_monto_agg = list(db.detalle_uuid.aggregate([
        {"$match": {**ppd_filter, "tiene_rep": False, "flujo": "EMITIDOS"}},
        {"$group": {"_id": None, "total": {"$sum": "$saldo_acumulado"}}}
    ]))
    sin_rep_monto = sin_rep_monto_agg[0]["total"] if sin_rep_monto_agg else 0

    # DSO
    dso_res = list(db.detalle_uuid.aggregate([
        {"$match": {**ppd_filter, "dias_sin_pago": {"$ne": None}}},
        {"$group": {"_id": None, "dso_avg": {"$avg": "$dias_sin_pago"}}}
    ]))
    dso_avg = round(dso_res[0]["dso_avg"], 1) if dso_res else 0

    # Tasa recuperación
    total_ppd = db.detalle_uuid.count_documents(ppd_filter)
    total_con_rep = db.detalle_uuid.count_documents({**ppd_filter, "tiene_rep": True})
    recuperacion_pct = round((total_con_rep / total_ppd * 100) if total_ppd else 0, 1)

    # Eficiencia < 30 días (PPD con REP dentro de 30d)
    con_rep_30d = db.detalle_uuid.count_documents({
        **ppd_filter, "tiene_rep": True, "dias_sin_pago": {"$lte": 30}
    })
    eficiencia_recuperacion = round((con_rep_30d / total_ppd * 100) if total_ppd else 0, 1)

    # Total CFDIs del período (all, then by flujo)
    total_uuids = db.detalle_uuid.count_documents(filtro)
    total_emitidos = db.detalle_uuid.count_documents({**filtro, "flujo": "EMITIDOS"})
    total_recibidos = db.detalle_uuid.count_documents({**filtro, "flujo": "RECIBIDOS"})

    # ══════════════════════════════════════════════════════════════════════
    #  BLOQUE 2 — Eficiencia Documental
    # ══════════════════════════════════════════════════════════════════════

    # NC excesivas (> 30% del monto)
    nc_excesivas_agg = list(db.detalle_uuid.aggregate([
        {"$match": filtro},
        {"$addFields": {
            "total_facturado": {"$ifNull": ["$conceptos.1. (+) Total Facturado", 0]},
            "notas_credito":   {"$abs": {"$ifNull": ["$conceptos.2. (-) Notas de Crédito (01)", 0]}}
        }},
        {"$match": {
            "total_facturado": {"$gt": 0},
            "$expr": {"$gt": ["$notas_credito", {"$multiply": ["$total_facturado", 0.3]}]}
        }},
        {"$count": "total"}
    ]))
    nc_excesivas_count = nc_excesivas_agg[0]["total"] if nc_excesivas_agg else 0

    # Ratio NC / Facturado
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

    # Anticipos pendientes
    anticipos_agg = list(db.detalle_uuid.aggregate([
        {"$match": filtro},
        {"$match": {"conceptos.7. (-) Anticipo (07)": {"$lt": 0}}},
        {"$group": {"_id": None, "count": {"$sum": 1}, "monto": {"$sum": "$conceptos.7. (-) Anticipo (07)"}}}
    ]))
    anticipos = anticipos_agg[0] if anticipos_agg else {"count": 0, "monto": 0}

    # OTROS sin clasificar
    otros_count = db.detalle_uuid.count_documents({**filtro, "segmento": "OTROS"})
    otros_monto_agg = list(db.detalle_uuid.aggregate([
        {"$match": {**filtro, "segmento": "OTROS"}},
        {"$group": {"_id": None, "total": {"$sum": _signed_saldo()}}}
    ]))
    otros_monto = otros_monto_agg[0]["total"] if otros_monto_agg else 0

    # Deducibilidad — % de CFDIs que tienen todos los campos SAT requeridos
    # Proxy: tiene UUID, rfc_receptor, tiene_rep o es PUE (no necesita REP)
    deducibles = db.detalle_uuid.count_documents({
        **filtro,
        "uuid": {"$nin": [None, ""]},
        "rfc_receptor": {"$nin": [None, ""]},
        "$or": [
            {"segmento": "PUE"},
            {"segmento": "PPD", "tiene_rep": True}
        ]
    })
    deducibilidad_pct = round((deducibles / total_uuids * 100) if total_uuids else 0, 1)

    # CFDIs cancelados
    cancelados = db.detalle_uuid.count_documents({**filtro, "estado": "CANCELADO"})
    tasa_cancelacion = round((cancelados / total_uuids * 100) if total_uuids else 0, 1)

    # ══════════════════════════════════════════════════════════════════════
    #  BLOQUE 3 — Riesgo Fiscal SAT
    # ══════════════════════════════════════════════════════════════════════

    # Concentración top 5 RFC receptor
    top5_rfc = list(db.detalle_uuid.aggregate([
        {"$match": {**filtro, "flujo": "EMITIDOS", "rfc_receptor": {"$nin": [None, ""]}}},
        {"$group": {
            "_id":    "$rfc_receptor",
            "nombre": {"$first": "$nombre_receptor"},
            "monto":  {"$sum": "$saldo_acumulado"},
            "count":  {"$sum": 1}
        }},
        {"$sort": {"monto": -1}},
        {"$limit": 5}
    ]))

    total_emitido_agg = list(db.detalle_uuid.aggregate([
        {"$match": {**filtro, "flujo": "EMITIDOS"}},
        {"$group": {"_id": None, "total": {"$sum": "$saldo_acumulado"}}}
    ]))
    total_emit_monto = total_emitido_agg[0]["total"] if total_emitido_agg else 1
    top5_suma = sum(r["monto"] for r in top5_rfc)
    concentracion_pct = round(abs(top5_suma / total_emit_monto * 100) if total_emit_monto else 0, 1)
    indice_concentracion = concentracion_pct  # same metric, exposed separately for the gauge

    # PPD críticos (sin REP, >30 días)
    ppd_criticos = db.detalle_uuid.count_documents({
        **filtro, "segmento": "PPD", "flujo": "EMITIDOS",
        "tiene_rep": False, "dias_sin_pago": {"$gt": 30}
    })
    ppd_criticos_monto_agg = list(db.detalle_uuid.aggregate([
        {"$match": {**filtro, "segmento": "PPD", "flujo": "EMITIDOS",
                   "tiene_rep": False, "dias_sin_pago": {"$gt": 30}}},
        {"$group": {"_id": None, "total": {"$sum": "$saldo_acumulado"}}}
    ]))
    ppd_criticos_monto = ppd_criticos_monto_agg[0]["total"] if ppd_criticos_monto_agg else 0

    # Discrepancia fiscal: % de CFDIs sin clasificar (segmento OTROS) vs total
    discrepancia_pct = round((otros_count / total_uuids * 100) if total_uuids else 0, 1)

    # Días próximos a vencer REP (PPD emitidos sin REP con dias_sin_pago entre 25-30)
    dias_prox_vencer_agg = list(db.detalle_uuid.aggregate([
        {"$match": {
            **ppd_filter,
            "flujo": "EMITIDOS",
            "tiene_rep": False,
            "dias_sin_pago": {"$gte": 25, "$lte": 30}
        }},
        {"$group": {"_id": None, "min_dias": {"$min": "$dias_sin_pago"}}}
    ]))
    dias_prox_vencer = 0
    if dias_prox_vencer_agg:
        dias_activos = dias_prox_vencer_agg[0].get("min_dias", 0) or 0
        dias_prox_vencer = max(0, 30 - dias_activos)

    # ══════════════════════════════════════════════════════════════════════
    #  BLOQUE 4 — Inteligencia de UUIDs
    # ══════════════════════════════════════════════════════════════════════

    # Top 10 negativos
    top10_negativos = list(db.detalle_uuid.aggregate([
        {"$match": filtro},
        {"$addFields": {"saldo_signo": _signed_saldo()}},
        {"$match": {"saldo_signo": {"$lt": 0}}},
        {"$sort": {"saldo_signo": 1}},
        {"$limit": 10},
        {"$project": {
            "uuid": 1, "segmento": 1, "flujo": 1,
            "rfc_receptor": 1, "nombre_receptor": 1,
            "monto": "$saldo_signo",
            "tiene_rep": 1, "dias_sin_pago": 1, "_id": 0
        }}
    ]))
    # Normalise field names for the frontend
    top10_negativos = [
        {
            "uuid":      t.get("uuid", ""),
            "tipo":      t.get("segmento", "PPD"),
            "sinRep":    not t.get("tiene_rep", True),
            "monto":     t.get("monto", 0),
            "rfc":       t.get("rfc_receptor", ""),
            "nombre":    t.get("nombre_receptor", ""),
        }
        for t in top10_negativos
    ]

    # Cadenas de mayor complejidad
    cadenas_largas_raw = list(db.trazabilidad_uuid.aggregate([
        {"$match": filtro},
        {"$group": {"_id": "$uuid_raiz", "eventos": {"$sum": 1}}},
        {"$match": {"eventos": {"$gt": 3}}},
        {"$sort": {"eventos": -1}},
        {"$limit": 10}
    ]))
    cadenas_largas = [{"uuid": c["_id"], "eventos": c["eventos"]} for c in cadenas_largas_raw]

    # Distribución emitidos / recibidos
    dist_flujo_raw = list(db.detalle_uuid.aggregate([
        {"$match": filtro},
        {"$group": {
            "_id":   "$flujo",
            "count": {"$sum": 1},
            "monto": {"$sum": "$saldo_acumulado"}
        }}
    ]))
    dist_map = {d["_id"]: {"count": d["count"], "monto": d["monto"]} for d in dist_flujo_raw}
    emit_n = dist_map.get("EMITIDOS", {}).get("count", 0)
    recv_n = dist_map.get("RECIBIDOS", {}).get("count", 0)
    emit_m = dist_map.get("EMITIDOS", {}).get("monto", 0)
    recv_m = dist_map.get("RECIBIDOS", {}).get("monto", 0)
    total_n_dist = (emit_n + recv_n) or 1
    dist_flujo_obj = {
        "emitidos_n":     emit_n,
        "recibidos_n":    recv_n,
        "emitidos_pct":   round(emit_n / total_n_dist * 100, 1),
        "recibidos_pct":  round(recv_n / total_n_dist * 100, 1),
        "emitidos_monto": emit_m,
        "recibidos_monto": -abs(recv_m),  # always show as negative
    }

    # Saldo neto = emitidos - |recibidos|
    saldo_total = emit_m - abs(recv_m)

    # ══════════════════════════════════════════════════════════════════════
    #  BLOQUE 5 — Evolución histórica (últimos 6 periodos)
    # ══════════════════════════════════════════════════════════════════════
    try:
        year, month = int(periodo.split("-")[0]), int(periodo.split("-")[1])
    except Exception:
        year, month = datetime.now().year, datetime.now().month

    evolucion = []
    for i in range(5, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        p = f"{y}-{str(m).padStart(2,'0')}" if False else f"{y}-{str(m).zfill(2)}"
        hist_emit = db.detalle_uuid.count_documents({"company_id": filtro_company, "periodo": p, "flujo": "EMITIDOS"})
        hist_recv = db.detalle_uuid.count_documents({"company_id": filtro_company, "periodo": p, "flujo": "RECIBIDOS"})
        saldo_ppd_agg = list(db.detalle_uuid.aggregate([
            {"$match": {"company_id": filtro_company, "periodo": p, "segmento": "PPD"}},
            {"$group": {"_id": None, "total": {"$sum": _signed_saldo()}}}
        ]))
        saldo_pue_agg = list(db.detalle_uuid.aggregate([
            {"$match": {"company_id": filtro_company, "periodo": p, "segmento": "PUE"}},
            {"$group": {"_id": None, "total": {"$sum": _signed_saldo()}}}
        ]))
        evolucion.append({
            "periodo":   p,
            "emitidos":  hist_emit,
            "recibidos": hist_recv,
            "saldoPPD":  saldo_ppd_agg[0]["total"] if saldo_ppd_agg else 0,
            "saldoPUE":  saldo_pue_agg[0]["total"] if saldo_pue_agg else 0,
        })

    # ══════════════════════════════════════════════════════════════════════
    #  RESPONSE — keys aligned with KPIsTab.jsx mapping
    # ══════════════════════════════════════════════════════════════════════
    return {
        "periodo": periodo,

        # Global
        "total_uuids":    total_uuids,
        "saldo_total":    saldo_total,

        # New fiscal indicators
        "tasa_cancelacion":      tasa_cancelacion,
        "cfdi_cancelados":       cancelados,
        "eficiencia_recuperacion": eficiencia_recuperacion,
        "dias_prox_vencer":      dias_prox_vencer,
        "deducibilidad_pct":     deducibilidad_pct,
        "discrepancia_pct":      discrepancia_pct,

        # Historical evolution (for the chart)
        "evolucion": evolucion,

        # Bloque 1 — Salud de Cartera PPD
        "bloque1_cartera": {
            "total_uuids":      total_ppd,
            "dso":              dso_avg,
            "sin_rep_count":    sin_rep_count,
            "sin_rep_monto":    sin_rep_monto,
            "recuperacion_pct": recuperacion_pct,
            "aging":            aging_list,
        },

        # Bloque 2 — Eficiencia Documental
        "bloque2_eficiencia": {
            "total_uuids":      total_uuids,
            "nc_excesivas":     nc_excesivas_count,
            "ratio_nc":         ratio_nc,
            "anticipos_n":      anticipos.get("count", 0),
            "anticipos_monto":  abs(anticipos.get("monto", 0)),
            "otros_sin_class":  otros_count,
            "otros_monto":      otros_monto,
        },

        # Bloque 3 — Riesgo Fiscal SAT
        "bloque3_riesgo": {
            "top5_rfc":             top5_rfc,
            "concentracion_pct":    concentracion_pct,
            "indice_concentracion": indice_concentracion,
            "ppd_criticos_count":   ppd_criticos,
            "ppd_criticos_monto":   ppd_criticos_monto,
        },

        # Bloque 4 — Inteligencia UUID
        "bloque4_inteligencia": {
            "dist_flujo":    dist_flujo_obj,
            "cadenas_largas": cadenas_largas,
        },

        # Top 10 at root for easy access
        "top10_negativos": top10_negativos,
    }

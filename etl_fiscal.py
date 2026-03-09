"""
etl_fiscal.py  —  Versión con fix de rfc_emisor/nombre_emisor en pagos PPD
============================================================================
FIX aplicado:  Cuando los pagos (pagos_detalle) corresponden a facturas de
períodos anteriores, el LEFT JOIN a c_padre en pagos_reps puede devolver
null.  Se agregó:
  1. Una consulta adicional `uuids_info` que busca directamente en BigQuery
     el emisor/receptor de cualquier UUID referenciado en pagos que no esté
     ya en el df del período actual.
  2. Un paso post-concat que rellena los nulls desde esa tabla de lookup.
"""

import pandas as pd
from google.cloud import bigquery
from pymongo import MongoClient, errors, UpdateOne, InsertOne
import warnings
from datetime import datetime
import time
import numpy as np

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.display.float_format = '{:,.2f}'.format

CONFIG = {
    "project_id": "csreporter-iso27001",
    "dataset_id": "csmonitor",
    "company_id": 2,
    "rfc_empresa": "DGN811026BU6",
    "mongo_uri": "mongodb+srv://aguilarhugo55_db_user:c5mfG11QT68ib4my@clusteract1.kpdhd5e.mongodb.net/fiscal_reports?authSource=admin&appName=ClusterAct1",
    "mongo_db": "fiscal_reports",
    "col_matriz": "matriz_resumen",
    "col_detalle": "detalle_uuid",
    "col_trazabilidad": "trazabilidad_uuid"
}

try:
    bq_client = bigquery.Client(project=CONFIG["project_id"])
    print(f"✅ Conectado a BigQuery: {CONFIG['project_id']}")
except Exception as e:
    print(f"⚠️ Error BigQuery: {e}")
    exit(1)

try:
    mongo_client = MongoClient(CONFIG["mongo_uri"])
    db = mongo_client[CONFIG["mongo_db"]]
    print(f"✅ Conectado a MongoDB")
except Exception as e:
    print(f"⚠️ Error MongoDB: {e}")
    exit(1)


# =============================================================================
# EXTRACCIÓN  (se agrega uuids_info al dict de queries)
# =============================================================================
def extraer_datos_mes(periodo, limite=None):
    dataset = f"{CONFIG['project_id']}.{CONFIG['dataset_id']}"
    p_sql = f"'{periodo}'"

    if limite:
        sub_ids_base = f"""
            SELECT id FROM (
                SELECT DISTINCT id FROM (
                    -- 1. Facturas con pagos asociados (Tipo 'I')
                    (SELECT parent.id
                    FROM `{dataset}.public_cfdi_pago_documentos_relacionados` doc
                    JOIN `{dataset}.public_cfdis` parent ON UPPER(parent.uuid) = UPPER(doc.id_documento)
                    WHERE FORMAT_DATE('%Y-%m', parent.fecha_emision) = {p_sql} 
                      AND parent.company_id = {CONFIG['company_id']} 
                      AND parent.estatus = 'vigente'
                    LIMIT 3000)
                    
                    UNION ALL
                    
                    -- 2. Egresos (Notas de Crédito y Devoluciones)
                    (SELECT id 
                    FROM `{dataset}.public_cfdis`
                    WHERE FORMAT_DATE('%Y-%m', fecha_emision) = {p_sql} 
                      AND company_id = {CONFIG['company_id']} 
                      AND estatus = 'vigente' 
                      AND tipo = 'E'
                    LIMIT 1000)
                    
                    UNION ALL
                    
                    -- 3. Anticipos 
                    (SELECT parent.id 
                    FROM `{dataset}.public_cfdi_relacionados` r
                    JOIN `{dataset}.public_cfdis` parent ON r.uuid_relacionado = parent.uuid
                    WHERE FORMAT_DATE('%Y-%m', parent.fecha_emision) = {p_sql} 
                      AND parent.company_id = {CONFIG['company_id']} 
                      AND parent.estatus = 'vigente' 
                      AND r.tipo_relacion = '07'
                    LIMIT 500)
                    
                    UNION ALL
                    
                    -- 4. Pagos Aplicados independientes (Tipo 'P')
                    (SELECT id 
                    FROM `{dataset}.public_cfdis`
                    WHERE FORMAT_DATE('%Y-%m', fecha_emision) = {p_sql} 
                      AND company_id = {CONFIG['company_id']} 
                      AND estatus = 'vigente' 
                      AND tipo = 'P'
                    LIMIT 1000)
                    
                    UNION ALL
                    
                    -- 5. Resto de facturas normales
                    (SELECT id 
                    FROM `{dataset}.public_cfdis`
                    WHERE FORMAT_DATE('%Y-%m', fecha_emision) = {p_sql} 
                      AND company_id = {CONFIG['company_id']} 
                      AND estatus = 'vigente'
                    LIMIT 14500)
                )
            ) LIMIT {limite}
        """
    else:
        sub_ids_base = f"""
            SELECT id
            FROM `{dataset}.public_cfdis`
            WHERE FORMAT_DATE('%Y-%m', fecha_emision) = {p_sql}
              AND company_id = {CONFIG['company_id']}
              AND estatus = 'vigente'
        """

    sub_ids = f"({sub_ids_base})"

    queries = {
        'cfdis_base': f"""
            SELECT
                c.id, c.uuid, c.fecha_emision, c.tipo, c.metodo_pago, c.estatus, c.total,
                e.rfc AS rfc_emisor, e.nombre AS nombre_emisor,
                r.rfc AS rfc_receptor, r.nombre AS nombre_receptor
            FROM `{dataset}.public_cfdis` c
            LEFT JOIN `{dataset}.public_cfdi_emisors`  e ON c.emisor_id  = e.id
            LEFT JOIN `{dataset}.public_cfdi_receptors` r ON c.receptor_id = r.id
            WHERE c.id IN {sub_ids}
              AND c.tipo IN ('I', 'E', 'P')
        """,
        'relaciones_origen': f"""
            SELECT
                r.cfdi_id AS child_id,
                r.tipo_relacion,
                parent.metodo_pago AS metodo_padre,
                parent.uuid AS uuid_padre,
                parent.id AS parent_id
            FROM `{dataset}.public_cfdi_relacionados` r
            JOIN `{dataset}.public_cfdis` parent ON r.uuid_relacionado = parent.uuid
            WHERE (r.cfdi_id IN {sub_ids} OR parent.id IN {sub_ids})
              AND parent.estatus = 'vigente'
        """,
        'pagos_reps': f"""
            SELECT
                det.fecha_pago,
                doc.imp_pagado,
                doc.id_documento AS uuid_factura,
                c_pago.uuid AS uuid_pago,
                COALESCE(e.rfc, e_p.rfc)    AS rfc_emisor,
                COALESCE(e.nombre, e_p.nombre) AS nombre_emisor,
                COALESCE(r.rfc, r_p.rfc)    AS rfc_receptor,
                COALESCE(r.nombre, r_p.nombre) AS nombre_receptor
            FROM `{dataset}.public_cfdi_pagos` p
            JOIN `{dataset}.public_cfdis` c_pago ON p.cfdi_id = c_pago.id
            JOIN `{dataset}.public_cfdi_pago_detalles` det ON p.id = det.cfdi_pago_id
            JOIN `{dataset}.public_cfdi_pago_documentos_relacionados` doc ON det.id = doc.cfdi_pago_detalle_id
            LEFT JOIN `{dataset}.public_cfdis` c_padre            ON UPPER(doc.id_documento) = UPPER(c_padre.uuid)
            -- Fallback emisor/receptor from the payment receipt itself
            LEFT JOIN `{dataset}.public_cfdi_emisors` e_p  ON c_pago.emisor_id = e_p.id
            LEFT JOIN `{dataset}.public_cfdi_receptors` r_p ON c_pago.receptor_id = r_p.id
            -- Primary emisor/receptor from the invoice being paid (if available)
            LEFT JOIN `{dataset}.public_cfdi_emisors`  e   ON c_padre.emisor_id  = e.id
            LEFT JOIN `{dataset}.public_cfdi_receptors` r  ON c_padre.receptor_id = r.id
            WHERE p.cfdi_id IN {sub_ids}
        """,
        # ── NUEVO: lookup de emisor/receptor para UUIDs no encontrados ──
        # (Se ejecuta más tarde, una vez que sabemos qué UUIDs necesitamos)
    }

    data = {}
    for k, v in queries.items():
        try:
            df = bq_client.query(v).to_dataframe()
            data[k] = df
            print(f"  ✓ {k}: {len(df)} registros")
        except Exception as e:
            print(f"  ❌ Error en {k}: {e}")
            data[k] = pd.DataFrame()
    return data


# =============================================================================
# LOOKUP AUXILIAR: emisor/receptor por lista de UUIDs
# =============================================================================
def fetch_emisor_receptor_por_uuids(uuids: list) -> pd.DataFrame:
    """Consulta BigQuery para obtener rfc/nombre de emisor y receptor
    dado una lista de UUIDs de facturas.  Se usa para rellenar los nulls
    de facturas de períodos anteriores que aparecen como destino de pagos."""
    if not uuids:
        return pd.DataFrame(columns=["uuid", "rfc_emisor", "nombre_emisor", "rfc_receptor", "nombre_receptor"])

    dataset = f"{CONFIG['project_id']}.{CONFIG['dataset_id']}"
    CHUNK = 400
    results = []
    for i in range(0, len(uuids), CHUNK):
        chunk = uuids[i:i + CHUNK]
        # Normalizar a mayúsculas en Python, luego usar como literales SQL
        uuids_upper = [u.upper() for u in chunk]
        uuids_sql = ", ".join(f"'{u}'" for u in uuids_upper)
        q = f"""
            SELECT
                UPPER(c.uuid) AS uuid,
                e.rfc   AS rfc_emisor,
                e.nombre AS nombre_emisor,
                r.rfc   AS rfc_receptor,
                r.nombre AS nombre_receptor
            FROM `{dataset}.public_cfdis` c
            LEFT JOIN `{dataset}.public_cfdi_emisors`  e ON c.emisor_id  = e.id
            LEFT JOIN `{dataset}.public_cfdi_receptors` r ON c.receptor_id = r.id
            WHERE UPPER(c.uuid) IN ({uuids_sql})
        """
        # NOTA: Sin filtro company_id para poder encontrar facturas
        # de otras empresas que son RECIBIDAS por DGN811026BU6.
        try:
            df_chunk = bq_client.query(q).to_dataframe()
            results.append(df_chunk)
        except Exception as ex:
            print(f"    ⚠️ fetch_emisor_receptor chunk {i//CHUNK+1}: {ex}")

    return pd.concat(results, ignore_index=True) if results else pd.DataFrame(
        columns=["uuid", "rfc_emisor", "nombre_emisor", "rfc_receptor", "nombre_receptor"]
    )

def fetch_cfdi_basicos(uuids_missing):
    if not uuids_missing:
        return pd.DataFrame()
        
    dataset = f"{CONFIG['project_id']}.{CONFIG['dataset_id']}"
    uuids_upper = [str(u).strip().upper() for u in uuids_missing if pd.notna(u)]
    if not uuids_upper:
        return pd.DataFrame()
        
    results = []
    CHUNK = 500
    for i in range(0, len(uuids_upper), CHUNK):
        chunk = uuids_upper[i:i+CHUNK]
        uuids_sql = ", ".join(f"'{u}'" for u in chunk)
        q = f"""
            SELECT 
                UPPER(c.uuid) AS uuid, 
                c.total,
                c.fecha_emision,
                e.rfc   AS rfc_emisor, 
                e.nombre AS nombre_emisor,
                r.rfc   AS rfc_receptor,
                r.nombre AS nombre_receptor
            FROM `{dataset}.public_cfdis` c
            LEFT JOIN `{dataset}.public_cfdi_emisors`  e ON c.emisor_id  = e.id
            LEFT JOIN `{dataset}.public_cfdi_receptors` r ON c.receptor_id = r.id
            WHERE UPPER(c.uuid) IN ({uuids_sql})
        """
        try:
            df_chunk = bq_client.query(q).to_dataframe()
            results.append(df_chunk)
        except Exception as ex:
            print(f"    ⚠️ fetch_cfdi_basicos chunk {i//CHUNK+1}: {ex}")

    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()


# =============================================================================
# FUNCIONES DE CLASIFICACIÓN FISCAL (sin cambios)
# =============================================================================
def definir_segmento(row):
    tipo = str(row['tipo']).upper()
    metodo = str(row.get('metodo_pago', '')).upper()
    metodo_padre = str(row.get('metodo_padre', '')).upper()
    if tipo == 'I':
        return metodo if metodo in ['PUE', 'PPD'] else 'PUE'
    if tipo == 'E':
        return metodo_padre if metodo_padre in ['PUE', 'PPD'] else (metodo if metodo in ['PUE', 'PPD'] else 'PUE')
    if tipo == 'P':
        return 'PPD'
    return 'PUE'


def clasificar_flujo(row, rfc_empresa):
    rfc_emisor = str(row['rfc_emisor']).upper().strip()
    rfc_receptor = str(row['rfc_receptor']).upper().strip()
    if rfc_emisor == rfc_empresa:
        return 'EMITIDOS'
    elif rfc_receptor == rfc_empresa:
        return 'RECIBIDOS'
    return 'INDETERMINADO'


def clasificar_concepto(row):
    t = str(row['tipo']).upper()
    rel_raw = str(row.get('tipo_relacion', ''))
    rel = rel_raw.split('.')[0].zfill(2) if rel_raw and rel_raw.lower() not in ['nan', 'na', ''] else 'NA'
    monto = float(row['total']) if pd.notna(row.get('total')) else 0.0

    if t == 'P':
        return '8. (-) Pagos Aplicados (08/09)', 0.0
    if t == 'I' and rel not in ['02']:
        return '1. (+) Total Facturado', monto
    if t == 'E' and rel == '01':
        return '2. (-) Notas de Crédito (01)', -monto
    if t == 'I' and rel == '02':
        return '3. (+) Nota de Débito (02)', monto
    if t == 'E' and rel == '03':
        return '4. (-) Devoluciones (03)', -monto
    if rel in ['05', '06']:
        return '6. Traslado de mercancía (05,06)', 0.0
    if t == 'E' and rel == '07':
        return '7. (-) Anticipo (07)', -monto
    if t == 'I':
        return '1. (+) Total Facturado', monto
    if t == 'E':
        return '2. (-) Notas de Crédito (01)', -monto
    return 'Otros', 0.0


# =============================================================================
# GENERACIÓN DE REPORTES
# =============================================================================
def generar_reportes_mes(periodo, limite_cfdi=10000):
    print(f"\n📅 Procesando mes: {periodo} (limitado a {limite_cfdi} CFDI)")
    start_total = time.time()

    data = extraer_datos_mes(periodo, limite=limite_cfdi)
    df = data.get('cfdis_base', pd.DataFrame()).copy()
    rels = data.get('relaciones_origen', pd.DataFrame()).copy()
    pagos = data.get('pagos_reps', pd.DataFrame()).copy()

    if df.empty:
        print(f"⚠️ No hay CFDI en {periodo}")
        return None

    t1 = time.time()
    print(f"   ⏱️ Extracción: {t1 - start_total:.1f}s")

    df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
    df['Periodo'] = periodo
    df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0.0)
    df['metodo_pago'] = df['metodo_pago'].fillna('ND')
    # DO NOT OVERWRITE df['tipo'], it accurately contains 'I', 'E', or 'P'!

    if not rels.empty:
        id_to_uuid = df.set_index('id')['uuid'].to_dict()
        rels['uuid_hijo'] = rels['child_id'].map(id_to_uuid)
        
        # Unify both child and parent relationships into a single dictionary
        # If a CFDI is a child, it inherits the relation metadata.
        # If a CFDI is a parent (Anticipo), it inherits the relation metadata.
        rel_map = {}
        for row in rels.to_dict(orient='records'):
            child_id = row.get('child_id')
            parent_id = row.get('parent_id')
            tipo_rel = row.get('tipo_relacion', 'NA')
            metodo_padre = row.get('metodo_padre', 'NA')
            
            if pd.notna(child_id):
                rel_map[child_id] = {'tipo_relacion': tipo_rel, 'metodo_padre': metodo_padre}
            if pd.notna(parent_id):
                rel_map[parent_id] = {'tipo_relacion': tipo_rel, 'metodo_padre': metodo_padre}
                
        df['tipo_relacion'] = df['id'].map(lambda x: rel_map.get(x, {}).get('tipo_relacion', 'NA'))
        df['metodo_padre'] = df['id'].map(lambda x: rel_map.get(x, {}).get('metodo_padre', 'NA'))
    else:
        df['tipo_relacion'] = 'NA'
        df['metodo_padre'] = 'NA'

    t2 = time.time()

    df['Segmento'] = df.apply(definir_segmento, axis=1)
    df['Flujo'] = df.apply(lambda r: clasificar_flujo(r, CONFIG['rfc_empresa']), axis=1)

    res = df.apply(clasificar_concepto, axis=1, result_type='expand')
    df['Concepto_Financiero'] = res[0]
    df['Monto_Real'] = res[1]

    t3 = time.time()

    # Calculate Aggregation on Invoices/Egresos BEFORE payments corrupt uuid matching
    df_agg_base = df.groupby(['Segmento', 'Concepto_Financiero'])['Monto_Real'].sum().reset_index()

    if not pagos.empty:
        pagos['fecha_pago'] = pd.to_datetime(pagos['fecha_pago'])
        pagos['Periodo'] = periodo
        pagos['imp_pagado'] = pd.to_numeric(pagos['imp_pagado'], errors='coerce').fillna(0.0)

        pagos_detalle = pagos.copy()
        pagos_detalle['tipo'] = 'P'
        pagos_detalle['metodo_pago'] = 'PPD'
        pagos_detalle['Segmento'] = 'PPD'
        pagos_detalle['Flujo'] = 'EMITIDOS'
        pagos_detalle['Concepto_Financiero'] = '8. (-) Pagos Aplicados (08/09)'
        pagos_detalle['Monto_Real'] = pagos_detalle['imp_pagado'] * -1
        pagos_detalle.rename(columns={'uuid_factura': 'uuid'}, inplace=True)
        for col_name in ['id', 'total']:
            pagos_detalle[col_name] = None
        
        # Add Pagos instantly to the aggregated DataFrame
        df_agg_pagos = pagos_detalle.groupby(['Segmento', 'Concepto_Financiero'])['Monto_Real'].sum().reset_index()
        df_agg = pd.concat([df_agg_base, df_agg_pagos], ignore_index=True)
        df_agg = df_agg.groupby(['Segmento', 'Concepto_Financiero'])['Monto_Real'].sum().reset_index()
        
        # Merge for details
        df = pd.concat([df, pagos_detalle], ignore_index=True, sort=False)
    else:
        df_agg = df_agg_base

    # ── FIX: Rellenar nulls de rfc/nombre dentro del mismo UUID ────────────
    # Para UUIDs que tienen alguna fila con datos (ej. factura orig + pago),
    # propagamos el valor no-null al resto de filas del mismo UUID.
    COLS_RFC = ['rfc_emisor', 'nombre_emisor', 'rfc_receptor', 'nombre_receptor']
    for col_name in COLS_RFC:
        df[col_name] = df.groupby('uuid')[col_name].transform(
            lambda s: s.ffill().bfill()
        )

    # ── FIX: Para UUIDs que siguen sin datos (facturas de otros períodos),
    #         consultamos BigQuery directamente. ──────────────────────────
    uuids_aun_null = df[df['rfc_emisor'].isna()]['uuid'].dropna().unique().tolist()
    if uuids_aun_null:
        print(f"   🔍 {len(uuids_aun_null)} UUIDs aún sin emisor — consultando BigQuery...")
        df_lookup = fetch_emisor_receptor_por_uuids(uuids_aun_null)
        if not df_lookup.empty:
            df_lookup['uuid_upper'] = df_lookup['uuid'].str.upper()
            lookup_map = df_lookup.set_index('uuid_upper')[COLS_RFC].to_dict(orient='index')

            def fill_from_lookup(row):
                key = str(row.get('uuid', '')).upper()
                if pd.isna(row.get('rfc_emisor')) and key in lookup_map:
                    for c in COLS_RFC:
                        row[c] = lookup_map[key].get(c)
                return row

            df = df.apply(fill_from_lookup, axis=1)
            print(f"   ✓ Datos de emisor/receptor rellenados para {len(df_lookup)} UUIDs adicionales")

    t4 = time.time()
    print(f"   ⏱️ Integración pagos + fix nulls: {t4 - t3:.1f}s")

    # ========== 1. MATRIZ RESUMEN ==========
    # df_agg is already calculated securely!

    conceptos_fijos = [
        '1. (+) Total Facturado',
        '2. (-) Notas de Crédito (01)',
        '3. (+) Nota de Débito (02)',
        '4. (-) Devoluciones (03)',
        '6. Traslado de mercancía (05,06)',
        '7. (-) Anticipo (07)',
        '8. (-) Pagos Aplicados (08/09)'
    ]
    segmentos_fijos = ['PPD', 'PUE']

    matriz = []
    
    # ── FIX: Flatten df_agg to a robust dictionary to avoid boolean mask failures
    agg_dict = {}
    for row in df_agg.itertuples(index=False):
        seg = row.Segmento
        conc = row.Concepto_Financiero
        monto = row.Monto_Real
        agg_dict[(seg, conc)] = agg_dict.get((seg, conc), 0.0) + monto

    for seg in segmentos_fijos:
        for concepto in conceptos_fijos:
            monto = agg_dict.get((seg, concepto), 0.0)
            matriz.append({'periodo': periodo, 'company_id': CONFIG['company_id'],
                           'segmento': seg, 'concepto': concepto, 'monto': float(monto)})

    conceptos_saldo = ['1. (+) Total Facturado', '2. (-) Notas de Crédito (01)',
                       '4. (-) Devoluciones (03)', '7. (-) Anticipo (07)', '8. (-) Pagos Aplicados (08/09)']
    for seg in segmentos_fijos:
        saldo = sum(item['monto'] for item in matriz if item['segmento'] == seg and item['concepto'] in conceptos_saldo)
        matriz.append({'periodo': periodo, 'company_id': CONFIG['company_id'],
                       'segmento': seg,
                       'concepto': '9. (=) Saldo ' + ('Insoluto PPD' if seg == 'PPD' else 'Teórico PUE'),
                       'monto': float(saldo)})

    t5 = time.time()
    print(f"   ⏱️ Matriz resumen: {t5 - t4:.1f}s")

    # ========== 2. DETALLE POR UUID ==========
    df_first = df.groupby('uuid').first()[
        ['Segmento', 'Flujo'] + COLS_RFC
    ].reset_index()
    df_saldo = df.groupby('uuid')['Monto_Real'].sum().reset_index()
    df_saldo.rename(columns={'Monto_Real': 'saldo_acumulado'}, inplace=True)
    df_conceptos = df.groupby(['uuid', 'Concepto_Financiero'])['Monto_Real'].sum().reset_index()

    # Optimized CONCEPTOS building: Group by uuid and build a dictionary once
    uuid_to_conceptos = {}
    for row in df_conceptos.itertuples(index=False):
        uid = row.uuid
        if uid not in uuid_to_conceptos:
            uuid_to_conceptos[uid] = {}
        uuid_to_conceptos[uid][row.Concepto_Financiero] = row.Monto_Real

    df_detalle_base = df_first.merge(df_saldo, on='uuid')

    def safe(v):
        return None if (v is None or (isinstance(v, float) and np.isnan(v))) else v

    detalle = []
    # Use to_dict('records') for fast iteration
    for row in df_detalle_base.to_dict('records'):
        detalle.append({
            'periodo': periodo,
            'company_id': CONFIG['company_id'],
            'uuid': row['uuid'],
            'segmento': row['Segmento'],
            'flujo': row['Flujo'],
            'rfc_emisor':    safe(row.get('rfc_emisor')),
            'nombre_emisor': safe(row.get('nombre_emisor')),
            'rfc_receptor':  safe(row.get('rfc_receptor')),
            'nombre_receptor': safe(row.get('nombre_receptor')),
            'conceptos': uuid_to_conceptos.get(row['uuid'], {}),
            'saldo_acumulado': row['saldo_acumulado']
        })

    t6 = time.time()
    print(f"   ⏱️ Detalle UUID: {t6 - t5:.1f}s ({len(detalle)} UUIDs)")

    # ========== 3. TRAZABILIDAD UUID ==========
    trazabilidad = []
    
    # Map cleaned UUID info directly from df since df was already patched via BQ
    # This now includes fallback emisor/receptor data from payments!
    COLS_RFC = ['rfc_emisor', 'nombre_emisor', 'rfc_receptor', 'nombre_receptor']
    # Optimized info_map build: prioritizing non-null rows
    # We sort by non-null counts or just use last-writer-wins efficiently
    info_map = {}
    # Use itertuples for 10x speedup over iterrows
    for row in df.itertuples(index=False):
        uid = getattr(row, 'uuid', None)
        if not uid or pd.isna(uid): continue
        curr = info_map.get(uid, {})
        for col in COLS_RFC:
            val = getattr(row, col, None)
            if pd.notna(val) and val != '':
                curr[col] = val
        info_map[uid] = curr

    if not rels.empty and 'uuid_hijo' in rels.columns:
        # Pre-filter df to only include relevant children for O(1) inside loop
        rel_uuids = set(rels['uuid_hijo'].unique())
        df_kids = df[df['uuid'].isin(rel_uuids)].to_dict('records')
        kid_moves = {}
        for m in df_kids:
            kid_moves.setdefault(m['uuid'], []).append(m)

        for row in rels.itertuples(index=False):
            hijo = row.uuid_hijo
            padre = row.uuid_padre
            tipo = row.tipo_relacion
            info_padre = info_map.get(padre) or info_map.get(hijo) or {}
            
            if pd.notna(hijo) and pd.notna(padre):
                for m in kid_moves.get(hijo, []):
                    trazabilidad.append({
                        'periodo': periodo,
                        'company_id': CONFIG['company_id'],
                        'uuid_raiz': padre,
                        'uuid_relacionado': hijo,
                        'tipo_relacion': tipo,
                        'concepto': m['Concepto_Financiero'],
                        'fecha': m['fecha_emision'].isoformat() if pd.notna(m.get('fecha_emision')) else None,
                        'monto': m['Monto_Real'],
                        'monto': m['Monto_Real']
                        # Metadata pruned to save space, only BASE carries it
                    })

    if not pagos.empty:
        for p in pagos.to_dict('records'):
            uuid_fact = p.get('uuid_factura')
            if pd.notna(uuid_fact):
                info_fact = info_map.get(uuid_fact) or {}
                trazabilidad.append({
                    'periodo': periodo,
                    'company_id': CONFIG['company_id'],
                    'uuid_raiz': uuid_fact,
                    'uuid_relacionado': p.get('uuid_pago'),
                    'tipo_relacion': 'PAGO',
                    'concepto': '8. (-) Pagos Aplicados (08/09)',
                    'fecha': p['fecha_pago'].isoformat() if pd.notna(p.get('fecha_pago')) else None,
                    'monto': -abs(p['imp_pagado']),
                    'monto': -abs(p['imp_pagado'])
                    # Metadata pruned to save space, only BASE carries it
                })

    # Collect all root UUIDs that we must process in this period
    # 1. Roots from invoices issued this month (tipo 'I')
    raices_activas = set(df[df['tipo'] == 'I']['uuid'].unique())
    # 2. Roots from payments/rels (which might be for invoices from other months)
    traz_raices = set(t.get('uuid_raiz') for t in trazabilidad if pd.notna(t.get('uuid_raiz')))
    raices_activas = raices_activas.union(traz_raices)

    # We will build base events for these roots
    base_events = []
    
    # 1. Look for roots genuinely present in our current month's cfdi_base df
    df_real_bases = df[(df['uuid'].isin(raices_activas)) & (df['tipo'] != 'P')].drop_duplicates('uuid')
    for row in df_real_bases.to_dict('records'):
        uid = row['uuid']
        info_fallback = info_map.get(uid, {})
        base_events.append({
            'periodo': periodo,
            'company_id': CONFIG['company_id'],
            'uuid_raiz': uid,
            'uuid_relacionado': uid,
            'tipo_relacion': 'BASE',
            'concepto': '1. (+) Total Facturado',
            'fecha': row['fecha_emision'].isoformat() if pd.notna(row.get('fecha_emision')) else None,
            'monto': float(row.get('total', 0.0)),
            'rfc_emisor': row.get('rfc_emisor') or info_fallback.get('rfc_emisor'),
            'nombre_emisor': row.get('nombre_emisor') or info_fallback.get('nombre_emisor'),
            'rfc_receptor': row.get('rfc_receptor') or info_fallback.get('rfc_receptor'),
            'nombre_receptor': row.get('nombre_receptor') or info_fallback.get('nombre_receptor')
        })
        
    # 2. Find roots strictly missing invoice data and fetch them from BQ
    found_roots = set(df_real_bases['uuid'].dropna())
    missing_roots = raices_activas - found_roots
    
    if missing_roots:
        df_missing = fetch_cfdi_basicos(list(missing_roots))
        if not df_missing.empty:
            for _, row in df_missing.iterrows():
                # Handle Timestamp serialization
                dt = row['fecha_emision']
                fecha_str = dt.isoformat() if pd.notna(dt) else None
                base_events.append({
                    'periodo': periodo,
                    'company_id': CONFIG['company_id'],
                    'uuid_raiz': row['uuid'],
                    'uuid_relacionado': row['uuid'],
                    'tipo_relacion': 'BASE',
                    'concepto': '1. (+) Total Facturado',
                    'fecha': fecha_str,
                    'monto': float(row.get('total', 0.0)),
                    'rfc_emisor': row.get('rfc_emisor') or info_map.get(row['uuid'], {}).get('rfc_emisor'),
                    'nombre_emisor': row.get('nombre_emisor') or info_map.get(row['uuid'], {}).get('nombre_emisor'),
                    'rfc_receptor': row.get('rfc_receptor') or info_map.get(row['uuid'], {}).get('rfc_receptor'),
                    'nombre_receptor': row.get('nombre_receptor') or info_map.get(row['uuid'], {}).get('nombre_receptor')
                })
        else:
            # Still missing from BQ? Synthesize from what we have in info_map
            for missed_uid in missing_roots:
                info_fallback = info_map.get(missed_uid, {})
                if info_fallback:
                    base_events.append({
                        'periodo': periodo,
                        'company_id': CONFIG['company_id'],
                        'uuid_raiz': missed_uid,
                        'uuid_relacionado': missed_uid,
                        'tipo_relacion': 'BASE',
                        'concepto': '1. (+) Total Facturado (Sintetizado)',
                        'fecha': None,
                        'monto': 0.0,
                        'rfc_emisor': info_fallback.get('rfc_emisor'),
                        'nombre_emisor': info_fallback.get('nombre_emisor'),
                        'rfc_receptor': info_fallback.get('rfc_receptor'),
                        'nombre_receptor': info_fallback.get('nombre_receptor')
                    })
        
        # Prepend the base events so they are processed first in running balance
        trazabilidad = base_events + trazabilidad

    # Deduplicate trazabilidad array before returning
    trazabilidad_dedup = []
    seen_traz = set()
    for tr in trazabilidad:
        sig = (tr.get('uuid_raiz'), tr.get('uuid_relacionado'), tr.get('concepto'), tr.get('fecha'), tr.get('monto'), tr.get('tipo_relacion'))
        if sig not in seen_traz:
            seen_traz.add(sig)
            trazabilidad_dedup.append(tr)

    t7 = time.time()
    print(f"   ⏱️ Trazabilidad: {t7 - t6:.1f}s ({len(trazabilidad_dedup)} eventos únicos de {len(trazabilidad)} originales)")

    return matriz, detalle, trazabilidad_dedup, t7 - start_total


# =============================================================================
# INSERCIÓN EN MONGODB
# =============================================================================
def guardar_en_mongo(periodo, matriz, detalle, trazabilidad):
    col_matriz = db[CONFIG['col_matriz']]
    col_detalle = db[CONFIG['col_detalle']]
    col_trazabilidad = db[CONFIG['col_trazabilidad']]

    t_start = time.time()

    col_matriz.create_index([("periodo", 1), ("company_id", 1), ("segmento", 1), ("concepto", 1)], unique=True)
    col_detalle.create_index([("periodo", 1), ("company_id", 1), ("uuid", 1)], unique=True)
    col_trazabilidad.create_index([("periodo", 1), ("company_id", 1), ("uuid_raiz", 1), ("fecha", 1)])

    if matriz:
        col_matriz.bulk_write([
            UpdateOne(
                {"periodo": periodo, "company_id": CONFIG['company_id'],
                 "segmento": f["segmento"], "concepto": f["concepto"]},
                {"$set": f}, upsert=True
            ) for f in matriz
        ], ordered=False)
    print(f"   💾 Matriz: {time.time()-t_start:.1f}s ({len(matriz)} docs)")

    if detalle:
        col_detalle.bulk_write([
            UpdateOne(
                {"periodo": periodo, "company_id": CONFIG['company_id'], "uuid": item["uuid"]},
                {"$set": item}, upsert=True
            ) for item in detalle
        ], ordered=False)
    print(f"   💾 Detalle UUID: ({len(detalle)} docs)")

    if trazabilidad:
        col_trazabilidad.delete_many({"periodo": periodo, "company_id": CONFIG['company_id']})
        try:
            col_trazabilidad.bulk_write([InsertOne(doc) for doc in trazabilidad], ordered=False)
        except errors.BulkWriteError as e:
            print(f"   ⚠️ Trazabilidad: {len(e.details.get('writeErrors', []))} duplicados ignorados")
    print(f"   💾 Trazabilidad: ({len(trazabilidad)} eventos)")
    print(f"✅ Guardado en MongoDB para {periodo} (total: {time.time()-t_start:.1f}s)")


# =============================================================================
# PROCESAR MÚLTIPLES MESES
# =============================================================================
def procesar_meses(lista_periodos, limite_cfdi=10000):
    # One-time storage recovery
    col_traz = db[CONFIG['col_trazabilidad']]
    col_det = db[CONFIG['col_detalle']]
    
    print("🧹 Iniciando optimización de almacenamiento...")
    try:
        # Drop redundant/heavy indexes
        existing_indexes_traz = [idx['name'] for idx in col_traz.list_indexes()]
        if 'company_id_1_uuid_raiz_1_fecha_1' in existing_indexes_traz:
            col_traz.drop_index('company_id_1_uuid_raiz_1_fecha_1')
            print("   ✅ Indice redundante en trazabilidad eliminado")
            
        existing_indexes_det = [idx['name'] for idx in col_det.list_indexes()]
        for idx_to_drop in ['company_id_1_autocreated', 'company_id_1_rfc_receptor_1', 'company_id_1_rfc_emisor_1']:
            if idx_to_drop in existing_indexes_det:
                col_det.drop_index(idx_to_drop)
                print(f"   ✅ Indice redundante {idx_to_drop} eliminado")
    except Exception as e:
        print(f"   ⚠️ Error optimizando índices: {e}")

    # Clean inactive months (only months older than our 6-month window)
    old_periods = ['2025-08', '2025-07', '2025-06', '2025-05', '2025-04', '2025-03']
    for cname in [CONFIG['col_matriz'], CONFIG['col_detalle'], CONFIG['col_trazabilidad']]:
        res = db[cname].delete_many({'periodo': {'$in': old_periods}})
        if res.deleted_count > 0:
            print(f"   🧹 Limpieza: {res.deleted_count} registros de {cname}")

    tiempo_total = 0
    for periodo in lista_periodos:
        print("\n" + "=" * 60)
        start = time.time()
        resultado = generar_reportes_mes(periodo, limite_cfdi=limite_cfdi)
        if resultado:
            matriz, detalle, trazabilidad, tiempo_proc = resultado
            guardar_en_mongo(periodo, matriz, detalle, trazabilidad)
            duracion = time.time() - start
            tiempo_total += duracion
            print(f"⏱️ Tiempo total {periodo}: {duracion:.1f}s (proc: {tiempo_proc:.1f}s)")
        else:
            print(f"⚠️ No se generaron datos para {periodo}")

    print("\n" + "=" * 60)
    print(f"🎉 PROCESO COMPLETADO — {tiempo_total / 60:.1f} min")


if __name__ == "__main__":
    # 20k sample per month, last 6 months
    periodos_a_procesar = ['2026-02', '2026-01', '2025-12', '2025-11', '2025-10', '2025-09']
    procesar_meses(periodos_a_procesar, limite_cfdi=20000)

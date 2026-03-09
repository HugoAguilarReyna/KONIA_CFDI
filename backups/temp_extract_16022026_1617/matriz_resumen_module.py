import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os
from pymongo import MongoClient
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURACIÓN MONGODB
# =============================================================================
# Use environment variables in production, but for now using the provided string
MONGO_URI = "mongodb+srv://aguilarhugo55_db_user:c5mfG11QT68ib4my@clusteract1.kpdhd5e.mongodb.net/fiscal_reports?authSource=admin&appName=ClusterAct1"
DB_NAME = "fiscal_reports"
COLLECTION_NAME = "matriz_resumen"

def get_fiscal_reports_data(company_id_str, year=None, month=None):
    """Fetches pre-aggregated data from fiscal_reports.matriz_resumen."""
    try:
        # Mapping for dev environment
        # In prod, this should be in a distinct collection or env var
        company_map = {"TENANT_001": 2, "comp_default": 2} 
        
        # If it's already an int, use it, else map
        if isinstance(company_id_str, int):
            cid = company_id_str
        else:
            cid = company_map.get(company_id_str, 2)
            
        client = get_mongo_client()
        db = client[DB_NAME]
        col = db[COLLECTION_NAME]
        
        query = {"company_id": cid}
        
        if year:
            if month and month > 0:
                # Exact match YYYY-MM
                query["periodo"] = f"{year}-{month:02d}"
            else:
                # Regex for YYYY-
                query["periodo"] = {"$regex": f"^{year}-"}
                
        docs = list(col.find(query, {"_id": 0}))
        return docs
    except Exception as e:
        st.error(f"Error fetching fiscal reports: {e}")
        return []

def process_fiscal_data(docs):
    """Adapts fiscal_reports documents to the React artifact structure."""
    data = []
    for doc in docs:
        periodo = doc.get("periodo", "")
        if not periodo: continue
        
        # Construct date YYYY-MM-01 for React grouping
        fecha = f"{periodo}-01"
        
        # Strip garbage from concept (e.g. trailing newlines or numbers from OCR/Extraction artifacts)
        c = doc.get("concepto", "Otros").strip().split('\n')[0].strip()
        tipo = "I" # Default
        if "(-)" in c: tipo = "E"
        elif "Traslado" in c: tipo = "T"
        
        item = {
            "fecha": fecha,
            "segmento": doc.get("segmento", "PUE"),
            "concepto": c, # Fixed: React artifact expects 'concepto', not 'concepto_fiscal'
            "tipo": tipo,
            "metodo_pago": doc.get("segmento", "PUE"),
            "monto": float(doc.get("monto", 0.0))
        }
        data.append(item)
    return data


@st.cache_resource
def get_mongo_client():
    """Returns a cached MongoDB client."""
    return MongoClient(MONGO_URI)

@st.cache_data(ttl=300)
def cargar_matriz_desde_mongo(company_id=2):
    """Carga todos los datos de la matriz resumen desde MongoDB con caché de 5 minutos."""
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        col = db[COLLECTION_NAME]
        
        # Obtener todos los datos de la empresa
        query = {"company_id": company_id}
        docs = list(col.find(query, {"_id": 0}))
        
        if not docs:
            return pd.DataFrame()
        
        df = pd.DataFrame(docs)
        return df
    except Exception as e:
        st.error(f"Error conectando a MongoDB: {e}")
        return pd.DataFrame()

def get_previous_period(period_str):
    """Calculates the previous month given a YYYY-MM string."""
    try:
        date = datetime.strptime(period_str, "%Y-%m")
        prev_date = date.replace(day=1) - timedelta(days=1)
        return prev_date.strftime("%Y-%m")
    except:
        return period_str

def get_available_periods_from_mongo(company_id=2):
    """
    Queries MongoDB to find all distinct 'periodo' values (YYYY-MM) in fiscal_reports,
    ensuring the filter dropdowns are populated with ACTUAL available data,
    independent of what's currently loaded in the main DataFrame.
    """
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        col = db[COLLECTION_NAME]
        
        # DISTINCT query is efficient
        unique_periods = col.distinct("periodo", {"company_id": company_id})
        
        # Filter for valid YYYY-MM format just in case
        valid_periods = [p for p in unique_periods if isinstance(p, str) and len(p) == 7 and '-' in p]
        
        return sorted(valid_periods, reverse=True)
    except Exception as e:
        st.error(f"Error fetching periods from Mongo: {e}")
        return []

# =============================================================================
# PROCESAMIENTO DINÁMICO (Nuevo para Premium Filters)
# =============================================================================

def procesar_matriz_dinamica(df):
    """
    Convierte un DataFrame de CFDIs crudos en una estructura rica para React.
    Mantiene dimensiones para filtrado en el cliente (Tipo, Metodo, Fecha).
    """
    if df.empty:
        return []
    
    df = df.copy()
    df['fecha_emision'] = pd.to_datetime(df['fecha_emision'])
    df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0.0)
    
    # Segmentación (PPD vs PUE)
    def definir_segmento(row):
        m = str(row.get('metodo_pago', '')).upper()
        return m if m in ['PUE', 'PPD'] else 'PUE' # Default to PUE
    
    df['segmento'] = df.apply(definir_segmento, axis=1)
    
    # Clasificación Fiscal Detallada (Lógica de Matriz Fiscal)
    def clasificar_concepto(row):
        t = str(row.get('tipo', 'I')).upper()
        # Intentar obtener tipo_relacion, si no existe, usar 'NA'
        # Nota: En MongoDB raw, a veces no existe esta columna si no se hizo join.
        tr = str(row.get('tipo_relacion', 'NA')) 
        
        # 1. Ingresos
        if t == 'I':
            if tr == '02':
                return '3. (+) Nota de Débito (02)'
            else:
                return '1. (+) Total Facturado'
        
        # 2. Egresos
        if t == 'E':
            if tr == '01':
                return '2. (-) Notas de Crédito (01)'
            elif tr == '03':
                return '4. (-) Devoluciones (03)'
            elif tr == '04':
                return '5. (-) Sustituciones (04)'
            elif tr == '07':
                return '7. (-) Anticipo (07)'
            else:
                # Default para Egreso sin relación específica identificada o 01 genérico
                return '2. (-) Notas de Crédito (01)'
                
        # 3. Traslados
        if t == 'T' or tr in ['05', '06']:
            return '6. Traslado de mercancía (05,06)'
            
        # 4. Pagos
        if t == 'P':
            return '8. (-) Pagos Aplicados (08/09)'
            
        return 'Otros'

    df['concepto'] = df.apply(clasificar_concepto, axis=1)
    
    # Pre-agrupar por Día + Segmento + Concepto + Tipo + Metodo 
    # (Para no pasar miles de filas a React, solo las necesarias para filtros)
    df_agg = df.groupby([
        df['fecha_emision'].dt.strftime('%Y-%m-%d'), 
        'segmento', 
        'concepto',
        'tipo',
        'metodo_pago'
    ])['total'].sum().reset_index()
    
    df_agg.columns = ['fecha', 'segmento', 'concepto', 'tipo', 'metodo_pago', 'monto']
    
    return df_agg.to_dict(orient='records')

# =============================================================================
# FUNCIÓN PRINCIPAL DE RENDERIZADO (ACTUALIZADA)
# =============================================================================

def render_matriz_resumen_artifact(df_filtered, periodo_label="Selección Actual", grouping="M", year=None, month=None):
    """
    Renderiza la Matriz Resumen con un Artifact React interactivo usando data dinámica.
    Ahora usa el DataFrame filtrado de la aplicación principal para respetar los filtros de sidebar.
    """
    
    st.markdown('<div class="section-header">📊 MATRIZ FISCAL RESUMEN (PREMIUM)</div>', unsafe_allow_html=True)
    
    # 0. Context Recovery (Company ID)
    company_id = st.session_state.get("company_id", "TENANT_001")
    
    # 1. Procesar datos dinámicamente
    with st.spinner("Procesando datos fiscales..."):
        # USER REQUEST: "este filtro debe apuntar a la tabla de mongo apuntar al campo periodo"
        # We prioritize fetching from the pre-calculated 'matriz_resumen' collection in Mongo
        # employing the 'periodo' field (YYYY-MM).
        
        # Try fetching from Mongo first using the strict period filter
        docs = get_fiscal_reports_data(company_id, year, month)
        
        if docs:
            data_list = process_fiscal_data(docs)
        elif df_filtered is not None and not df_filtered.empty:
             # Fallback to dynamic processing if Mongo has no data
            data_list = procesar_matriz_dinamica(df_filtered)
        else:
            data_list = []

    if not data_list:
        st.warning(f"⚠️ No hay datos fiscales procesados para el periodo seleccionado ({year}-{month}).")
        return
    
    # 2. Preparar Payload
    # Determinamos mes_actual y mes_anterior de los datos reales para compatibilidad con el UI viejo
    # aunque ahora usaremos 'fecha' para agrupar.
    periodos = sorted(list(set([d['fecha'][:7] for d in data_list])))
    mes_actual = periodos[-1] if periodos else "N/A"
    mes_anterior = periodos[-2] if len(periodos) > 1 else "N/A"

    # Map Python grouping code to React grouping code
    grouping_map = {"D": "day", "W": "week", "M": "month"}
    react_grouping = grouping_map.get(grouping, "month")

    artifact_payload = {
        "mes_anterior": mes_anterior,
        "mes_actual": mes_actual,
        "data": data_list,
        "label": periodo_label,
        "grouping": react_grouping
    }
    
    # 3. Inyectar en HTML y Renderizar
    artifact_path = os.path.join(os.path.dirname(__file__), "matriz_resumen_artifact.html")
    
    if os.path.exists(artifact_path):
        with open(artifact_path, "r", encoding="utf-8") as f:
            html_template = f.read()
            
        json_payload = json.dumps(artifact_payload, allow_nan=False)
        
        injection = f"""
        <script>
            window.data = {json_payload};
            console.log("Matriz Premium Data Injected:", window.data);
        </script>
        """
        
        if '<div id="root"></div>' in html_template:
            final_html = html_template.replace('<div id="root"></div>', f'{injection}<div id="root"></div>')
            # Increased height to 2000px as per user request to show full table
            components.html(final_html, height=2000, scrolling=True)
        else:
            st.error("Error: Artifact template invalido (falta #root).")
    else:
        st.error(f"Artifact no encontrado en: {artifact_path}")

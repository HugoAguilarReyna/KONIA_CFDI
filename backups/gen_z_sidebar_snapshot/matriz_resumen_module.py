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
        
        c = doc.get("concepto", "Otros")
        tipo = "I" # Default
        if "(-)" in c: tipo = "E"
        elif "Traslado" in c: tipo = "T"
        
        item = {
            "fecha": fecha,
            "segmento": doc.get("segmento", "PUE"),
            "concepto_fiscal": c,
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


def render_matriz_resumen_artifact(periodo_ignored, company_id=2, sidebar_container=None):
    """
    Renderiza la Matriz Resumen con filtros Premium en el sidebar.
    """
    import datetime
    
    # 0. RESOLVER CONTAINER
    # Si pasamos un container personalizado (sidebar premium), lo usamos.
    # Si no, fallback a st.sidebar (aunque sin el estilo premium flotante completo tal vez).
    filter_target = sidebar_container if sidebar_container else st.sidebar
    
    # 1. RENDERIZAR FILTROS EN SIDEBAR
    with filter_target:
        # MARCADOR CSS (CRÍTICO PARA EL ESTILO FLOTANTE)
        st.markdown('<div id="filter-sidebar-marker"></div>', unsafe_allow_html=True)
        
        st.markdown("### 🔍 FILTROS PREMIUM")
        st.markdown("---")

        # A. AÑO Y MES (Controlan la carga de datos)
        col_y, col_m = st.columns([1, 1])
        with col_y:
            sel_year = st.selectbox("Año", ["2024", "2025", "2026"], index=0, key="prem_year")
        with col_m:
            meses_map = {1:"ENE", 2:"FEB", 3:"MAR", 4:"ABR", 5:"MAY", 6:"JUN", 
                         7:"JUL", 8:"AGO", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DIC"}
            current_month_idx = datetime.datetime.now().month - 1
            sel_month_name = st.selectbox("Mes", list(meses_map.values()), index=current_month_idx, key="prem_month")
            
        # Convertir selección a periodo YYYY-MM
        sel_month_num = [k for k,v in meses_map.items() if v == sel_month_name][0]
        periodo_seleccionado = f"{sel_year}-{sel_month_num:02d}"

        st.markdown("---")

        # B. TIPO COMPROBANTE
        tipo_opts = ['Ingreso (I)', 'Egreso (E)', 'Nómina (N)', 'Pago (P)']
        sel_tipos = st.multiselect("Tipo Comprobante", tipo_opts, default=['Ingreso (I)', 'Egreso (E)'], key="prem_tipo")
        
        # Mapping reverso
        tipo_map = {'Ingreso (I)': 'I', 'Egreso (E)': 'E', 'Nómina (N)': 'N', 'Pago (P)': 'P'}
        sel_tipo_codes = [tipo_map[t] for t in sel_tipos]

        # C. MÉTODO PAGO
        st.markdown("---")
        metodo_opts = ['PPD', 'PUE']
        sel_metodos = st.multiselect("Método de Pago", metodo_opts, default=metodo_opts, key="prem_metodo")

        # D. BÚSQUEDA
        st.markdown("---")
        search_term = st.text_input("Buscar Concepto", "", key="prem_search")
        
        # E. ACCIONES
        st.markdown("---")
        if st.button("🔄 Actualizar", type="primary", use_container_width=True):
            st.rerun()

    # 2. CARGAR Y PROCESAR DATOS
    # Usamos el periodo seleccionado en el sidebar
    
    st.markdown(f'<div class="section-header">📊 MATRIZ FISCAL: {periodo_seleccionado}</div>', unsafe_allow_html=True)
    
    with st.spinner(f"Analizando periodo {periodo_seleccionado}..."):
        # Cargar todos los datos relevantes (simulado: cargar todo o por año)
        # Nota: Idealmente get_fiscal_reports_data filtraría por año/mes en backend.
        # Asumiremos que carga suficiente data y filtraremos en memoria.
        
        # Intentar cargar data del año seleccionado
        docs = get_fiscal_reports_data(company_id, year=int(sel_year), month=None) 
        
        if not docs:
             st.warning(f"No hay datos para {sel_year}")
             return

        # Procesar a formato plano
        raw_data = process_fiscal_data(docs)
        
        # 3. FILTRADO EN MEMORIA (Python)
        filtered_data = []
        for d in raw_data:
            # Filtro Periodo (Exacto o Rango? Matriz usualmente muestra Mes Actual y Anterior)
            # Para la matriz, necesitamos data de este mes Y el anterior.
            # O la función process_fiscal_data ya nos da lo que necesitamos?
            # Asumiremos que docs trae todo el año y filtramos aquí.
            
            # Filtro de Propiedades
            # d tiene: {'fecha': 'YYYY-MM-01', 'segmento': 'PPD/PUE', 'concepto': '...', 'tipo': 'I/E', 'monto': ...}
            
            # 1. Filtro Tipo
            if d.get('tipo', 'I') not in sel_tipo_codes:
                continue
                
            # 2. Filtro Método (Solo aplica relevante si es PPD/PUE, si es otro ignoramos filtro? O estricto?)
            # El segmento ya es PPD/PUE.
            if d.get('segmento') not in sel_metodos:
                continue
                
            # 3. Filtro Búsqueda
            if search_term and search_term.lower() not in d.get('concepto', '').lower():
                 continue
                 
            filtered_data.append(d)
            
    # 4. PREPARAR PAYLOAD REACT
    # Calcular mes anterior
    dt_curr = datetime.date(int(sel_year), sel_month_num, 1)
    # Mes anterior simple
    dt_prev = (dt_curr.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
    periodo_anterior = f"{dt_prev.year}-{dt_prev.month:02d}"
    
    # Payload
    artifact_payload = {
        "mes_anterior": periodo_anterior,
        "mes_actual": periodo_seleccionado,
        "data": filtered_data,
        "label": f"Periodo {periodo_seleccionado}",
        "grouping": "month"
    }

    # 5. RENDERIZAR
    artifact_path = os.path.join(os.path.dirname(__file__), "matriz_resumen_artifact.html")
    if os.path.exists(artifact_path):
        with open(artifact_path, "r", encoding="utf-8") as f:
            html_val = f.read()
        
        import json
        payload_json = json.dumps(artifact_payload, allow_nan=False)
        
        injection = f"""
        <script>
        window.matrixData = {payload_json};
        </script>
        """
        html_content = injection + html_val
        components.html(html_content, height=800, scrolling=True)



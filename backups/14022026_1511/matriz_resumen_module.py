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
# FUNCIÓN PRINCIPAL DE RENDERIZADO
# =============================================================================

def render_matriz_resumen_artifact(periodo_seleccionado, company_id=2):
    """
    Renderiza la Matriz Resumen con un Artifact React interactivo.
    """
    
    st.markdown('<div class="section-header">📊 MATRIZ FISCAL RESUMEN (PREMIUM)</div>', unsafe_allow_html=True)
    
    # 1. Cargar datos
    with st.spinner("Conectando con MongoDB Atlas..."):
        df_matriz = cargar_matriz_desde_mongo(company_id)
    
    if df_matriz.empty:
        st.warning("⚠️ No se encontraron datos en la colección 'matriz_resumen'.")
        return
    
    # 2. Lógica de Períodos
    periodos_disponibles = sorted(df_matriz['periodo'].unique())
    
    if periodo_seleccionado == "Todos" or periodo_seleccionado is None:
        # Default to last 2 available
        if len(periodos_disponibles) >= 2:
            mes_actual = periodos_disponibles[-1]
            mes_anterior = periodos_disponibles[-2]
        elif len(periodos_disponibles) == 1:
             mes_actual = periodos_disponibles[0]
             mes_anterior = periodos_disponibles[0] # Fallback
        else:
             st.error("No hay períodos disponibles.")
             return
    else:
        mes_actual = periodo_seleccionado
        # Try to find previous period in available list, else calculate
        idx = -1
        if mes_actual in periodos_disponibles:
             idx = periodos_disponibles.index(mes_actual)
        
        if idx > 0:
            mes_anterior = periodos_disponibles[idx - 1]
        else:
            # If selected is the first available, or not in list, try to calc or just use same
            mes_anterior = get_previous_period(mes_actual)

    # 3. Filtrar DataFrames
    # We need data for BOTH periods to pass to React
    df_filtrado = df_matriz[df_matriz['periodo'].isin([mes_anterior, mes_actual])].copy()

    # --- DATA CLEANING ---
    # Strip whitespace to ensure merging with template works
    if not df_filtrado.empty:
        if 'concepto' in df_filtrado.columns:
            df_filtrado['concepto'] = df_filtrado['concepto'].astype(str).str.strip()
        if 'segmento' in df_filtrado.columns:
            df_filtrado['segmento'] = df_filtrado['segmento'].astype(str).str.strip()
        # CRITICAL: Ensure monto is numeric BEFORE merge to avoid object/sum issues
        if 'monto' in df_filtrado.columns:
            df_filtrado['monto'] = pd.to_numeric(df_filtrado['monto'], errors='coerce').fillna(0)

    # --- ENFORCE STANDARD CONCEPTS (Feedback Fix) ---
    # Ensure all standard concepts exist for both periods and segments, even with 0 value
    required_concepts = [
        "1. (+) Total Facturado",
        "2. (-) Notas de Crédito (01)",
        "3. (+) Nota de Débito (02)",
        "4. (-) Devoluciones (03)",
        "5. (-) Sustituciones (04)",
        "6. Traslado de mercancía (05,06)",
        "7. (-) Anticipo (07)",
        "8. (-) Pagos Aplicados (08/09)",
        "9. (=) Saldo Insoluto PPD",
        "9. (=) Saldo Teórico PUE"
    ]
    
    segments = ["PPD", "PUE"]
    periods = [mes_anterior, mes_actual]
    
    # Create a template DataFrame with all combinations
    template_data = []
    for p in periods:
        for s in segments:
            for c in required_concepts:
                template_data.append({
                    "periodo": p,
                    "segmento": s, 
                    "concepto": c, 
                    "monto": 0.0,
                    # Add dummy values for other columns if needed to avoid NaN issues during merge
                    "company_id": company_id, 
                    "rfc_emisor": "GENERIC",
                    "total": 0.0
                })
                
    df_template = pd.DataFrame(template_data)
    
    if not df_filtrado.empty:
        # Merge actual data into template
        # We perform an outer merge or concatenation, then group by to sum (actual + 0)
        df_combined = pd.concat([df_template, df_filtrado], ignore_index=True)
        # Sum by key columns to merge the 0 placeholders with actual values
        df_final = df_combined.groupby(["periodo", "segmento", "concepto"], as_index=False)["monto"].sum()
    else:
        df_final = df_template

    # Use df_final for the JSON generation
    # df_filtrado = df_final # Reassign for downstream use
    
    # DEBUG: Show what we found
    # st.info(f"DEBUG: Períodos: {mes_anterior} vs {mes_actual} | Registros Totales (Merge): {len(df_final)}")
    
    # DIAGNOSTIC: Show concepts that were actually merged vs required
    # if not df_filtrado.empty:
    #      actual_concepts = df_filtrado['concepto'].unique()
    #      st.text(f"Conceptos en DB: {actual_concepts}")

    if df_final.empty:
        # This shouldn't happen now due to template, but good safety
        st.warning(f"No hay datos para los períodos {mes_anterior} y {mes_actual}")
        return

    # 4. Preparar JSON para React
    # React expects: { mes_anterior, mes_actual, data:Array }
    
    # Ensure numeric types
    if 'monto' in df_final.columns:
        df_final['monto'] = pd.to_numeric(df_final['monto'], errors='coerce').fillna(0)

    data_list = df_final.to_dict(orient='records')
    
    artifact_payload = {
        "mes_anterior": mes_anterior,
        "mes_actual": mes_actual,
        "data": data_list
    }
    
    # 5. Inyectar en HTML y Renderizar
    artifact_path = os.path.join(os.path.dirname(__file__), "matriz_resumen_artifact.html")
    
    if os.path.exists(artifact_path):
        with open(artifact_path, "r", encoding="utf-8") as f:
            html_template = f.read()
            
        # Serialize data safe for HTML injection
        json_payload = json.dumps(artifact_payload, allow_nan=False)
        
        # Injection Script
        injection = f"""
        <script>
            window.data = {json_payload};
            console.log("Matriz Resumen Data Injected:", window.data);
        </script>
        """
        
        # Inject before root or body end
        if '<div id="root"></div>' in html_template:
            final_html = html_template.replace('<div id="root"></div>', f'{injection}<div id="root"></div>')
            
            # Render with Streamlit Components
            components.html(final_html, height=1200, scrolling=True)
            
            # 6. Botón de exportación (Streamlit-side as fallback/convenience)
            col_exp, _ = st.columns([1, 4])
            with col_exp:
                csv = df_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Fuente de Datos (CSV)",
                    data=csv,
                    file_name=f"matriz_fiscal_{mes_anterior}_{mes_actual}.csv",
                    mime="text/csv",
                    key="download_matriz_resumen"
                )
        else:
            st.error("Error: Artifact template invalido (falta #root).")
    else:
        st.error(f"Artifact no encontrado en: {artifact_path}")

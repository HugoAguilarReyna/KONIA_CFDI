import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import os
import json
import pandas as pd

def render_detalle_uuid_inline(df_filtered, sel_year, sel_month, month_labels):
    """
    Renders the original Detalle UUID React artifact integration.
    Moved from app.py to clear up space.
    """
    st.markdown('<div class="section-header">DETALLE DE TRANSACCIONES (UUID) INTERACTIVO</div>', unsafe_allow_html=True)
    
    if not df_filtered.empty:
        # --- DATA PREPARATION FOR REACT ARTIFACT ---
        # Mapping columns to the expected format of the React component
        react_data = []
        
        # Use columns dynamically if available, otherwise use defaults
        has_metodo = 'metodo_pago' in df_filtered.columns
        has_tipo = 'tipo' in df_filtered.columns
        
        # Convert up to 1000 rows for performance in the React component
        for _, row in df_filtered.head(1000).iterrows():
            # Logic for Flow: I=Ingreso (Emitido for us), E=Egreso (NC), P=Pago
            # Assuming business logic context: I=Emitidos (Income), E=Recibidos (Expense/NC)
            tipo_raw = str(row.get('tipo', 'I')).upper()
            flujo = "EMITIDOS" if tipo_raw.startswith('I') else "RECIBIDOS"
            
            # Helper to safely float conversion (handle NaN)
            def safe_float(val):
                try:
                    f = float(val)
                    return 0.0 if np.isnan(f) or np.isinf(f) else f
                except:
                    return 0.0
            
            item = {
                "uuid": str(row.get('uuid', 'N/A')),
                "Segmento": str(row.get('metodo_pago', 'PUE')) if has_metodo else "PUE",
                "Flujo": flujo,
                "1. (+) Total Facturado": safe_float(row.get('total', 0)),
                "2. (-) Notas de Crédito (01)": 0.0,
                "4. (-) Devoluciones (03)": 0.0,
                "7. (-) Anticipo (07)": 0.0,
                "8. (-) Pagos Aplicados (08/09)": 0.0,
                "9. (=) Saldo Acumulado por UUID": safe_float(row.get('total', 0))
            }
            react_data.append(item)

        # --- RENDER REACT ARTIFACT ---
        # Note: path is relative to app.py, so we use app.py's dir if running from there
        # But __file__ here refers to utils_ui.py. 
        # Assuming utils_ui.py is in same dir as app.py and artifact.
        artifact_file = os.path.join(os.path.dirname(__file__), "detalle_uuid_artifact.html")
        
        if os.path.exists(artifact_file):
            # Use utf-8-sig to handle BOM if present, or just utf-8
            with open(artifact_file, "r", encoding="utf-8") as f:
                html_template = f.read()
            
            # Injection of data into the global window object
            # Ensure simpleJSON compatible text
            try:
                data_json = json.dumps(react_data, allow_nan=False)
            except ValueError:
                    # Fallback if allow_nan=False fails (should be caught by safe_float but just in case)
                    data_json = json.dumps(react_data, default=lambda x: 0.0)

            periodo_str = f"{sel_year}-{month_labels.get(sel_month, sel_month)}"
            
            # Replace the generic data with real data via simple script injection
            # We inject window.data and window.periodo before the React app mounts
            injection_script = f"""
            <script>
                window.data = {data_json};
                window.periodo = "{periodo_str}";
                console.log("Data injected successfully: " + window.data.length + " records");
            </script>
            """
            
            # Inject BEFORE the closing body tag or BEFORE the div root to ensure it runs first
            if '<div id="root"></div>' in html_template:
                final_html = html_template.replace('<div id="root"></div>', f'{injection_script}<div id="root"></div>')
                components.html(final_html, height=1000, scrolling=True)
            else:
                st.error("Error: Placeholder 'root' no encontrado en el artifact.")
        else:
            st.warning("⚠️ Componente de visualización ('detalle_uuid_artifact.html') no encontrado.")
            # st.dataframe(df_filtered, use_container_width=True) # Avoid passing df if unnecessary complexity
            st.error("Artifact missing.")
    else:
        st.info("No hay datos para mostrar con los filtros seleccionados.")

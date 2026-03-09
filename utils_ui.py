import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import os
import json
import pandas as pd

def render_detalle_uuid_inline(data_source, sel_year, sel_month, month_labels):
    """
    Renders the original Detalle UUID React artifact integration.
    Updated to use MongoDB-structured data.
    """
    st.markdown('<div class="section-header">DETALLE DE TRANSACCIONES (UUID) INTERACTIVO</div>', unsafe_allow_html=True)
    
    # Preprocesar datos (puede ser una lista de dicts de Mongo o un DF)
    if isinstance(data_source, pd.DataFrame):
        if data_source.empty:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
            return
        raw_docs = data_source.to_dict('records')
    else:
        if not data_source:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
            return
        raw_docs = data_source

    # Mapping to React format
    react_data = []
    for doc in raw_docs[:1000]:  # Cap for performance
        conceptos = doc.get('conceptos', {})
        
        # Helper to extract from concepts or direct keys
        def find_val_robust(pattern, pretty_key):
            # Try raw concepts first
            for k, v in conceptos.items():
                if pattern in k:
                    try: return float(v)
                    except: pass
            
            # Try the pretty_key directly on the doc (in case it was already mapped)
            val = doc.get(pretty_key)
            if val is not None:
                try: return float(val)
                except: pass
            
            return 0.0

        item = {
            "uuid": str(doc.get('uuid', 'N/A')),
            "Segmento": str(doc.get('segmento', doc.get('Segmento', 'PUE'))),
            "Flujo": str(doc.get('flujo', doc.get('Flujo', 'EMITIDOS'))),
            "1. (+) Total Facturado": find_val_robust('Total Facturado', '1. (+) Total Facturado'),
            "2. (-) Notas de Crédito (01)": find_val_robust('Notas de Crédito', '2. (-) Notas de Crédito (01)'),
            "4. (-) Devoluciones (03)": find_val_robust('Devoluciones', '4. (-) Devoluciones (03)'),
            "7. (-) Anticipo (07)": find_val_robust('Anticipo', '7. (-) Anticipo (07)'),
            "8. (-) Pagos Aplicados (08/09)": find_val_robust('Pagos Aplicados', '8. (-) Pagos Aplicados (08/09)'),
            "9. (=) Saldo Acumulado por UUID": float(doc.get('saldo_acumulado', doc.get('9. (=) Saldo Acumulado por UUID', 0)))
        }
        react_data.append(item)

    # --- RENDER REACT ARTIFACT ---
    # Note: path is relative to app.py
    artifact_file = os.path.join(os.path.dirname(__file__), "detalle_uuid_artifact.html")
    
    if os.path.exists(artifact_file):
        with open(artifact_file, "r", encoding="utf-8") as f:
            html_template = f.read()
        
        try:
            data_json = json.dumps(react_data, allow_nan=False)
        except ValueError:
            data_json = json.dumps(react_data, default=lambda x: 0.0)

        periodo_str = f"{sel_year}-{month_labels.get(sel_month, sel_month)}"
        
        injection_script = f"""
        <script>
            window.data = {data_json};
            window.periodo = "{periodo_str}";
            console.log("Data injected successfully: " + window.data.length + " records");
        </script>
        """
        
        if '<div id="root"></div>' in html_template:
            final_html = html_template.replace('<div id="root"></div>', f'{injection_script}<div id="root"></div>')
            components.html(final_html, height=1000, scrolling=True)
        else:
            st.error("Error: Placeholder 'root' no encontrado en el artifact.")
    else:
        st.warning("⚠️ Componente de visualización ('detalle_uuid_artifact.html') no encontrado.")
        st.error("Artifact missing.")

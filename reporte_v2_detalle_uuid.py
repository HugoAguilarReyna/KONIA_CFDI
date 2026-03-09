"""
SOLUCIÓN FINAL SIMPLIFICADA - DETALLE UUID
Búsqueda UUID dentro del tab
Mapeo por periodo
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# 1. FUNCIONES DE DATOS
# ============================================================================

def obtener_datos_detalle_uuid(db, periodo, company_id=None):
    """
    Obtiene datos de fiscal_reports.detalle_uuid filtrados por periodo.
    Soporta:
    - String: "YYYY-MM"
    - Lista: ["YYYY-MM", "YYYY-MM", ...]
    - String: "Anual YYYY"
    """
    collection = db['detalle_uuid']
    
    if isinstance(periodo, list):
        query = {'periodo': {'$in': periodo}}
    elif isinstance(periodo, str) and "Anual" in periodo:
        year = periodo.split(" ")[1]
        query = {'periodo': {'$regex': f'^{year}-'}}
    else:
        query = {'periodo': periodo}
        
    if company_id:
        # Mapeo especial para TENANT_001 (Sandbox) -> BQ_COMPANY_ID
        if company_id == "TENANT_001":
            import os
            bq_cid = os.getenv("BQ_COMPANY_ID")
            if bq_cid:
                company_id = bq_cid
            else:
                # Fallback manual si no lee el env
                company_id = "2"
        
        # Intentar conversión a int si es posible (el esquema usa Int32)
        try:
            query['company_id'] = int(company_id)
        except (ValueError, TypeError):
            query['company_id'] = company_id
    
    docs = list(collection.find(query))
    
    if not docs:
        total_en_col = collection.estimated_document_count()
        if total_en_col == 0:
            st.error(f"⚠️ La colección '{collection.name}' está vacía en la base de datos '{db.name}'.")
        return pd.DataFrame()
    
    data = []
    for doc in docs:
        conceptos = doc.get('conceptos', {})
        
        def find_val(pattern):
            for k, v in conceptos.items():
                if pattern in k:
                    return v
            return 0

        data.append({
            'uuid': doc.get('uuid', ''),
            'segmento': doc.get('segmento', 'PUE'),
            'flujo': doc.get('flujo', 'EMITIDOS'),
            'saldo_acumulado': doc.get('saldo_acumulado', 0),
            'conceptos': conceptos,
            '1. (+) Total Facturado': find_val('Total Facturado'),
            '2. (-) Notas de Crédito (01)': find_val('Notas de Crédito'),
            '4. (-) Devoluciones (03)': find_val('Devoluciones'),
            '7. (-) Anticipo (07)': find_val('Anticipo'),
            '8. (-) Pagos Aplicados (08/09)': find_val('Pagos Aplicados'),
            '9. (=) Saldo Acumulado por UUID': doc.get('saldo_acumulado', 0),
            'periodo': doc.get('periodo', '')
        })
    
    return pd.DataFrame(data)


def mostrar_reporte_uuid_simplificado(db, periodo_str, company_id=None):
    """
    Punto de entrada principal para el Tab de Detalle UUID.
    """
    st.markdown("### Detalle UUID")
    
    # 1. BÚSQUEDA UUID (DENTRO DEL TAB)
    buscar_uuid = st.text_input(
        "Buscar UUID",
        placeholder="Ej: 0000504d-1ba5-4f81-b660...",
        key="buscar_uuid_tab"
    )
    
    try:
        # 2. Obtener datos
        df = obtener_datos_detalle_uuid(db, periodo_str, company_id=company_id)
        
        if not df.empty:
            # 3. Aplicar búsqueda UUID
            if buscar_uuid and buscar_uuid.strip():
                df_filtrado = df[df['uuid'].str.contains(buscar_uuid, case=False, na=False)]
            else:
                df_filtrado = df
            
            if not df_filtrado.empty:
                # 4. Mostrar Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Registros", len(df_filtrado))
                with col2:
                    total_fact = df_filtrado['1. (+) Total Facturado'].sum()
                    st.metric("Total Facturado", f"${total_fact:,.2f}")
                with col3:
                    total_saldo = df_filtrado['9. (=) Saldo Acumulado (08/09) por UUID'].sum()
                    st.metric("Saldo Total", f"${total_saldo:,.2f}")
                
                # 5. Formatear para visualización
                df_display = df_filtrado.copy()
                columnas_moneda = [
                    '1. (+) Total Facturado',
                    '2. (-) Notas de Crédito (01)',
                    '4. (-) Devoluciones (03)',
                    '7. (-) Anticipo (07)',
                    '8. (-) Pagos Aplicados (08/09)',
                    '9. (=) Saldo Acumulado por UUID'
                ]
                
                for col in columnas_moneda:
                    df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}")
                
                # 6. Mostrar tabla
                columnas_mostrar = [col for col in df_display.columns if col != 'periodo']
                st.dataframe(
                    df_display[columnas_mostrar],
                    use_container_width=True,
                    height=500,
                    hide_index=True
                )
                
                st.caption(f"Visualizando {len(df_filtrado)} registros | Período: {periodo_str}")
                
                # 7. Descargar CSV
                csv = df_filtrado[columnas_mostrar].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"detalle_uuid_{periodo_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ No hay resultados para la búsqueda")
        else:
            st.warning(f"⚠️ No hay datos para el período seleccionado: {periodo_str}")
            
    except Exception as e:
        st.error(f"Error al procesar Detalle UUID: {str(e)}")

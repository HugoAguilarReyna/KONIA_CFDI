"""
CSS PREMIUM PARA SIDEBAR HAMBURGUESA (V11)
Secuestra el contenedor stVerticalBlock con el marcador #filter-sidebar-marker
Mantiene colores originales (#667eea -> #764ba2)
"""

SIDEBAR_PREMIUM_CSS = """
<style>
    /* ============================================================================
       1. CONTENEDOR PRINCIPAL (SLIDER)
       ============================================================================ */
    
    /* Contenedor Principal */
    .actual-filter-sidebar {
        position: fixed !important;
        top: 0 !important;
        left: -330px !important; /* Oculto por defecto */
        width: 320px !important;
        height: 100vh !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        z-index: 999999 !important;
        transition: left 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        padding: 80px 20px 20px 20px !important;
        box-shadow: 10px 0 30px rgba(0,0,0,0.3) !important;
        overflow-y: auto !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
        display: block !important;
        color: #FFFFFF !important;
    }

    /* Estado ABIERTO (Toggled via JS) */
    .actual-filter-sidebar.sidebar-open {
        left: 0 !important;
    }

    /* ============================================================================
       2. ORGANIZACIÓN INTERNA Y GLASSMORFISM
       ============================================================================ */
    
    /* Texto base (Blanco) */
    .actual-filter-sidebar, 
    .actual-filter-sidebar p, 
    .actual-filter-sidebar span, 
    .actual-filter-sidebar label {
        color: #FFFFFF !important;
    }


    /* Contenedores de Grupo (Glassmorphism) */
    .premium-filter-container {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin-top: 15px !important;
        margin-bottom: 15px !important;
    }

    /* Labels principales (Títulos de los filtros) */
    .actual-filter-sidebar [data-testid="stWidgetLabel"] p {
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        color: #E2E8F0 !important;
        margin-top: 18px !important; 
        margin-bottom: 6px !important;
    }

    /* Reset para las ETIQUETAS DE OPCIONES (Radio, Checkbox) */
    /* Estas NO deben tener márgenes que las desalineen del círculo/check */
    .actual-filter-sidebar label div[data-testid="stMarkdownContainer"] p {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        display: inline-block !important;
        vertical-align: middle !important;
    }

    /* Alineación vertical del Radio Button */
    .actual-filter-sidebar [data-testid="stRadio"] label {
        align-items: center !important;
        display: flex !important;
    }

    /* Espaciado entre WIDGETS (Bloques raíz) */
    .actual-filter-sidebar [data-testid="stVerticalBlock"] > div[data-testid="element-container"] {
        margin-bottom: 8px !important;
    }
    
    /* Separadores horizontales */
    .actual-filter-sidebar hr {
        margin: 25px 0 !important;
        opacity: 0.2 !important;
    }

    /* ============================================================================
       3. ESTILADO DE COMPONENTES (PILLS & INPUTS)
       ============================================================================ */
    
    /* Pills Base (Botones secundarios) */
    .actual-filter-sidebar button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        padding: 6px 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .actual-filter-sidebar button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }

    /* Estilo para Pills SELECCIONADAS (Active State) - DEFINITIVO */
    /* Usamos los selectores exactos encontrados en la inspección */
    .actual-filter-sidebar button[aria-pressed="true"],
    .actual-filter-sidebar button.st-emotion-cache-1sr539l.e1mwqyj910,
    .actual-filter-sidebar [data-testid="stBaseButton-secondaryPillActive"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border-color: #f7fafc !important;
    }

    /* Forzar el color MORADO en el texto interior (p, span, label) */
    .actual-filter-sidebar button[aria-pressed="true"] p,
    .actual-filter-sidebar button[aria-pressed="true"] span,
    .actual-filter-sidebar button.st-emotion-cache-1sr539l.e1mwqyj910 p,
    .actual-filter-sidebar button.st-emotion-cache-1sr539l.e1mwqyj910 span,
    .actual-filter-sidebar [data-testid="stBaseButton-secondaryPillActive"] p,
    .actual-filter-sidebar [data-testid="stBaseButton-secondaryPillActive"] span {
        color: #764ba2 !important;
        -webkit-text-fill-color: #764ba2 !important;
        font-weight: 800 !important;
    }

    /* Inputs y Selects */
    .actual-filter-sidebar input,
    .actual-filter-sidebar select,
    .actual-filter-sidebar .stSelectbox {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }


    /* ============================================================================
       4. RESET PARA EVITAR COLISIONES
       ============================================================================ */
    
    /* Asegurar que las tarjetas de la app principal NO se vean afectadas */
    /* El selector div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) es lo suficientemente específico */
</style>
"""

def inject_sidebar_css():
    """Inyecta el CSS del Sidebar Premium (Slider)"""
    import streamlit as st
    st.markdown(SIDEBAR_PREMIUM_CSS, unsafe_allow_html=True)

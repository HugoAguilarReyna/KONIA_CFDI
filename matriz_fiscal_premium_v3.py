"""
╔══════════════════════════════════════════════════════════════════╗
║       MATRIZ FISCAL PREMIUM v3.0 — KONIA DESIGN SYSTEM          ║
║   Streamlit + MongoDB Atlas — ClusterAct1 / fiscal_reports       ║
╚══════════════════════════════════════════════════════════════════╝
pip install streamlit pymongo pandas plotly numpy
streamlit run matriz_fiscal_premium_v3.py
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from pymongo import MongoClient

# ══════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Matriz Fiscal Premium v3 | KONIA",
                   page_icon="⚖️", layout="wide",
                   initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════
# CSS — KONIA DESIGN SYSTEM (light / violet)
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box}
.stApp{background:#F4F5FB;font-family:'Outfit',sans-serif}
#MainMenu,footer,header{visibility:hidden}.stDeployButton{display:none}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#5B5BD6 0%,#4747B8 60%,#3A3A9E 100%)!important;border-right:none!important}
[data-testid="stSidebar"]>div{padding-top:0!important}
[data-testid="stSidebar"] *{color:#fff!important}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.18)!important;margin:10px 0}
[data-testid="stSidebar"] .stTextInput input{background:rgba(255,255,255,.12)!important;border:1px solid rgba(255,255,255,.25)!important;border-radius:10px!important;color:#fff!important;font-family:'Outfit',sans-serif!important}
[data-testid="stSidebar"] .stTextInput input::placeholder{color:rgba(255,255,255,.5)!important}
[data-testid="stSidebar"] .stSelectbox>div>div{background:rgba(255,255,255,.12)!important;border:1px solid rgba(255,255,255,.25)!important;border-radius:10px!important}
[data-testid="stSidebar"] .stMultiSelect>div>div{background:rgba(255,255,255,.12)!important;border:1px solid rgba(255,255,255,.25)!important;border-radius:10px!important}
[data-testid="stSidebar"] .stRadio>div>label{background:rgba(255,255,255,.1)!important;padding:6px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.2);transition:all .2s;cursor:pointer;margin:2px}
[data-testid="stSidebar"] .stCheckbox>label{background:rgba(255,255,255,.08);padding:5px 10px;border-radius:8px;border:1px solid rgba(255,255,255,.15);transition:all .2s;width:100%;display:block}
.main .block-container{padding:24px 32px!important;max-width:100%!important}
[data-testid="metric-container"]{background:#fff;border-radius:14px;padding:18px 22px;border:1px solid #EDEEF8;box-shadow:0 2px 12px rgba(91,91,214,.08);transition:all .25s ease}
[data-testid="metric-container"]:hover{box-shadow:0 8px 28px rgba(91,91,214,.16);transform:translateY(-2px)}
[data-testid="stMetricLabel"]{font-family:'Outfit',sans-serif!important;font-size:.78rem!important;font-weight:600!important;text-transform:uppercase;letter-spacing:.08em;color:#6B7280!important}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:1.45rem!important;font-weight:600!important;color:#1E1E3F!important}
.stTabs [data-baseweb="tab-list"]{background:#fff;border-radius:12px 12px 0 0;padding:4px 8px 0;border-bottom:2px solid #EDEEF8;gap:4px}
.stTabs [data-baseweb="tab"]{font-family:'Outfit',sans-serif;font-weight:500;font-size:.88rem;color:#6B7280;border-radius:8px 8px 0 0;padding:10px 20px;border:none;transition:all .2s}
.stTabs [aria-selected="true"]{color:#5B5BD6!important;border-bottom:3px solid #5B5BD6!important;font-weight:600!important;background:rgba(91,91,214,.05)!important}
.stButton>button{background:#fff;border:1.5px solid #5B5BD6;color:#5B5BD6;border-radius:10px;font-family:'Outfit',sans-serif;font-weight:600;font-size:.88rem;padding:8px 20px;transition:all .25s ease}
.stButton>button:hover{background:#5B5BD6;color:#fff;box-shadow:0 6px 20px rgba(91,91,214,.35);transform:translateY(-1px)}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#5B5BD6,#7C7CF0);color:#fff;border:none;box-shadow:0 4px 14px rgba(91,91,214,.35)}
.konia-card{background:#fff;border-radius:14px;padding:22px 24px;border:1px solid #EDEEF8;box-shadow:0 2px 12px rgba(91,91,214,.08);margin-bottom:16px;transition:all .25s ease}
.konia-card:hover{box-shadow:0 8px 28px rgba(91,91,214,.15);transform:translateY(-2px)}
.kpi-card{background:#fff;border-radius:14px;padding:20px 22px;border:1px solid #EDEEF8;border-left:4px solid var(--kpi-c,#5B5BD6);box-shadow:0 2px 12px rgba(91,91,214,.08);transition:all .25s ease;height:100%;min-height:120px}
.kpi-card:hover{box-shadow:0 8px 28px rgba(91,91,214,.15);transform:translateY(-2px)}
.kpi-label{font-family:'Outfit',sans-serif;font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#6B7280;margin-bottom:8px}
.kpi-value{font-family:'JetBrains Mono',monospace;font-size:1.45rem;font-weight:600;color:#1E1E3F;margin-bottom:6px;line-height:1.2;word-break:break-all}
.kpi-delta{font-family:'JetBrains Mono',monospace;font-size:.75rem;font-weight:500;display:inline-flex;align-items:center;gap:3px;padding:3px 8px;border-radius:20px}
.kpi-delta.pos{background:#ECFDF5;color:#059669}
.kpi-delta.neg{background:#FEF2F2;color:#DC2626}
.kpi-delta.neu{background:#EEF2FF;color:#5B5BD6}
.kpi-sub{font-family:'Outfit',sans-serif;font-size:.72rem;color:#9CA3AF;margin-top:5px}
.kpi-icon{float:right;font-size:1.5rem;opacity:.18;margin-top:-2px}
.nota-global{background:linear-gradient(135deg,#FEF3C7,#FDE68A);border:1px solid #F59E0B;border-left:4px solid #F59E0B;border-radius:10px;padding:11px 16px;margin-bottom:18px;font-family:'Outfit',sans-serif;font-size:.8rem;color:#92400E;display:flex;align-items:center;gap:10px}
.section-hdr{font-family:'Syne',sans-serif;font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#9CA3AF;margin:22px 0 12px;padding-bottom:7px;border-bottom:1px solid #EDEEF8}
.sb-hdr{background:rgba(255,255,255,.12);border-bottom:1px solid rgba(255,255,255,.15);padding:20px 16px;margin-bottom:6px}
.sb-title{font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:800;color:#fff;letter-spacing:.06em}
.sb-sub{font-family:'Outfit',sans-serif;font-size:.7rem;color:rgba(255,255,255,.6);margin-top:2px;text-transform:uppercase;letter-spacing:.1em}
.sb-sec{font-family:'Outfit',sans-serif;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.45);margin:14px 0 6px;padding:0 2px}
.live-badge{display:inline-flex;align-items:center;gap:5px;background:rgba(16,185,129,.15);border:1px solid rgba(16,185,129,.4);border-radius:20px;padding:3px 10px;font-size:.68rem;font-weight:700;color:#10B981;text-transform:uppercase;letter-spacing:.08em}
.live-badge::before{content:'';width:6px;height:6px;background:#10B981;border-radius:50%;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.8)}}
.pg-hdr{background:#fff;border-radius:16px;padding:20px 26px;border:1px solid #EDEEF8;box-shadow:0 2px 12px rgba(91,91,214,.08);margin-bottom:22px}
.pg-title{font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:#1E1E3F}
.pg-title span{color:#5B5BD6}
.pg-sub{font-family:'Outfit',sans-serif;font-size:.78rem;color:#9CA3AF;margin-top:3px}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MONGODB
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def init_db():
    try:
        uri = st.secrets.get("MONGO_URI","mongodb+srv://user:pass@clusteract1.xxxxx.mongodb.net/")
        c = MongoClient(uri, serverSelectionTimeoutMS=4000)
        c.admin.command("ping")
        return c["fiscal_reports"]
    except Exception as e:
        return None

db = init_db()

# ══════════════════════════════════════════════════════════════════
# MOCK DATA
# ══════════════════════════════════════════════════════════════════
def _mock_periodos():
    return [
        {"periodo":"2026-01","id_tiempo":202601,"nombre_mes_es":"ENERO","anio":2026,"mes":1,"trimestre":1,"rango_mes_estandar":"Jan 01 - Jan 31"},
        {"periodo":"2025-12","id_tiempo":202512,"nombre_mes_es":"DICIEMBRE","anio":2025,"mes":12,"trimestre":4,"rango_mes_estandar":"Dec 01 - Dec 31"},
        {"periodo":"2025-11","id_tiempo":202511,"nombre_mes_es":"NOVIEMBRE","anio":2025,"mes":11,"trimestre":4,"rango_mes_estandar":"Nov 01 - Nov 30"},
    ]

def _mock_resumen(periodo):
    base_ene = [
        ("PPD","1. (+) Total Facturado",98049668.38),("PPD","2. (-) Notas de Crédito (01)",-36576.69),
        ("PPD","3. (+) Nota de Débito (02)",2298.77),("PPD","4. (-) Devoluciones (03)",0.0),
        ("PPD","5. (-) Sustituciones (04)",0.0),("PPD","7. (-) Anticipo (07)",-3099.42),
        ("PPD","8. (-) Pagos Aplicados (08/09)",-120576780.60),("PPD","9. (=) Saldo insoluto PPD",-22564489.56),
        ("PUE","1. (+) Total Facturado",31931749.19),("PUE","2. (-) Notas de Crédito (01)",-149611.41),
        ("PUE","3. (+) Nota de Débito (02)",0.0),("PUE","7. (-) Anticipo (07)",-232414.90),
        ("PUE","8. (-) Pagos Aplicados (08/09)",0.0),("PUE","9. (=) Saldo Teórico PUE",31549722.88),
    ]
    base_dic = [
        ("PPD","1. (+) Total Facturado",84900000.0),("PPD","2. (-) Notas de Crédito (01)",-166000.0),
        ("PPD","7. (-) Anticipo (07)",-2800.0),("PPD","8. (-) Pagos Aplicados (08/09)",-108000000.0),
        ("PPD","9. (=) Saldo insoluto PPD",-19800000.0),
        ("PUE","1. (+) Total Facturado",20900000.0),("PUE","7. (-) Anticipo (07)",-195000.0),
        ("PUE","9. (=) Saldo Teórico PUE",0.0),
    ]
    rows = base_dic if periodo == "2025-12" else base_ene
    return pd.DataFrame([{"periodo":periodo,"company_id":2,"segmento":s,"concepto":c,"monto":m} for s,c,m in rows])

def _mock_detalle(periodo):
    import random, uuid as uu
    conceptos=["1. (+) Total Facturado","2. (-) Notas de Crédito (01)","7. (-) Anticipo (07)","8. (-) Pagos Aplicados (08/09)"]
    random.seed(42)
    rows=[{"periodo":periodo,"company_id":2,"uuid_raiz":str(uu.uuid4())[:8],
           "uuid_relacionado":str(uu.uuid4())[:8],"tipo_relacion":random.choice(["01","04","08"]),
           "concepto":random.choice(conceptos),"fecha":f"{periodo}-{random.randint(1,28):02d}",
           "monto":round(random.uniform(-500000,800000),2),"segmento":random.choice(["PPD","PUE"])} for _ in range(40)]
    return pd.DataFrame(rows)

# ══════════════════════════════════════════════════════════════════
# DATA FETCHERS
# ══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300,show_spinner=False)
def get_periodos():
    if db is None: return _mock_periodos()
    try:
        d=list(db.dim_tiempo.find({},{"periodo":1,"id_tiempo":1,"nombre_mes_es":1,"anio":1,"mes":1,"trimestre":1,"rango_mes_estandar":1}).sort("id_tiempo",-1).limit(36))
        return d if d else _mock_periodos()
    except: return _mock_periodos()

@st.cache_data(ttl=120,show_spinner=False)
def get_resumen(periodo,company_id=2,segs=None):
    if db is None: return _mock_resumen(periodo)
    try:
        q={"periodo":periodo,"company_id":company_id}
        if segs: q["segmento"]={"$in":segs}
        d=list(db.matriz_resumen.find(q,{"_id":0}))
        return pd.DataFrame(d) if d else _mock_resumen(periodo)
    except: return _mock_resumen(periodo)

@st.cache_data(ttl=120,show_spinner=False)
def get_detalle(periodo,company_id=2):
    if db is None: return _mock_detalle(periodo)
    try:
        d=list(db.detalle_uuid.find({"periodo":periodo,"company_id":company_id},{"_id":0}).limit(500))
        return pd.DataFrame(d) if d else _mock_detalle(periodo)
    except: return _mock_detalle(periodo)

# ══════════════════════════════════════════════════════════════════
# FORMATEO
# ══════════════════════════════════════════════════════════════════
def fm(v, modo="kpi"):
    if v is None or (isinstance(v,float) and np.isnan(v)): return "$0.00"
    if modo=="g":
        if abs(v)>=1e6: return f"${v/1e6:.1f}M"
        if abs(v)>=1e3: return f"${v/1e3:.1f}K"
        return f"${v:,.0f}"
    return f"${v:,.2f}"

def var_pct(a,b):
    if b and b!=0: return (a-b)/abs(b)*100
    return None

def badge(pct,inv=False):
    if pct is None: return '<span class="kpi-delta neu">N/D</span>'
    good=(pct>=0) if not inv else (pct<=0)
    cls="pos" if good else "neg"
    ar="↑" if pct>=0 else "↓"
    return f'<span class="kpi-delta {cls}">{ar} {abs(pct):.1f}%</span>'

# ══════════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════════
def calc_kpis(da,db_ant):
    def g(df,seg,kw):
        if df is None or df.empty: return 0.0
        m=df[df["segmento"].str.upper().eq(seg.upper())&df["concepto"].str.contains(kw,case=False,na=False)]
        return m["monto"].sum() if not m.empty else 0.0
    a={
        "fp":g(da,"PPD","Total Facturado"),"fu":g(da,"PUE","Total Facturado"),
        "ncp":g(da,"PPD","Notas de Crédito"),"ncu":g(da,"PUE","Notas de Crédito"),
        "ndp":g(da,"PPD","Nota de Débito"),"ndu":g(da,"PUE","Nota de Débito"),
        "devp":g(da,"PPD","Devoluciones"),"susp":g(da,"PPD","Sustituciones"),
        "ap":g(da,"PPD","Anticipo"),"au":g(da,"PUE","Anticipo"),
        "pp":g(da,"PPD","Pagos Aplicados"),"pu":g(da,"PUE","Pagos Aplicados"),
        "sp":g(da,"PPD","Saldo insoluto PPD"),"su":g(da,"PUE","Saldo"),
    }
    b={"f":g(db_ant,"PPD","Total Facturado")+g(db_ant,"PUE","Total Facturado"),
       "nc":g(db_ant,"PPD","Notas de Crédito")+g(db_ant,"PUE","Notas de Crédito"),
       "p":g(db_ant,"PPD","Pagos Aplicados")+g(db_ant,"PUE","Pagos Aplicados"),
       "s":g(db_ant,"PPD","Saldo insoluto PPD")+g(db_ant,"PUE","Saldo")} if db_ant is not None else {}
    k={
        "fact":a["fp"]+a["fu"],"saldo":a["sp"]+a["su"],
        "pagos":abs(a["pp"])+abs(a["pu"]),"ant":abs(a["ap"])+abs(a["au"]),
        "nc":abs(a["ncp"])+abs(a["ncu"]),"nd":a["ndp"]+a["ndu"],
        "dev":abs(a["devp"])+abs(a["susp"]),"ap_raw":a["ap"],"au_raw":a["au"],
        "sp":a["sp"],"su":a["su"],
        "vf":var_pct(a["fp"]+a["fu"],b.get("f")),
        "vnc":var_pct(abs(a["ncp"]+a["ncu"]),abs(b.get("nc",0))),
        "vp":var_pct(abs(a["pp"]+a["pu"]),abs(b.get("p",0))),
        "vs":var_pct(a["sp"]+a["su"],b.get("s")),
    }
    return k

# ══════════════════════════════════════════════════════════════════
# PLOTLY DEFAULTS
# ══════════════════════════════════════════════════════════════════
PB=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit",color="#374151",size=12),
        margin=dict(l=12,r=12,t=40,b=12),
        hoverlabel=dict(bgcolor="white",font_size=13,font_family="JetBrains Mono",bordercolor="#EDEEF8"))
CP="#F59E0B"; CU="#5B5BD6"; CA="#06B6D4"; CT="#10B981"; GR="rgba(0,0,0,.04)"

# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sb-hdr"><div class="sb-title">⚖️ KONIA</div><div class="sb-sub">Panel Fiscal Premium</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="sb-sec">FILTROS</div>',unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="sb-sec">Tipo Comprobante</div>',unsafe_allow_html=True)
    tc1,tc2=st.columns(2)
    with tc1:
        cb_eg=st.checkbox("Egreso",value=True,key="cb_eg")
        cb_nm=st.checkbox("Nómina",value=False,key="cb_nm")
    with tc2:
        cb_in=st.checkbox("Ingreso",value=True,key="cb_in")
        cb_pg=st.checkbox("Pago",value=False,key="cb_pg")
    st.markdown("---")

    st.markdown('<div class="sb-sec">Método de Pago</div>',unsafe_allow_html=True)
    mp1,mp2=st.columns(2)
    with mp1: cb_ppd=st.checkbox("PPD",value=True,key="cb_ppd")
    with mp2: cb_pue=st.checkbox("PUE",value=True,key="cb_pue")
    segs=[s for s,b in [("PPD",cb_ppd),("PUE",cb_pue)] if b]
    st.markdown("---")

    st.markdown('<div class="sb-sec">🔍 Buscar Concepto / Descripción</div>',unsafe_allow_html=True)
    srch=st.text_input("B",placeholder="UUID, concepto...",label_visibility="collapsed",key="srch")
    st.markdown("---")

    st.markdown('<div class="sb-sec">Agrupación Temporal</div>',unsafe_allow_html=True)
    agrup=st.radio("A",["DIARIO","SEMANAL","MENSUAL"],index=2,horizontal=True,label_visibility="collapsed",key="agrup")
    st.markdown("---")

    st.markdown('<div class="sb-sec">📅 Periodo</div>',unsafe_allow_html=True)
    periodos_db=get_periodos()
    per_sel=st.selectbox("P",options=periodos_db,
        format_func=lambda p:f"{p['nombre_mes_es']} {p['anio']} ({p['rango_mes_estandar']})",
        index=0,label_visibility="collapsed",key="per_sel")
    st.markdown("---")

    st.markdown('<div class="sb-sec">🏷️ Concepto Fiscal</div>',unsafe_allow_html=True)
    CONCS=["1. (+) Total Facturado","2. (-) Notas de Crédito (01)","3. (+) Nota de Débito (02)",
           "4. (-) Devoluciones (03)","5. (-) Sustituciones (04)","7. (-) Anticipo (07)",
           "8. (-) Pagos Aplicados (08/09)","9. (=) Saldo Insoluto"]
    conc_sel=st.multiselect("C",options=CONCS,default=CONCS,placeholder="Todos",label_visibility="collapsed",key="conc_sel")
    st.markdown("---")

    st.markdown('<div class="sb-sec">👤 Cliente / RFC</div>',unsafe_allow_html=True)
    rfc_txt=st.text_input("R",placeholder="RFC o razón social...",label_visibility="collapsed",key="rfc_txt")
    st.markdown("---")

    st.markdown('<div class="sb-sec">📋 Uso de CFDI</div>',unsafe_allow_html=True)
    cfdi_sel=st.multiselect("CF",options=["G01 - Adq. mercancías","G03 - Gastos general","I02 - Devoluciones","P01 - Por definir"],
        default=[],placeholder="Todos los usos",label_visibility="collapsed",key="cfdi_sel")
    st.markdown("---")

    st.markdown('<div class="sb-sec">💰 Rango de Montos</div>',unsafe_allow_html=True)
    monto_rng=st.slider("M",0,200_000_000,(0,200_000_000),500_000,format="$%d",label_visibility="collapsed",key="monto_rng")
    st.markdown("---")

    bc1,bc2=st.columns(2)
    with bc1: apply_btn=st.button("✅ Aplicar",use_container_width=True,type="primary",key="apply_btn")
    with bc2:
        if st.button("🗑️ Limpiar",use_container_width=True,key="clear_btn"):
            st.cache_data.clear(); st.rerun()

    st.markdown('<br><div style="text-align:center;opacity:.4;font-size:.66rem;font-family:Outfit,sans-serif;">Matriz Fiscal Premium v3.0<br>KONIA © 2026</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# DATOS
# ══════════════════════════════════════════════════════════════════
periodo_act = per_sel["periodo"]
periodo_ant = periodos_db[1]["periodo"] if len(periodos_db)>1 else None

with st.spinner("Cargando datos..."):
    df_act  = get_resumen(periodo_act, segs=segs if segs else None)
    df_ant  = get_resumen(periodo_ant) if periodo_ant else None
    df_det  = get_detalle(periodo_act)

if srch and not df_det.empty:
    df_det=df_det[df_det.apply(lambda r:srch.lower() in str(r).lower(),axis=1)]

K=calc_kpis(df_act,df_ant)

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="pg-hdr" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
  <div>
    <div class="pg-title">Matriz Fiscal <span>Premium</span></div>
    <div class="pg-sub">Análisis fiscal en tiempo real · {per_sel['nombre_mes_es']} {per_sel['anio']} · {per_sel['rango_mes_estandar']}</div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <span class="live-badge">LIVE</span>
    <div style="text-align:right;">
      <div style="font-size:.7rem;color:#9CA3AF;font-family:Outfit,sans-serif;">Actualizado</div>
      <div style="font-size:.9rem;font-weight:600;color:#1E1E3F;font-family:'JetBrains Mono',monospace;">{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
    </div>
  </div>
</div>
""",unsafe_allow_html=True)

# NOTA GLOBAL
st.markdown('<div class="nota-global">⚠️ <strong>Interpretación:</strong> Cifras negativas en <em>Saldo Insoluto</em> y <em>Anticipos</em> son pasivos (saldo a favor de clientes). Los Pagos Aplicados se muestran en valor absoluto. Anticipos = categoría separada.</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# KPIs FILA 1
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="section-hdr">📊 Indicadores Clave de Desempeño</div>',unsafe_allow_html=True)
k1,k2,k3,k4=st.columns(4)

with k1:
    st.markdown(f"""<div class="kpi-card" style="--kpi-c:#5B5BD6;">
        <span class="kpi-icon">📄</span>
        <div class="kpi-label">Total Facturado</div>
        <div class="kpi-value">{fm(K['fact'])}</div>
        {badge(K['vf'])}
        <div class="kpi-sub">PPD + PUE · vs mes anterior</div>
    </div>""",unsafe_allow_html=True)

with k2:
    sc="#EF4444" if K['saldo']<0 else "#10B981"
    st.markdown(f"""<div class="kpi-card" style="--kpi-c:{sc};">
        <span class="kpi-icon">⚖️</span>
        <div class="kpi-label">Saldo Insoluto Total</div>
        <div class="kpi-value" style="color:{sc};">{fm(K['saldo'])}</div>
        {badge(K['vs'],inv=True)}
        <div class="kpi-sub">Saldo a favor clientes (pasivo)</div>
    </div>""",unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div class="kpi-card" style="--kpi-c:#10B981;">
        <span class="kpi-icon">✅</span>
        <div class="kpi-label">Pagos Aplicados</div>
        <div class="kpi-value" style="color:#10B981;">{fm(K['pagos'])}</div>
        {badge(K['vp'])}
        <div class="kpi-sub">PPD + PUE · flujo de cobro</div>
    </div>""",unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div class="kpi-card" style="--kpi-c:#06B6D4;">
        <span class="kpi-icon">🎯</span>
        <div class="kpi-label">Anticipos Recibidos</div>
        <div class="kpi-value" style="color:#06B6D4;">{fm(K['ant'])}</div>
        <span class="kpi-delta neu">PPD + PUE</span>
        <div class="kpi-sub">Pendientes de aplicar</div>
    </div>""",unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)

# KPIs FILA 2
k5,k6,k7,k8=st.columns(4)

with k5:
    st.markdown(f"""<div class="kpi-card" style="--kpi-c:#EF4444;">
        <span class="kpi-icon">📋</span>
        <div class="kpi-label">Notas de Crédito</div>
        <div class="kpi-value" style="color:#EF4444;">-{fm(K['nc'])}</div>
        {badge(K['vnc'],inv=True)}
        <div class="kpi-sub">Ajuste facturación (C01)</div>
    </div>""",unsafe_allow_html=True)

with k6:
    nc2="#5B5BD6" if K['nd']>0 else "#6B7280"
    st.markdown(f"""<div class="kpi-card" style="--kpi-c:{nc2};">
        <span class="kpi-icon">📝</span>
        <div class="kpi-label">Notas de Débito</div>
        <div class="kpi-value">{fm(K['nd'])}</div>
        <span class="kpi-delta pos">Cargo adicional</span>
        <div class="kpi-sub">PPD + PUE · concepto 02</div>
    </div>""",unsafe_allow_html=True)

with k7:
    st.markdown(f"""<div class="kpi-card" style="--kpi-c:#9CA3AF;">
        <span class="kpi-icon">🔄</span>
        <div class="kpi-label">Devoluciones / Sust.</div>
        <div class="kpi-value" style="color:#9CA3AF;">{fm(K['dev'])}</div>
        <span class="kpi-delta neu">{'Sin movimientos' if K['dev']==0 else 'Con movimientos'}</span>
        <div class="kpi-sub">Conceptos 03 y 04</div>
    </div>""",unsafe_allow_html=True)

with k8:
    sna=K['ap_raw']+K['au_raw']
    st.markdown(f"""<div class="kpi-card" style="--kpi-c:#F59E0B;">
        <span class="kpi-icon">💧</span>
        <div class="kpi-label">Saldo Neto Anticipos</div>
        <div class="kpi-value" style="color:#F59E0B;">{fm(sna)}</div>
        <span class="kpi-delta neg">Impacto liquidez</span>
        <div class="kpi-sub">Anticipos recibidos neto</div>
    </div>""",unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════
tab1,tab2,tab3=st.tabs(["📊 Matriz Resumen (Premium)","📈 Análisis Gráfico","🔍 Detalle Transaccional (Original)"])

# ── TAB 1: TABLA ──────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-hdr">📋 Matriz Financiera Detallada</div>',unsafe_allow_html=True)
    if not df_act.empty:
        try:
            piv=df_act.pivot_table(index="concepto",columns="segmento",values="monto",aggfunc="sum").reset_index()
            for c in ["PPD","PUE"]:
                if c not in piv.columns: piv[c]=0.0
            piv["TOTAL GLOBAL"]=piv.get("PPD",0)+piv.get("PUE",0)
            disp=piv[["concepto","PPD","PUE","TOTAL GLOBAL"]].copy()
            for c in ["PPD","PUE","TOTAL GLOBAL"]: disp[c]=disp[c].apply(fm)
            disp.columns=["CONCEPTO FISCAL","PPD","PUE","TOTAL GLOBAL"]
            st.dataframe(disp,use_container_width=True,height=420,
                column_config={"CONCEPTO FISCAL":st.column_config.TextColumn(width="large"),
                               "PPD":st.column_config.TextColumn(width="medium"),
                               "PUE":st.column_config.TextColumn(width="medium"),
                               "TOTAL GLOBAL":st.column_config.TextColumn(width="medium")})
        except: st.dataframe(df_act,use_container_width=True)
    else: st.info("Sin datos para el periodo.")

# ── TAB 2: GRÁFICAS ────────────────────────────────────────────────
with tab2:

    # G1: Facturación apilada + tendencia
    st.markdown('<div class="section-hdr">📊 Facturación Total PPD vs PUE</div>',unsafe_allow_html=True)
    plabs,fppd_v,fpue_v,tots=[],[],[],[]
    for p in reversed(periodos_db[:2]):
        _d=get_resumen(p["periodo"])
        def _f(df,seg):
            m=df[(df["segmento"]==seg)&df["concepto"].str.contains("Total Facturado",na=False)]
            return m["monto"].sum() if not m.empty else 0
        fp=_f(_d,"PPD"); fu=_f(_d,"PUE")
        plabs.append(f"{p['nombre_mes_es'][:3]} {p['anio']}")
        fppd_v.append(fp); fpue_v.append(fu); tots.append(fp+fu)
    vars_=[None]+[var_pct(tots[i],tots[i-1]) for i in range(1,len(tots))]

    fig1=go.Figure()
    fig1.add_trace(go.Bar(name="PPD",x=plabs,y=fppd_v,marker=dict(color=CP,line=dict(color="white",width=2)),
        text=[fm(v,"g") for v in fppd_v],textposition="inside",textfont=dict(color="white",size=13,family="JetBrains Mono"),
        hovertemplate="<b>PPD %{x}</b><br>$%{y:,.2f}<extra></extra>"))
    fig1.add_trace(go.Bar(name="PUE",x=plabs,y=fpue_v,marker=dict(color=CU,line=dict(color="white",width=2)),
        text=[fm(v,"g") for v in fpue_v],textposition="inside",textfont=dict(color="white",size=13,family="JetBrains Mono"),
        hovertemplate="<b>PUE %{x}</b><br>$%{y:,.2f}<extra></extra>"))
    fig1.add_trace(go.Scatter(name="Tendencia",x=plabs,y=tots,mode="lines+markers+text",
        line=dict(color=CT,width=3,dash="dot"),marker=dict(size=10,color=CT,line=dict(color="white",width=2)),
        text=[""]+[f"+{v:.1f}%" if v and v>=0 else (f"{v:.1f}%" if v else "") for v in vars_[1:]],
        textposition="top center",textfont=dict(color=CT,size=14,family="JetBrains Mono"),
        hovertemplate="<b>Total %{x}</b><br>$%{y:,.2f}<extra></extra>"))
    fig1.update_layout(barmode="stack",title=dict(text="Facturación Total — Barras Apiladas PPD/PUE con Tendencia",
        font=dict(family="Syne",size=14,color="#1E1E3F")),
        xaxis=dict(showgrid=False,title=""),yaxis=dict(showgrid=True,gridcolor=GR,tickformat="$,.0f"),
        legend=dict(orientation="h",y=1.08,x=0,font=dict(family="Outfit")),**PB,height=380)
    st.plotly_chart(fig1,use_container_width=True,key="g1")

    # G2 + G3 lado a lado
    gc1,gc2=st.columns(2)

    with gc1:
        st.markdown('<div class="section-hdr">📉 Saldos Insolutos por Método de Pago</div>',unsafe_allow_html=True)
        sp_v,su_v,sa_v=[],[],[]
        for p in reversed(periodos_db[:2]):
            _d=get_resumen(p["periodo"])
            def _s(df,seg,kw):
                m=df[(df["segmento"]==seg)&df["concepto"].str.contains(kw,na=False)]
                return m["monto"].sum() if not m.empty else 0.0
            sp_v.append(_s(_d,"PPD","Saldo insoluto"))
            su_v.append(_s(_d,"PUE","Saldo"))
            sa_v.append(-(abs(_s(_d,"PPD","Anticipo"))+abs(_s(_d,"PUE","Anticipo"))))

        fig2=go.Figure()
        fig2.add_trace(go.Bar(name="PPD Insoluto",x=plabs,y=sp_v,marker=dict(color=CP,line=dict(color="white",width=1.5)),
            text=[fm(v,"g") for v in sp_v],textposition="outside",textfont=dict(color="#374151",size=11,family="JetBrains Mono"),
            hovertemplate="<b>PPD %{x}</b><br>$%{y:,.2f}<extra></extra>"))
        fig2.add_trace(go.Bar(name="PUE Insoluto",x=plabs,y=su_v,marker=dict(color=CU,line=dict(color="white",width=1.5)),
            text=[fm(v,"g") for v in su_v],textposition="outside",textfont=dict(color="#374151",size=11,family="JetBrains Mono"),
            hovertemplate="<b>PUE %{x}</b><br>$%{y:,.2f}<extra></extra>"))
        fig2.add_trace(go.Bar(name="Anticipos",x=plabs,y=sa_v,marker=dict(color=CA,line=dict(color="white",width=1.5)),
            text=[fm(v,"g") for v in sa_v],textposition="outside",textfont=dict(color="#374151",size=11,family="JetBrains Mono"),
            hovertemplate="<b>Anticipos %{x}</b><br>$%{y:,.2f}<extra></extra>"))
        fig2.update_layout(barmode="group",
            title=dict(text="Saldos Insolutos por Método de Pago<br><sub>Cifras negativas = saldo a favor de clientes</sub>",
                font=dict(family="Syne",size=13,color="#1E1E3F")),
            xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor=GR,tickformat="$,.0f",
                zeroline=True,zerolinecolor="#E5E7EB",zerolinewidth=1.5),
            legend=dict(orientation="h",y=1.18,font=dict(family="Outfit",size=11)),**PB,height=360)
        st.plotly_chart(fig2,use_container_width=True,key="g2")

    with gc2:
        st.markdown('<div class="section-hdr">🍩 Composición de Saldos — Donut</div>',unsafe_allow_html=True)
        sp_abs=abs(K["sp"]); su_abs=abs(K["su"]); sa_abs=K["ant"]
        tot_comp=sp_abs+su_abs+sa_abs
        # ⚠️ FIX: "PUE" nunca "PUC"
        fig3=go.Figure(go.Pie(
            labels=["PPD","PUE","Anticipos"],values=[sp_abs,su_abs,sa_abs],
            hole=0.62,marker=dict(colors=[CP,CU,CA],line=dict(color="white",width=3)),
            textinfo="label+percent",textfont=dict(family="Outfit",size=13,color="#374151"),
            customdata=[[fm(v)] for v in [sp_abs,su_abs,sa_abs]],
            hovertemplate="<b>%{label}</b><br>%{customdata[0]}<br>%{percent}<extra></extra>"))
        fig3.add_annotation(text=f"<b>Total</b><br>{fm(tot_comp,'g')}",x=0.5,y=0.5,showarrow=False,
            font=dict(size=14,color="#1E1E3F",family="JetBrains Mono"),align="center")
        fig3.update_layout(title=dict(text=f"Composición · {per_sel['nombre_mes_es']} {per_sel['anio']}",
            font=dict(family="Syne",size=13,color="#1E1E3F")),
            legend=dict(orientation="v",x=0.82,y=0.5,font=dict(family="Outfit",size=12),itemsizing="constant"),
            **PB,height=360)
        st.plotly_chart(fig3,use_container_width=True,key="g3")

    # G4: Movimientos del Período
    st.markdown('<div class="section-hdr">📊 Movimientos del Período — Comparativa Mensual</div>',unsafe_allow_html=True)
    cmp_lbs=["Facturación\nTotal","Notas de\nCrédito","Notas de\nDébito","Anticipos\nRecibidos","Pagos\nAplicados"]

    def _ext(df):
        def _s(seg,kw):
            if df is None or df.empty: return 0.0
            m=df[(df["segmento"]==seg)&df["concepto"].str.contains(kw,na=False)]
            return m["monto"].sum() if not m.empty else 0.0
        return [abs(_s("PPD","Total Facturado"))+abs(_s("PUE","Total Facturado")),
                abs(_s("PPD","Notas de Crédito"))+abs(_s("PUE","Notas de Crédito")),
                abs(_s("PPD","Nota de Débito"))+abs(_s("PUE","Nota de Débito")),
                abs(_s("PPD","Anticipo"))+abs(_s("PUE","Anticipo")),
                abs(_s("PPD","Pagos Aplicados"))+abs(_s("PUE","Pagos Aplicados"))]

    va=_ext(df_ant); vb=_ext(df_act)
    la=periodos_db[1]["nombre_mes_es"][:3]+f" {periodos_db[1]['anio']}" if len(periodos_db)>1 else "Ant."
    lb=per_sel["nombre_mes_es"][:3]+f" {per_sel['anio']}"

    fig4=go.Figure()
    fig4.add_trace(go.Bar(name=la,x=cmp_lbs,y=va,
        marker=dict(color="rgba(91,91,214,.3)",line=dict(color=CU,width=2)),
        text=[fm(v,"g") for v in va],textposition="outside",textfont=dict(color=CU,size=11,family="JetBrains Mono"),
        hovertemplate=f"<b>%{{x}}</b><br>{la}: $%{{y:,.2f}}<extra></extra>"))
    fig4.add_trace(go.Bar(name=lb,x=cmp_lbs,y=vb,
        marker=dict(color="rgba(91,91,214,.85)",line=dict(color=CU,width=2)),
        text=[fm(v,"g") for v in vb],textposition="outside",textfont=dict(color="#1E1E3F",size=11,family="JetBrains Mono"),
        hovertemplate=f"<b>%{{x}}</b><br>{lb}: $%{{y:,.2f}}<extra></extra>"))
    for i,(a_,b_) in enumerate(zip(va,vb)):
        if a_ and a_!=0:
            p_=var_pct(b_,a_)
            if p_ is not None:
                col="#10B981" if p_>=0 else "#EF4444"
                fig4.add_annotation(x=cmp_lbs[i],y=max(a_,b_)*1.18,
                    text=f"{'+'if p_>=0 else ''}{p_:.1f}%",showarrow=False,
                    font=dict(size=11,color=col,family="JetBrains Mono"))
    fig4.update_layout(barmode="group",bargap=.28,bargroupgap=.06,
        title=dict(text="Movimientos del Período — Principales Conceptos Fiscales",
            font=dict(family="Syne",size=14,color="#1E1E3F")),
        xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor=GR,tickformat="$,.0f"),
        legend=dict(orientation="h",y=1.08,x=0,font=dict(family="Outfit")),**PB,height=420)
    st.plotly_chart(fig4,use_container_width=True,key="g4")

    # G5: Evolución histórica
    st.markdown('<div class="section-hdr">📈 Evolución Histórica de Saldos Insolutos</div>',unsafe_allow_html=True)
    hlabs,hvals=[],[]
    for p in reversed(periodos_db):
        _d=get_resumen(p["periodo"])
        def _sv(df,seg,kw):
            m=df[(df["segmento"]==seg)&df["concepto"].str.contains(kw,na=False)]
            return m["monto"].sum() if not m.empty else 0.0
        hlabs.append(f"{p['nombre_mes_es'][:3]} {p['anio']}")
        hvals.append(_sv(_d,"PPD","Saldo insoluto")+_sv(_d,"PUE","Saldo"))

    fig5=go.Figure()
    fig5.add_trace(go.Scatter(x=hlabs,y=hvals,mode="lines+markers",fill="tozeroy",
        fillgradient=dict(type="vertical",colorscale=[[0,"rgba(91,91,214,0)"],[1,"rgba(91,91,214,.18)"]]),
        line=dict(color=CU,width=3),marker=dict(size=9,color=CU,line=dict(color="white",width=2)),
        hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>",name="Saldo Total"))
    fig5.add_hline(y=0,line_dash="dash",line_color="#E5E7EB",line_width=1.5,
        annotation_text="Balance Cero",annotation_position="top left",
        annotation_font=dict(color="#9CA3AF",size=11))
    fig5.update_layout(title=dict(text="Evolución Saldos Insolutos — Períodos Disponibles",
        font=dict(family="Syne",size=13,color="#1E1E3F")),
        xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor=GR,tickformat="$,.0f"),
        **PB,height=300,showlegend=False)
    st.plotly_chart(fig5,use_container_width=True,key="g5")

# ── TAB 3: DETALLE ────────────────────────────────────────────────
with tab3:
    nuuids=len(df_det) if not df_det.empty else 0
    stot=df_det["monto"].sum() if not df_det.empty else 0
    prom=df_det["monto"].mean() if not df_det.empty else 0

    st.markdown(f"""
    <div class="konia-card">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:800;color:#1E1E3F;display:flex;align-items:center;gap:10px;">
            🔍 Detalle UUID <span class="live-badge">LIVE</span>
          </div>
          <div style="font-family:'Outfit',sans-serif;font-size:.8rem;color:#6B7280;margin-top:4px;">
            Explorador interactivo para el período: <strong style="color:#5B5BD6;">{per_sel['anio']}-{str(per_sel['mes']).zfill(2).upper()}</strong>
          </div>
        </div>
      </div>
    </div>
    """,unsafe_allow_html=True)

    d1,d2,d3,d4=st.columns(4)
    with d1: st.metric("TOTAL UUIDS",f"{nuuids:,}")
    with d2: st.metric("SALDO TOTAL",fm(stot))
    with d3: st.metric("PROMEDIO SALDO",fm(prom))
    with d4:
        if not df_det.empty and "segmento" in df_det.columns:
            nem=len(df_det[df_det["monto"]>0])
            ratio=(nem/nuuids*100) if nuuids>0 else 0
            st.metric("RATIO EMIT/RECIB",f"{ratio:.1f}%")
        else: st.metric("RATIO EMIT/RECIB","N/D")

    st.markdown("<br>",unsafe_allow_html=True)

    dc1,dc2=st.columns(2)
    with dc1:
        st.markdown('<div class="section-hdr">Distribución PPD / PUE</div>',unsafe_allow_html=True)
        if not df_det.empty and "segmento" in df_det.columns:
            sc=df_det.groupby("segmento")["monto"].sum().reset_index()
            fd1=go.Figure(go.Pie(labels=sc["segmento"],values=sc["monto"].abs(),hole=.6,
                marker=dict(colors=[CP,CU],line=dict(color="white",width=3)),
                textinfo="label+percent",textfont=dict(family="Outfit",size=13),
                hovertemplate="<b>%{label}</b><br>$%{value:,.2f}<extra></extra>"))
            fd1.update_layout(**PB,height=300,showlegend=True,
                legend=dict(orientation="h",y=-0.12,font=dict(family="Outfit")))
            st.plotly_chart(fd1,use_container_width=True,key="d1")
        else: st.info("Sin datos de segmento.")

    with dc2:
        st.markdown('<div class="section-hdr">Top 10 UUIDs por Saldo</div>',unsafe_allow_html=True)
        if not df_det.empty:
            t10=df_det.nlargest(10,"monto")[["uuid_raiz","monto"]]
            fd2=go.Figure(go.Bar(y=t10["uuid_raiz"].astype(str).str[:10]+"...",x=t10["monto"].abs(),
                orientation="h",marker=dict(color=t10["monto"].apply(lambda v:CP if v>=0 else CU),
                    line=dict(color="white",width=1.5)),
                hovertemplate="<b>%{y}</b><br>$%{x:,.2f}<extra></extra>"))
            fd2.update_layout(**PB,height=300,
                xaxis=dict(showgrid=True,gridcolor=GR,tickformat="$,.0f"),
                yaxis=dict(showgrid=False,autorange="reversed"),showlegend=False)
            st.plotly_chart(fd2,use_container_width=True,key="d2")

    st.markdown('<div class="section-hdr">Explorador de Registros</div>',unsafe_allow_html=True)
    if not df_det.empty:
        cs=[c for c in ["uuid_raiz","uuid_relacionado","segmento","concepto","fecha","monto"] if c in df_det.columns]
        dshow=df_det[cs].copy()
        if "monto" in dshow.columns: dshow["monto"]=dshow["monto"].apply(fm)
        ec1,ec2=st.columns([3,1])
        with ec1: st.markdown(f'<div style="font-family:Outfit,sans-serif;font-size:.8rem;color:#6B7280;">{len(dshow):,} registros encontrados</div>',unsafe_allow_html=True)
        with ec2: ps=st.selectbox("Por pág.",[25,50,100],key="pgsz")
        st.dataframe(dshow.head(ps),use_container_width=True,height=400)
    else: st.info("Sin registros para los filtros seleccionados.")

# FOOTER
st.markdown("<br><br>",unsafe_allow_html=True)
st.markdown('<div style="text-align:center;padding:16px 0;border-top:1px solid #EDEEF8;"><span style="font-family:Outfit,sans-serif;font-size:.76rem;color:#9CA3AF;">KONIA · Matriz Fiscal Premium v3.0 · © 2026 · Análisis SAT/CFDI en tiempo real</span></div>',unsafe_allow_html=True)

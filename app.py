import streamlit as st
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Control Línea 2 - CCU",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS EN TEMA CLARO (FONDO BLANCO) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 18px;
        border: 1px solid #e9ecef;
        border-left: 5px solid #0d6efd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: bold;
        color: #0d6efd;
    }
    .metric-label {
        font-size: 13px;
        color: #6c757d;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DICCIONARIO OFICIAL LÍNEA 2 CCU ---
PRODUCTOS_PRESET = {
    "Bilz / Pap / Kem Regular (600 ml)": {"factor": 7.125, "ml": 600, "bph": 60000},
    "Bilz / Pap / Kem Zero (600 ml)": {"factor": 7.125, "ml": 600, "bph": 60000},
    "Pepsi Regular / Zero (600 ml)": {"factor": 6.000, "ml": 600, "bph": 60000},
    "Seven Up / Tónica / Ginger Ale (600 ml)": {"factor": 6.000, "ml": 600, "bph": 60000},
    "Limón Soda Regular / Zero (600 ml)": {"factor": 5.000, "ml": 600, "bph": 60000},
    "Crush Regular / Zero (600 ml)": {"factor": 5.000, "ml": 600, "bph": 60000},
    "Rockstar (500 ml)": {"factor": 4.000, "ml": 500, "bph": 60000},
    "POP Huevo (500 ml)": {"factor": 7.125, "ml": 500, "bph": 42000},
    "Formato 1.25 L": {"factor": 7.125, "ml": 1250, "bph": 38000},
    "Bilz / Pap / Kem (1.5 L)": {"factor": 7.125, "ml": 1500, "bph": 38000},
    "Pepsi / 7Up (1.5 L)": {"factor": 6.000, "ml": 1500, "bph": 38000},
    "Crush (1.5 L)": {"factor": 5.000, "ml": 1500, "bph": 38000},
    "1.75 L Cisne": {"factor": 7.125, "ml": 1750, "bph": 34000},
    "Personalizado": {"factor": 7.125, "ml": 600, "bph": 60000}
}

# --- ENCABEZADO ---
st.title("⚡ Control de Producción - Línea 2 CCU")
st.caption("Calculadora de rendimiento para Sopladora Ergobloc L, Mixer y Materiales")

# --- BARRA LATERAL: SELECCIÓN DE PRODUCTO Y EFICIENCIA ---
with st.sidebar:
    st.header("⚙️ Configuración del Turno")
    prod_nombre = st.selectbox("Producto en Máquina", list(PRODUCTOS_PRESET.keys()))
    preset = PRODUCTOS_PRESET[prod_nombre]

    st.subheader("Parámetros del Producto")
    vol_ml = st.number_input("Volumen Botella (ml)", value=preset["ml"], step=50)
    factor_mezcla = st.number_input("Factor de Mezcla", value=preset["factor"], step=0.1)
    bph_nominal = st.number_input("Velocidad Nominal Ergobloc (BPH)", value=preset["bph"], step=1000)
    
    st.subheader("Eficiencia de Línea")
    oee = st.slider("OEE / Eficiencia Real (%)", min_value=50, max_value=100, value=85)
    bph_real = bph_nominal * (oee / 100.0)
    st.info(f"Velocidad Real: **{int(bph_real):,} BPH**")

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs([
    "📦 1. Producción x Programación", 
    "🧪 2. Cálculo Inverso (Jarabe)", 
    "🌊 3. Litros Finales (Sistema Completo)"
])

# ==========================================
# PESTAÑA 1: PROGRAMACIÓN DE PRODUCCIÓN
# ==========================================
with tab1:
    st.subheader("Planificación de Orden de Fabricación")
    col1, col2 = st.columns(2)
    
    with col1:
        litros_obj = st.number_input("Litros Totales a Producir", value=50000, step=5000)
        botellas_por_pack = st.number_input("Botellas por Pack (Ej. 6 para 3x2)", value=6, step=1)
        packs_por_pallet = st.number_input("Packs por Pallet", value=100, step=10)
    
    with col2:
        hora_inicio = st.time_input("Hora de Inicio / Actual", value=datetime.now().time())
    
    # Cálculos Tab 1
    total_botellas = (litros_obj * 1000) / vol_ml
    total_packs = total_botellas / botellas_por_pack
    total_pallets = total_packs / packs_por_pallet
    jarabe_necesario = litros_obj / factor_mezcla
    
    horas_prod = total_botellas / bph_real if bph_real > 0 else 0
    tiempo_fin = datetime.combine(datetime.today(), hora_inicio) + timedelta(hours=horas_prod)

    # Métricas en Pantalla
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Pallets Totales</div><div class="metric-value">{total_pallets:.1f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Packs Totales</div><div class="metric-value">{int(total_packs):,}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Jarabe Necesario</div><div class="metric-value">{jarabe_necesario:.0f} L</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Hora Término Est.</div><div class="metric-value">{tiempo_fin.strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: CÁLCULO INVERSO DESDE JARABE
# ==========================================
with tab2:
    st.subheader("¿Cuánto se produce con el Jarabe Disponible?")
    jarabe_disp = st.number_input("Litros de Jarabe en Tanque (L)", value=2000, step=100)
    
    # Cálculos Tab 2
    bebida_total_j = jarabe_disp * factor_mezcla
    botellas_j = (bebida_total_j * 1000) / vol_ml
    packs_j = botellas_j / 6
    pallets_j = packs_j / 100
    horas_j = botellas_j / bph_real if bph_real > 0 else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Bebida Final Producible", f"{int(bebida_total_j):,} Litros")
    with c2:
        st.metric("Total Botellas", f"{int(botellas_j):,} u")
    with c3:
        st.metric("Tiempo de Marcha Restante", f"{horas_j:.2f} Horas")

# ==========================================
# PESTAÑA 3: LITROS FINALES (SISTEMA COMPLETO)
# ==========================================
with tab3:
    st.subheader("🌊 Balance Total de Producto en Línea (Elaboración + Tuberías + Mixer)")
    st.caption("Usa esta pestaña al final del lote para calcular la última botella real antes de purgar.")

    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("### 🛢️ 1. Tanque Elaboración")
        jarabe_tanque = st.number_input("Jarabe Restante en Tanque (L)", value=2000, step=100, key="j_t3")
        bebida_de_jarabe = jarabe_tanque * factor_mezcla
        st.caption(f"➜ Equivale a **{int(bebida_de_jarabe):,} L** de bebida.")

    with col_b:
        st.markdown("### 🎛️ 2. Mixer / Carbonatador")
        litros_mixer = st.number_input("Producto Terminado en Mixer (L)", value=200, step=20)

    with col_c:
        st.markdown("### 🚀 3. Tuberías y Matriz")
        litros_tuberias = st.number_input("Producto Terminado en Tuberías (L)", value=1000, step=100)
        st.caption("Normalmente ~1.000 Litros con línea llena.")

    # CÁLCULO SUMATORIA TOTAL
    litros_totales_sistema = bebida_de_jarabe + litros_mixer + litros_tuberias
    botellas_sistema = (litros_totales_sistema * 1000) / vol_ml
    packs_sistema = botellas_sistema / 6
    pallets_sistema = packs_sistema / 100
    tiempo_sistema_min = (botellas_sistema / bph_real) * 60 if bph_real > 0 else 0

    st.markdown("---")
    st.markdown("## 📊 Resultado Total en Sistema")

    res1, res2, res3, res4 = st.columns(4)
    with res1:
        st.metric("Litros TOTALES Bebida", f"{int(litros_totales_sistema):,} L")
    with res2:
        st.metric("Botellas Reales", f"{int(botellas_sistema):,} u")
    with res3:
        st.metric("Packs Reales (3x2)", f"{int(packs_sistema):,} packs")
    with res4:
        st.metric("Tiempo de Llenado", f"{int(tiempo_sistema_min)} min")

    st.success(f"💡 **Resumen para el Supervisor:** Quedan exactamente **{pallets_sistema:.1f} Pallets** de producción total. La línea parará por falta de producto en **{int(tiempo_sistema_min)} minutos** a la velocidad actual.")

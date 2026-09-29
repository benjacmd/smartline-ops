import streamlit as st
from datetime import datetime, timedelta
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Control Línea 2 - CCU",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS EN TEMA CLARO ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #e9ecef;
        border-left: 5px solid #0d6efd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #0d6efd;
    }
    .metric-label {
        font-size: 12px;
        color: #6c757d;
        text-transform: uppercase;
        font-weight: 600;
    }
    .insumo-card {
        background-color: #eef2f7;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #198754;
        margin-bottom: 10px;
    }
    .insumo-title {
        font-weight: bold;
        color: #198754;
        font-size: 14px;
    }
    .insumo-qty {
        font-size: 20px;
        font-weight: bold;
        color: #212529;
    }
    </style>
""", unsafe_allow_html=True)

# --- DICCIONARIO OFICIAL LÍNEA 2 CCU ---
PRODUCTOS_PRESET = {
    "Bilz / Pap / Kem Regular (600 ml)": {"factor": 7.125, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Bilz / Pap / Kem Zero (600 ml)": {"factor": 7.125, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Pepsi Regular / Zero (600 ml)": {"factor": 6.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Seven Up / Tónica / Ginger Ale (600 ml)": {"factor": 6.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Limón Soda Regular / Zero (600 ml)": {"factor": 5.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Crush Regular / Zero (600 ml)": {"factor": 5.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Rockstar (500 ml)": {"factor": 4.000, "ml": 500, "bph": 60000, "pref_caja": 15000},
    "POP Huevo (500 ml)": {"factor": 7.125, "ml": 500, "bph": 42000, "pref_caja": 15000},
    "Formato 1.25 L": {"factor": 7.125, "ml": 1250, "bph": 38000, "pref_caja": 10000},
    "Bilz / Pap / Kem (1.5 L)": {"factor": 7.125, "ml": 1500, "bph": 38000, "pref_caja": 10000},
    "Pepsi / 7Up (1.5 L)": {"factor": 6.000, "ml": 1500, "bph": 38000, "pref_caja": 10000},
    "Crush (1.5 L)": {"factor": 5.000, "ml": 1500, "bph": 38000, "pref_caja": 10000},
    "1.75 L Cisne": {"factor": 7.125, "ml": 1750, "bph": 34000, "pref_caja": 10000},
    "Personalizado": {"factor": 7.125, "ml": 600, "bph": 60000, "pref_caja": 15000}
}

# --- ENCABEZADO ---
st.title("⚡ Control de Producción e Insumos - Línea 2 CCU")
st.caption("Calculadora en tiempo real para Ergobloc L, Mixer y Pedido a Bodega")

# --- BARRA LATERAL: SELECCIÓN Y CONFIGURACIÓN DE INSUMOS ---
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

    st.subheader("📦 Capacidades Estándar de Bodega")
    std_preforma_caja = st.number_input("Preformas x Caja", value=preset["pref_caja"], step=1000)
    std_tapa_caja = st.number_input("Tapas x Caja", value=5000, step=500)  # Actualizado a 5,000 por caja
    std_etiqueta_rollo = st.number_input("Etiquetas x Rollo", value=10000, step=1000)
    std_film_pack_rollo = st.number_input("Packs x Rollo Film Paquete", value=1200, step=100)
    std_carton_pallet = st.number_input("Planchas Cartón x Pallet", value=500, step=50)
    std_pallet_stretcher = st.number_input("Pallets x Rollo Stretcher", value=35, step=5)

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2 = st.tabs([
    "📦 1. Programación y Pedido a Bodega", 
    "🌊 2. Litros Finales e Insumos Restantes"
])

# ==========================================
# PESTAÑA 1: PROGRAMACIÓN E INSUMOS TOTALES
# ==========================================
with tab1:
    st.subheader("Planificación de Orden y Materiales Requeridos")
    col1, col2 = st.columns(2)
    
    with col1:
        litros_obj = st.number_input("Litros Totales a Producir", value=50000, step=5000)
        botellas_por_pack = st.number_input("Botellas por Pack (Ej. 6 para 3x2)", value=6, step=1, key="pack_t1")
        packs_por_pallet = st.number_input("Packs por Pallet", value=100, step=10, key="pallet_t1")
    
    with col2:
        hora_inicio = st.time_input("Hora de Inicio / Actual", value=datetime.now().time())

    # Cálculos Principales Tab 1
    total_botellas = (litros_obj * 1000) / vol_ml
    total_packs = total_botellas / botellas_por_pack
    total_pallets = total_packs / packs_por_pallet
    jarabe_necesario = litros_obj / factor_mezcla
    
    horas_prod = total_botellas / bph_real if bph_real > 0 else 0
    tiempo_fin = datetime.combine(datetime.today(), hora_inicio) + timedelta(hours=horas_prod)

    # Métricas Principales Tab 1
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Pallets Totales</div><div class="metric-value">{total_pallets:.1f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Packs Totales</div><div class="metric-value">{int(total_packs):,}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Jarabe Necesario</div><div class="metric-value">{jarabe_necesario:.0f} L</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Hora Término Est.</div><div class="metric-value">{tiempo_fin.strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Pedido de Insumos y Materiales a Bodega")
    st.caption("Calculado con un 2% adicional para mermas de arranque y pruebas de línea.")

    # Cálculos Insumos (+2% Mermas) Tab 1
    botellas_con_merma = total_botellas * 1.02
    packs_con_merma = total_packs * 1.02

    cajas_preforma = math.ceil(botellas_con_merma / std_preforma_caja)
    cajas_tapa = math.ceil(botellas_con_merma / std_tapa_caja)
    rollos_etiqueta = math.ceil(botellas_con_merma / std_etiqueta_rollo)
    rollos_film = math.ceil(packs_con_merma / std_film_pack_rollo)
    pallets_carton = math.ceil(total_pallets / std_carton_pallet)
    rollos_stretcher = math.ceil(total_pallets / std_pallet_stretcher)

    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🧪 Cajas de Preforma</div><div class="insumo-qty">{cajas_preforma} Cajas</div><small>({int(botellas_con_merma):,} un. @ {std_preforma_caja:,}/caja)</small></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🏷️ Rollos de Etiqueta</div><div class="insumo-qty">{rollos_etiqueta} Rollos</div><small>(BOPP / Body / Sleeve @ {std_etiqueta_rollo:,}/rollo)</small></div>', unsafe_allow_html=True)

    with ic2:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🔘 Cajas de Tapa</div><div class="insumo-qty">{cajas_tapa} Cajas</div><small>({int(botellas_con_merma):,} tapas @ 5,000/caja)</small></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">📦 Rollos Film Paquete</div><div class="insumo-qty">{rollos_film} Rollos</div><small>(Empaquetadora Variopac)</small></div>', unsafe_allow_html=True)

    with ic3:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">📜 Pallet Cartón Corrugado</div><div class="insumo-qty">{pallets_carton} Pallet(s)</div><small>({int(total_pallets)} planchas)</small></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🌀 Film Envolvedora (Stretch)</div><div class="insumo-qty">{rollos_stretcher} Rollos</div><small>(Envolvedora Stretch W.)</small></div>', unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: LITROS FINALES E INSUMOS REMANENTES
# ==========================================
with tab2:
    st.subheader("🌊 Balance Total de Producto en Línea (Elaboración + Tuberías + Mixer)")
    st.caption("Usa esta pestaña al final del lote para saber exactamente cuánto producto y material necesitas para terminar.")

    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("### 🛢️ 1. Tanque Elaboración")
        jarabe_tanque = st.number_input("Jarabe Restante en Tanque (L)", value=2000, step=100, key="j_t2")
        bebida_de_jarabe = jarabe_tanque * factor_mezcla
        st.caption(f"➜ Equivale a **{int(bebida_de_jarabe):,} L** de bebida.")

    with col_b:
        st.markdown("### 🎛️ 2. Mixer / Carbonatador")
        litros_mixer = st.number_input("Producto Terminado en Mixer (L)", value=200, step=20)
        st.caption("Normalmente ~200 Litros.")

    with col_c:
        st.markdown("### 🚀 3. Tuberías y Matriz")
        litros_tuberias = st.number_input("Producto Terminado en Tuberías (L)", value=1000, step=100)
        st.caption("Normalmente ~1.000 Litros con línea llena.")

    # CÁLCULO SUMATORIA TOTAL TAB 2
    litros_totales_sistema = bebida_de_jarabe + litros_mixer + litros_tuberias
    botellas_sistema = (litros_totales_sistema * 1000) / vol_ml
    packs_sistema = botellas_sistema / botellas_por_pack
    pallets_sistema = packs_sistema / packs_por_pallet
    tiempo_sistema_min = (botellas_sistema / bph_real) * 60 if bph_real > 0 else 0

    st.markdown("---")
    st.markdown("## 📊 Producto Final Producible")

    res1, res2, res3, res4 = st.columns(4)
    with res1:
        st.metric("Litros TOTALES Bebida", f"{int(litros_totales_sistema):,} L")
    with res2:
        st.metric("Botellas Reales", f"{int(botellas_sistema):,} u")
    with res3:
        st.metric("Packs Reales", f"{int(packs_sistema):,} packs")
    with res4:
        st.metric("Tiempo de Llenado", f"{int(tiempo_sistema_min)} min")

    st.success(f"💡 **Resumen para el Supervisor:** Quedan exactamente **{pallets_sistema:.1f} Pallets** de producción total. La línea parará por falta de producto en **{int(tiempo_sistema_min)} minutos** a la velocidad actual.")

    # CALCULADORA DE INSUMOS PARA EL REMANENTE
    st.markdown("---")
    st.subheader("📋 Insumos Necesarios para Terminar el Lote Actual")
    st.caption("Insumos mínimos requeridos en máquina para procesar la bebida restante del sistema (+2% merma).")

    botellas_rem_merma = botellas_sistema * 1.02
    packs_rem_merma = packs_sistema * 1.02

    cajas_pref_rem = math.ceil(botellas_rem_merma / std_preforma_caja)
    cajas_tapa_rem = math.ceil(botellas_rem_merma / std_tapa_caja)
    rollos_etiq_rem = math.ceil(botellas_rem_merma / std_etiqueta_rollo)
    rollos_film_rem = math.ceil(packs_rem_merma / std_film_pack_rollo)
    pallets_carton_rem = math.ceil(pallets_sistema / std_carton_pallet)
    rollos_stretch_rem = math.ceil(pallets_sistema / std_pallet_stretcher)

    ric1, ric2, ric3 = st.columns(3)
    with ric1:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🧪 Cajas de Preforma</div><div class="insumo-qty">{cajas_pref_rem} Cajas</div><small>({int(botellas_rem_merma):,} un. @ {std_preforma_caja:,}/caja)</small></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🏷️ Rollos de Etiqueta</div><div class="insumo-qty">{rollos_etiq_rem} Rollos</div><small>(BOPP / Body / Sleeve @ {std_etiqueta_rollo:,}/rollo)</small></div>', unsafe_allow_html=True)

    with ric2:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🔘 Cajas de Tapa</div><div class="insumo-qty">{cajas_tapa_rem} Cajas</div><small>({int(botellas_rem_merma):,} tapas @ 5,000/caja)</small></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">📦 Rollos Film Paquete</div><div class="insumo-qty">{rollos_film_rem} Rollos</div><small>(Empaquetadora Variopac)</small></div>', unsafe_allow_html=True)

    with ric3:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">📜 Pallet Cartón Corrugado</div><div class="insumo-qty">{pallets_carton_rem} Pallet(s)</div><small>({pallets_sistema:.1f} planchas)</small></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🌀 Film Envolvedora (Stretch)</div><div class="insumo-qty">{rollos_stretch_rem} Rollos</div><small>(Envolvedora Stretch W.)</small></div>', unsafe_allow_html=True)

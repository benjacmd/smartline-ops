import streamlit as st
from datetime import datetime, timedelta
import math
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Control Línea 2 - CCU",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MATRIZ OFICIAL CCU LÍNEA 2 ---
MATRIZ_CCU = {
    "1. 500 ml Rockstar": {"ml": 500, "factor": 4.0, "co2": 3.10, "peso_pref": 19.5, "etiq": "Sleeve Fullbody", "bph": 60000, "pref_caja": 15000, "pack": 6},
    "2. 500 ml POP (Huevo)": {"ml": 500, "factor": 7.125, "co2": 3.20, "peso_pref": 19.5, "etiq": "Sleeve Fullbody", "bph": 42000, "pref_caja": 15000, "pack": 6},
    "3. 600 ml BGP": {"ml": 600, "factor": 7.125, "co2": 4.20, "peso_pref": 19.5, "etiq": "BOPP", "bph": 60000, "pref_caja": 15000, "pack": 6},
    "4. 600 ml AXL": {"ml": 600, "factor": 7.125, "co2": 4.20, "peso_pref": 19.5, "etiq": "BOPP", "bph": 60000, "pref_caja": 15000, "pack": 6},
    "5. 600 ml Ripples (BOPP)": {"ml": 600, "factor": 7.125, "co2": 4.20, "peso_pref": 19.5, "etiq": "BOPP", "bph": 60000, "pref_caja": 15000, "pack": 6},
    "5.1. 600 ml Ripples (Sleeve)": {"ml": 600, "factor": 7.125, "co2": 4.20, "peso_pref": 19.5, "etiq": "Sleeve Halfbody", "bph": 60000, "pref_caja": 15000, "pack": 6},
    "6. 600 ml B&P": {"ml": 600, "factor": 7.125, "co2": 3.75, "peso_pref": 19.5, "etiq": "BOPP", "bph": 60000, "pref_caja": 15000, "pack": 6},
    "7.1. 1,5 L Carolina (BOPP)": {"ml": 1500, "factor": 7.125, "co2": 4.20, "peso_pref": 37.0, "etiq": "BOPP", "bph": 38000, "pref_caja": 8000, "pack": 6},
    "7.2. 1,5 L Carolina (Sleeve)": {"ml": 1500, "factor": 7.125, "co2": 4.20, "peso_pref": 37.0, "etiq": "Sleeve Halfbody", "bph": 36000, "pref_caja": 8000, "pack": 6},
    "8. 1,5 L Genérica": {"ml": 1500, "factor": 7.125, "co2": 3.95, "peso_pref": 37.0, "etiq": "BOPP", "bph": 38000, "pref_caja": 8000, "pack": 6},
    "9. 1,5 L Crush": {"ml": 1500, "factor": 5.0, "co2": 3.95, "peso_pref": 37.0, "etiq": "BOPP", "bph": 38000, "pref_caja": 8000, "pack": 6},
    "10. 1,5 L B&P": {"ml": 1500, "factor": 7.125, "co2": 3.75, "peso_pref": 37.0, "etiq": "BOPP", "bph": 38000, "pref_caja": 8000, "pack": 6},
    "11. 1,75 L Cisne": {"ml": 1750, "factor": 7.125, "co2": 4.20, "peso_pref": 47.6, "etiq": "BOPP", "bph": 34000, "pref_caja": 6000, "pack": 6}
}

SABORES = [
    "Bilz", "Bilz Zero", "Pap", "Pap Zero", "Kem", "Kem Zero", "Kem Piña", 
    "Pepsi", "Pepsi Zero", "7Up", "7Up Zero", "Limón Soda", "Limón Soda Zero", 
    "Crush", "Crush Zero", "Rockstar Original", "Rockstar Sandía", "Rockstar Mango", "POP Huevo"
]

if "packs_calculados" not in st.session_state:
    st.session_state.packs_calculados = 15000

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración del Envase")
    envase_sel = st.selectbox("Seleccionar Envase (Matriz L2)", list(MATRIZ_CCU.keys()))
    fmt = MATRIZ_CCU[envase_sel]

    st.markdown("---")
    st.markdown("### 📌 Ficha Técnica")
    st.write(f"• **Volumen:** {fmt['ml']} ml")
    st.write(f"• **Preforma:** {fmt['peso_pref']} g")
    st.write(f"• **Etiqueta:** {fmt['etiq']}")
    st.write(f"• **Target CO₂:** {fmt['co2']} v/v")

    st.markdown("---")
    st.markdown("### ⚡ Ajustes de Línea")
    factor_mezcla = st.number_input("Factor Mezcla (Jarabe → Bebida)", value=fmt["factor"], step=0.1)
    bph_nominal = st.number_input("Velocidad Ergobloc (BPH)", value=fmt["bph"], step=1000)
    oee = st.slider("Eficiencia / OEE (%)", 50, 100, 100)
    bph_real = bph_nominal * (oee / 100.0)
    st.caption(f"Velocidad Operativa: **{int(bph_real):,} BPH**")

# --- TITULO PRINCIPAL ---
st.title("⚡ Control de Producción Línea 2 - CCU")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🧪 1. Lote desde Jarabe", "🌊 2. Balance de Cierre", "📲 3. WhatsApp"])

# ==========================================
# PESTAÑA 1: PROGRAMACIÓN DE LOTE
# ==========================================
with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📥 Datos del Tanque")
        jarabe = st.number_input("Jarabe Disponible (L)", value=7000, step=500)
        hora_init = st.time_input("Hora de Inicio / Actual", value=datetime.now().time())
        bot_pack = st.selectbox("Agrupación (Bot/Pack)", [6, 12], index=0 if fmt["pack"]==6 else 1)
        pack_pallet = st.number_input("Packs por Pallet", value=100 if fmt['ml'] <= 600 else 60, step=5)

    # Cálculos principales
    litros_bebida = jarabe * factor_mezcla
    total_botellas = (litros_bebida * 1000) / fmt["ml"]
    total_packs = total_botellas / bot_pack
    st.session_state.packs_calculados = int(total_packs)
    total_pallets = total_packs / pack_pallet
    
    horas_prod = total_botellas / bph_real if bph_real > 0 else 0
    fin_est = datetime.combine(datetime.today(), hora_init) + timedelta(hours=horas_prod)

    with col_b:
        st.subheader("📊 Producción Calculada")
        m1, m2 = st.columns(2)
        m1.metric("Bebida Final", f"{int(litros_bebida):,} L".replace(",", "."))
        m2.metric("Botellas Reales", f"{int(total_botellas):,} u".replace(",", "."))
        m1.metric("Packs Totales", f"{int(total_packs):,} pk".replace(",", "."))
        m2.metric("Pallets Totales", f"{total_pallets:.1f}")
        
        st.success(f"⏱️ **Tiempo estimado:** {int(horas_prod)}h {int((horas_prod % 1) * 60)}m\n\n⏰ **Hora Término:** {fin_est.strftime('%H:%M hrs')}")

    st.divider()
    st.subheader("📦 Solicitud de Insumos a Bodega")
    
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Preformas", f"{math.ceil(total_botellas / fmt['pref_caja'])} Cajas", f"{fmt['pref_caja']:,} u/caja")
    i2.metric("Tapas", f"{math.ceil(total_botellas / 5000)} Cajas", "5.000 u/caja")
    i3.metric("Etiquetas", f"{math.ceil(total_botellas / 10000)} Rollos", "10.000 u/rollo")
    i4.metric("Film Paquete", f"{math.ceil(total_packs / 2700)} Rollos", "2.700 pk/rollo")

# ==========================================
# PESTAÑA 2: BALANCE FINAL DE CIERRE
# ==========================================
with tab2:
    st.subheader("🌊 Balance de Jarabe + Mixer + Tuberías")
    
    c1, c2, c3, c4 = st.columns(4)
    j_tanque = c1.number_input("Jarabe Tanque (L)", value=1200, step=100)
    l_mixer = c2.number_input("Mixer (L)", value=200, step=20)
    l_tubos = c3.number_input("Tuberías (L)", value=1000, step=100)
    merma_pct = c4.number_input("Merma Est. (%)", value=2.0, step=0.5)

    litros_sistema = (j_tanque * factor_mezcla) + l_mixer + l_tubos
    botellas_sistema = (litros_sistema * 1000) / fmt["ml"]
    packs_sistema = botellas_sistema / bot_pack
    minutos_restantes = (botellas_sistema / bph_real) * 60 if bph_real > 0 else 0

    st.divider()
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Litros Sistema", f"{int(litros_sistema):,} L".replace(",", "."))
    r2.metric("Botellas Reales", f"{int(botellas_sistema):,} u".replace(",", "."))
    r3.metric("Packs Producibles", f"{int(packs_sistema):,} pk".replace(",", "."))
    r4.metric("Minutos de Carrera", f"{int(minutos_restantes)} min")

# ==========================================
# PESTAÑA 3: NOTIFICACIÓN WHATSAPP
# ==========================================
with tab3:
    st.subheader("📲 Reporte Rápido de Turno")
    
    w1, w2, w3 = st.columns(3)
    turno = w1.selectbox("Turno", ["Turno A", "Turno B", "Turno C"])
    sabor = w2.selectbox("Sabor / Producto", SABORES)
    op_num = w3.text_input("Orden Producción (OP)", value="6600225198")

    w4, w5 = st.columns(2)
    packs_prod = w4.number_input("Packs Producidos", value=st.session_state.packs_calculados, step=100)
    fecha_txt = w5.text_input("Fecha", value=datetime.now().strftime("%d/%m/%Y"))

    fmt_label = f"{fmt['ml']}ml" if fmt['ml'] < 1000 else f"{fmt['ml']/1000}L"
    msg = f"Favor notificar:\n{turno} - Línea 2\n{sabor} {fmt_label}\nOP: {op_num}\nCajas: {packs_prod:,}\n{fecha_txt}".replace(",", ".")

    st.code(msg, language="text")

    url_wa = f"https://api.whatsapp.com/send?text={urllib.parse.quote(msg)}"
    st.markdown(f'''
        <a href="{url_wa}" target="_blank">
            <button style="background-color:#25d366; color:white; border:none; padding:12px; font-size:16px; font-weight:bold; border-radius:6px; cursor:pointer; width:100%;">
                📲 Enviar por WhatsApp
            </button>
        </a>
    ''', unsafe_allow_html=True)

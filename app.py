import streamlit as st
import math
from datetime import datetime, timedelta
import pytz

# Configuración de zona horaria de Chile
CHILE_TZ = pytz.timezone('America/Santiago')

# Configuración de página para celulares
st.set_page_config(
    page_title="SmartLine Ops",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ SmartLine Ops")
st.caption("Control Rápido de Producción e Insumos")

# --- DICCIONARIO EXCLUSIVO LÍNEA 2 CCU (ACTUALIZADO) ---
PRODUCTOS_PRESET = {
    # --- FORMATOS 500 ml / 600 ml ---
    "Bilz / Pap / Kem Regular (600 ml)": {"factor": 7.125, "ml": 600, "bph": 60000},
    "Bilz / Pap / Kem Zero (600 ml)": {"factor": 7.125, "ml": 600, "bph": 60000},
    "Pepsi Regular / Zero (600 ml)": {"factor": 6.000, "ml": 600, "bph": 60000},
    "Seven Up / Tónica / Ginger Ale (600 ml)": {"factor": 6.000, "ml": 600, "bph": 60000},
    "Limón Soda Regular / Zero (600 ml)": {"factor": 5.000, "ml": 600, "bph": 60000},
    "Crush Regular / Zero (600 ml)": {"factor": 5.000, "ml": 600, "bph": 60000},
    "Rockstar (500 ml)": {"factor": 4.000, "ml": 500, "bph": 60000},  # Factor 4 (Multiplica jarabe x 4)
    "POP Huevo (500 ml)": {"factor": 7.125, "ml": 500, "bph": 42000},

    # --- FORMATOS FAMILIARES (1.25 L / 1.5 L / 1.75 L) ---
    "Formato 1.25 L": {"factor": 7.125, "ml": 1250, "bph": 38000},
    "Bilz / Pap / Kem (1.5 L)": {"factor": 7.125, "ml": 1500, "bph": 38000},
    "Pepsi / 7Up (1.5 L)": {"factor": 6.000, "ml": 1500, "bph": 38000},
    "Crush (1.5 L)": {"factor": 5.000, "ml": 1500, "bph": 38000},
    "1.75 L Cisne": {"factor": 7.125, "ml": 1750, "bph": 34000},

    # --- AJUSTE MANUAL ---
    "Personalizado": {"factor": 7.125, "ml": 600, "bph": 60000}
}

# Pestañas principales para navegación ultrarrápida
tab1, tab2 = st.tabs(["🚀 Modo Turno (Inicio)", "🔄 Saldo de Jarabe"])

# ==========================================
# PESTAÑA 1: CÁLCULO PRINCIPAL DE TURNO
# ==========================================
with tab1:
    st.subheader("1. Parámetros del Lote")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        producto_sel = st.selectbox("Producto:", list(PRODUCTOS_PRESET.keys()))
        preset = PRODUCTOS_PRESET[producto_sel]
        jarabe = st.number_input("Litros de Jarabe (L)", value=16000, step=500)
    
    with col_p2:
        factor = st.number_input("Factor (Mixer)", value=preset["factor"], format="%.3f")
        velocidad_bph = st.number_input("Velocidad (BPH)", value=preset["bph"], step=5000)

    formato_ml = preset["ml"]

    # --- AJUSTES RÁPIDOS EN EXPANDER (OCULTO POR DEFECTO PARA NO MOLESTAR) ---
    with st.expander("⚙️ Stock Actual en Piso y Empaques"):
        c1, c2 = st.columns(2)
        with c1:
            stock_film = st.number_input("Rollos Film en piso", value=8, step=1)
            stock_tapas = st.number_input("Cajas Tapas en piso", value=5, step=1)
            stock_pref = st.number_input("Cajas Preformas en piso", value=3, step=1)
        with c2:
            cap_pref = st.number_input("Preformas x caja", value=14000, step=1000)
            cap_tapas = st.number_input("Tapas x caja", value=5000, step=500)
            rend_film = 17448  # Estándar fijo (1 rollo = 17,448 botellas)

    # --- CÁLCULOS MATEMÁTICOS DIRECTOS ---
    litros_bebida = jarabe * factor
    litros_envase = formato_ml / 1000.0
    botellas_totales = litros_bebida / litros_envase if litros_envase > 0 else 1

    horas_prod = botellas_totales / velocidad_bph if velocidad_bph > 0 else 1
    minutos_totales = horas_prod * 60

    # Insumos necesarios
    cajas_pref_totales = math.ceil(botellas_totales / cap_pref)
    cajas_tapas_totales = math.ceil(botellas_totales / cap_tapas)
    rollos_film_totales = math.ceil(botellas_totales / rend_film)

    # Faltantes por pedir a bodega
    faltan_pref = max(0, cajas_pref_totales - stock_pref)
    faltan_tapas = max(0, cajas_tapas_totales - stock_tapas)
    faltan_film = max(0, rollos_film_totales - stock_film)

    # Palletizado (12 bot/pack, 132 packs/pallet)
    total_packs = math.ceil(botellas_totales / 12)
    total_pallets = math.ceil(total_packs / 132)

    # Tiempos y Alertas
    ahora = datetime.now(CHILE_TZ)
    hora_fin = ahora + timedelta(minutes=minutos_totales)
    hora_corte_tolva = hora_fin - timedelta(minutes=60)
    duracion_rollo_min = (rend_film / velocidad_bph) * 60 if velocidad_bph > 0 else 17.5
    hora_fin_film_piso = ahora + timedelta(minutes=stock_film * duracion_rollo_min)

    st.divider()

    # --- RESULTADOS VISUALES ---
    st.subheader("📊 Resumen del Lote")
    m1, m2, m3 = st.columns(3)
    m1.metric("Bebida Total", f"{litros_bebida:,.0f} L")
    m2.metric("Botellas", f"{int(botellas_totales):,} u")
    m3.metric("Tiempo Total", f"{int(horas_prod)}h {int(minutos_totales % 60)}m")

    st.subheader("📦 Pedido Inmediato a Bodega")
    i1, i2, i3 = st.columns(3)
    
    with i1:
        st.markdown("**Preformas**")
        if faltan_pref > 0:
            st.error(f"Pedir **{faltan_pref} cajas**")
        else:
            st.success("✅ OK")

    with i2:
        st.markdown("**Tapas**")
        if faltan_tapas > 0:
            st.error(f"Pedir **{faltan_tapas} cajas**")
        else:
            st.success("✅ OK")

    with i3:
        st.markdown("**Film Vario**")
        if faltan_film > 0:
            st.error(f"Pedir **{faltan_film} rollos**")
        else:
            st.success("✅ OK")

    st.info(f"""
    🪵 **Pallets totales:** {total_pallets} pallets ({total_packs:,} packs)
    🏁 **Fin estimado:** {hora_fin.strftime('%H:%M')} hrs.
    🎞️ **Film en piso se acaba a las:** {hora_fin_film_piso.strftime('%H:%M')} hrs.
    ⏰ **Corte de Tolva:** A las **{hora_corte_tolva.strftime('%H:%M')} hrs** deja de cargar tapas para no vaciar a mano.
    """)

    # --- REPORTE WHATSAPP ---
    st.subheader("📱 Reporte para WhatsApp")
    msg_wa = f"""📊 *REPORTE DE LÍNEA - {producto_sel}*
🕐 Hora inicio: {ahora.strftime('%H:%M')} hrs | Fin Est.: {hora_fin.strftime('%H:%M')} hrs
🥤 Bebida Total: {litros_bebida:,.0f} L ({int(botellas_totales):,} botellas)
🪵 Pallets: {total_pallets} ({total_packs:,} packs)

📦 *PEDIR A BODEGA:*
- Preformas: {'✅ OK' if faltan_pref == 0 else f'Faltan {faltan_pref} cajas'}
- Tapas: {'✅ OK' if faltan_tapas == 0 else f'Faltan {faltan_tapas} cajas'}
- Film: {'✅ OK' if faltan_film == 0 else f'Faltan {faltan_film} rollos'}
⏰ *Hora corte tolva:* {hora_corte_tolva.strftime('%H:%M')} hrs"""

    st.code(msg_wa, language="text")

# ==========================================
# PESTAÑA 2: CALCULADORA INVERSA (SALDO JARABE)
# ==========================================
with tab2:
    st.subheader("🔄 Consultar Jarabe Restante")
    st.caption("Si la producción se cortó ayer, ingresa los packs hechos para saber cuánto jarabe queda.")

    j_inicial = st.number_input("Jarabe Inicial con el que empezaron (L)", value=16000, step=500)
    packs_hechos = st.number_input("Packs/Cajas producidas en total", value=0, step=100)

    if packs_hechos > 0:
        botellas_hechas = packs_hechos * 12
        litros_bebida_hechos = (botellas_hechas * formato_ml) / 1000.0
        jarabe_usado = litros_bebida_hechos / factor if factor > 0 else 0
        jarabe_saldo = max(0.0, j_inicial - jarabe_usado)

        bebida_saldo = jarabe_saldo * factor
        botellas_saldo = bebida_saldo / (formato_ml / 1000.0) if formato_ml > 0 else 0
        pallets_saldo = math.ceil((botellas_saldo / 12) / 132)

        st.divider()
        r1, r2 = st.columns(2)
        r1.metric("Jarabe Restante en Tanque", f"{jarabe_saldo:,.0f} L")
        r2.metric("Pallets que te quedan por hacer", f"{pallets_saldo} pallets")

        st.success(f"💡 Te quedan **{jarabe_saldo:,.0f} Litros** de jarabe. Eso alcanza para fabricar **{int(botellas_saldo):,} botellas más**.")

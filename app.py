from datetime import datetime, timedelta
import math
import urllib.parse
import pandas as pd
import streamlit as st

# ==========================================
# CONSTANTES Y CONFIGURACIÓN INICIAL
# ==========================================
PACKS_DEFECTO_INICIAL = 15724

st.set_page_config(
    page_title="Control Línea 2 - CCU",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "packs_calculados" not in st.session_state:
    st.session_state.packs_calculados = PACKS_DEFECTO_INICIAL

# ==========================================
# TABLA DE PROPORCIONES (OFICIAL CCU)
# Factor Total = Agua + 1 de Jarabe
# ==========================================
PROPORCIONES_SABORES = {
    # --- BEBIDAS REGULAR ---
    "Bilz": 7.125,                # 6.125 agua / 1 jarabe
    "Pap": 7.125,                 # 6.125 agua / 1 jarabe
    "Kem": 7.125,                 # 6.125 agua / 1 jarabe
    "Kem piña": 7.125,            # 6.125 agua / 1 jarabe
    "Pepsi Reducida": 6.0,        # 5 agua / 1 jarabe
    "7Up": 6.0,                   # 5 agua / 1 jarabe
    "Limón Soda": 5.0,            # 4 agua / 1 jarabe
    "Crush": 5.0,                 # 4 agua / 1 jarabe
    # --- BEBIDAS ZERO ---
    "Bilz Zero": 7.125,           # 6.125 agua / 1 jarabe
    "Pap Zero": 7.125,            # 6.125 agua / 1 jarabe
    "Kem Zero": 7.125,            # 6.125 agua / 1 jarabe
    "Pepsi Zero": 6.0,            # 5 agua / 1 jarabe
    "7Up Zero": 6.0,              # 5 agua / 1 jarabe
    "Limón Soda Zero": 6.0,       # 5 agua / 1 jarabe
    "Crush Zero": 5.0,            # 4 agua / 1 jarabe
    # --- ROCKSTAR Y OTROS ---
    "Rockstar Original": 4.0,     # 3 agua / 1 jarabe
    "Rockstar Sandía": 4.0,       # 3 agua / 1 jarabe
    "Rockstar Mango": 4.0,        # 3 agua / 1 jarabe
    "POP Huevo": 4.0,             # 3 agua / 1 jarabe
}

LISTA_SABORES = list(PROPORCIONES_SABORES.keys()) + [
    "Otro (Escribir manualmente)"
]

FORMATOS_LINEA_2 = {
    "500 ml Rockstar": {
        "vol_ml": 500,
        "moldes": "De L4",
        "carb_vol": 3.10,
        "peso_pref_g": 19.5,
        "temp_llenado": "20°C",
        "etiqueta": "Sleeve Fullbody",
        "paquete": "3x2 y 4x3",
        "bph_ergobloc": 60000,
        "bph_sleevematic": 66000,
        "bph_variopac": 69000,
        "bph_modulpal": 72000,
        "bph_stretch": 72000,
    },
    "500 ml POP (huevo)": {
        "vol_ml": 500,
        "moldes": "Set completo nuevo",
        "carb_vol": 3.20,
        "peso_pref_g": 19.5,
        "temp_llenado": "20°C",
        "etiqueta": "Sleeve Fullbody",
        "paquete": "3x2 y 4x3",
        "bph_ergobloc": 42000,
        "bph_sleevematic": 46200,
        "bph_variopac": 48300,
        "bph_modulpal": 50400,
        "bph_stretch": 50400,
    },
    "600 ml BGP": {
        "vol_ml": 600,
        "moldes": "Set completo nuevo",
        "carb_vol": 4.20,
        "peso_pref_g": 19.5,
        "temp_llenado": "15°C",
        "etiqueta": "BOPP",
        "paquete": "3x2 y 4x3",
        "bph_ergobloc": 60000,
        "bph_sleevematic": 0,
        "bph_variopac": 69000,
        "bph_modulpal": 72000,
        "bph_stretch": 72000,
    },
    "600 ml AXL": {
        "vol_ml": 600,
        "moldes": "Set completo nuevo",
        "carb_vol": 4.20,
        "peso_pref_g": 19.5,
        "temp_llenado": "15°C",
        "etiqueta": "BOPP",
        "paquete": "3x2 y 4x3",
        "bph_ergobloc": 60000,
        "bph_sleevematic": 0,
        "bph_variopac": 69000,
        "bph_modulpal": 72000,
        "bph_stretch": 72000,
    },
    "600 ml Ripples": {
        "vol_ml": 600,
        "moldes": "Set completo nuevo",
        "carb_vol": 4.20,
        "peso_pref_g": 19.5,
        "temp_llenado": "15°C",
        "etiqueta": "BOPP / Sleeve Halfbody*",
        "paquete": "3x2 y 4x3",
        "bph_ergobloc": 60000,
        "bph_sleevematic": 66000,
        "bph_variopac": 69000,
        "bph_modulpal": 72000,
        "bph_stretch": 72000,
    },
    "600 ml B&P": {
        "vol_ml": 600,
        "moldes": "Set completo nuevo",
        "carb_vol": 3.75,
        "peso_pref_g": 19.5,
        "temp_llenado": "20°C",
        "etiqueta": "BOPP",
        "paquete": "3x2 y 4x3",
        "bph_ergobloc": 60000,
        "bph_sleevematic": 0,
        "bph_variopac": 69000,
        "bph_modulpal": 72000,
        "bph_stretch": 72000,
    },
    "1.5 l Carolina": {
        "vol_ml": 1500,
        "moldes": "De L4",
        "carb_vol": 4.20,
        "peso_pref_g": 37.0,
        "temp_llenado": "20°C",
        "etiqueta": "BOPP / Sleeve Halfbody*",
        "paquete": "3x2",
        "bph_ergobloc": 36000,
        "bph_sleevematic": 39600,
        "bph_variopac": 41400,
        "bph_modulpal": 43200,
        "bph_stretch": 43200,
    },
    "1.5 l Generica": {
        "vol_ml": 1500,
        "moldes": "De L4",
        "carb_vol": 3.95,
        "peso_pref_g": 37.0,
        "temp_llenado": "20°C",
        "etiqueta": "BOPP",
        "paquete": "3x2",
        "bph_ergobloc": 38000,
        "bph_sleevematic": 0,
        "bph_variopac": 43700,
        "bph_modulpal": 45220,
        "bph_stretch": 45220,
    },
    "1.5 l Crush": {
        "vol_ml": 1500,
        "moldes": "16 de L5, 8 nuevos",
        "carb_vol": 3.95,
        "peso_pref_g": 37.0,
        "temp_llenado": "20°C",
        "etiqueta": "BOPP",
        "paquete": "3x2",
        "bph_ergobloc": 38000,
        "bph_sleevematic": 0,
        "bph_variopac": 43700,
        "bph_modulpal": 45220,
        "bph_stretch": 45220,
    },
    "1.5 l B&P": {
        "vol_ml": 1500,
        "moldes": "De L4",
        "carb_vol": 3.75,
        "peso_pref_g": 37.0,
        "temp_llenado": "20°C",
        "etiqueta": "BOPP",
        "paquete": "3x2",
        "bph_ergobloc": 38000,
        "bph_sleevematic": 0,
        "bph_variopac": 42560,
        "bph_modulpal": 42560,
        "bph_stretch": 42560,
    },
    "1.75 l Cisne": {
        "vol_ml": 1750,
        "moldes": "16 de L5, 8 nuevos",
        "carb_vol": 0,
        "peso_pref_g": 47.6,
        "temp_llenado": "20°C",
        "etiqueta": "BOPP",
        "paquete": "3x2",
        "bph_ergobloc": 34000,
        "bph_sleevematic": 0,
        "bph_variopac": 39100,
        "bph_modulpal": 40800,
        "bph_stretch": 40800,
    },
}

LISTA_SABORES = list(PROPORCIONES_SABORES.keys()) + [
    "Otro (Escribir manualmente)"
]
LISTA_FORMATOS = list(FORMATOS_LINEA_2.keys()) + ["Otro (Escribir manualmente)"]


# ==========================================
# FUNCIONES DE LÓGICA Y CÁLCULOS
# ==========================================
def formato_miles(valor: float | int) -> str:
    return f"{int(valor):,}".replace(",", ".")


def calcular_produccion_lote(
    jarabe_L: float,
    factor: float,
    vol_ml: int,
    botellas_pack: int,
    packs_pallet: int,
    bph_real: float,
):
    litros_bebida = jarabe_L * factor
    botellas = (litros_bebida * 1000) / vol_ml
    packs = botellas / botellas_pack if botellas_pack > 0 else 0
    pallets = packs / packs_pallet if packs_pallet > 0 else 0

    horas_prod = botellas / bph_real if bph_real > 0 else 0
    minutos_totales = int(horas_prod * 60)

    return {
        "litros_bebida": litros_bebida,
        "botellas": botellas,
        "packs": packs,
        "pallets": pallets,
        "horas_prod": horas_prod,
        "minutos_totales": minutos_totales,
        "duracion_fmt": f"{minutos_totales // 60}h {minutos_totales % 60}m",
    }


def calcular_insumos_requeridos(
    botellas: float,
    packs: float,
    pallets: float,
    std_preforma: int,
    std_tapa: int,
    std_etiqueta: int,
    std_film: int,
    std_carton: int,
    std_stretcher: int,
):
    return {
        "preformas_cajas": math.ceil(botellas / std_preforma) if std_preforma else 0,
        "tapas_cajas": math.ceil(botellas / std_tapa) if std_tapa else 0,
        "etiquetas_rollos": math.ceil(botellas / std_etiqueta) if std_etiqueta else 0,
        "film_rollos": math.ceil(packs / std_film) if std_film else 0,
        "carton_pallets": math.ceil(pallets / std_carton) if std_carton else 0,
        "stretcher_rollos": math.ceil(pallets / std_stretcher) if std_stretcher else 0,
    }


# ==========================================
# ESTILOS CSS PERSONALIZADOS
# ==========================================
st.markdown(
    """
    <style>
    .insumo-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #198754;
        margin-bottom: 10px;
        border-top: 1px solid #dee2e6;
        border-right: 1px solid #dee2e6;
        border-bottom: 1px solid #dee2e6;
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
    .insumo-sub {
        color: #6c757d;
        font-size: 12px;
    }
    .whatsapp-box {
        background-color: #e7f7ee;
        border: 1px solid #25d366;
        border-left: 6px solid #25d366;
        padding: 16px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 15px;
        color: #111b21;
        white-space: pre-wrap;
        margin-bottom: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# ENCABEZADO Y BARRA LATERAL
# ==========================================
st.title("⚡ Control de Producción e Insumos - Línea 2 CCU")
st.caption("Calculadora en tiempo real para Ergobloc L, Mixer y Pedido a Bodega")

with st.sidebar:
    st.header("⚙️ Configuración del Turno")

    # 1. Selección de Sabor
    sabor_nombre = st.selectbox("Sabor / Producto", LISTA_SABORES)

    # 2. Selección de Formato
    envase_nombre = st.selectbox(
        "Formato / Envase Línea 2", list(FORMATOS_LINEA_2.keys())
    )
    preset_envase = FORMATOS_LINEA_2[envase_nombre]

    vol_ml = preset_envase["vol_ml"]
    bph_nominal = preset_envase["bph_ergobloc"]

    # Asignar Factor automático desde la tabla según el Sabor
    factor_defecto = PROPORCIONES_SABORES.get(sabor_nombre, 7.125)

    # Key dinámica según el sabor para auto-actualizar en pantalla
    factor_mezcla = st.number_input(
    "Factor de Mezcla (Jarabe → Bebida)",
    value=factor_defecto,
    step=0.001,
    format="%.3f",
    key=f"factor_{sabor_nombre}",
    )

    oee = st.number_input("Rendimiento / OEE Est. (%)", value=100.0, step=1.0)
    bph_real = bph_nominal * (oee / 100.0)

    st.markdown("---")
    st.subheader("📦 Estándares de Insumos")
    std_preforma_caja = st.number_input("Preformas por caja", value=14000, step=1000)
    std_tapa_caja = st.number_input("Tapas por caja", value=5000, step=5000)
    std_etiqueta_rollo = st.number_input("Etiquetas por rollo", value=18000, step=1000)
    std_film_pack_rollo = st.number_input("Packs por rollo film", value=2700, step=100)
    std_carton_pallet = st.number_input("Planchas cartón/pallet", value=100, step=10)
    std_pallet_stretcher = st.number_input("Pallets por rollo stretch", value=40, step=5)

    st.info(
        f"**Sabor:** {sabor_nombre}\n\n"
        f"• Factor CCU: **{factor_mezcla}**\n\n"
        f"• Vel. Ergobloc: **{bph_nominal:,} BPH**\n\n".replace(",", ".")
        + f"• Peso Preforma: **{preset_envase['peso_pref_g']} g**\n\n"
        + f"• Etiqueta: **{preset_envase['etiqueta']}**"
    )

# ==========================================
# PESTAÑAS PRINCIPALES
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7  = st.tabs([
    "🧪 Programación", 
    "🌊 Balance Final", 
    "🍾 Formatos", 
    "📲 WhatsApp", 
    "📚 Guía Cálculos",
    "🧫 Saneados (CIP)",
    "🔄 Evaluador de Cambio"
])
# ------------------------------------------
# PESTAÑA 1: PROGRAMACIÓN DESDE JARABE
# ------------------------------------------
with tab1:
    st.markdown("### 🧪 Planificación de Lote según Jarabe Preparado")
    st.caption(
        "Calcula el rendimiento exacto del tanque, tiempos de embotellado e insumos requeridos."
    )

    with st.container():
        st.markdown("#### 📥 1. Parámetros del Tanque y Lote")
        col_in1, col_in2 = st.columns(2)

        with col_in1:
            jarabe_disponible = st.number_input(
                "🧪 Jarabe Disponible en Tanque (L)", value=7000, step=500
            )
            hora_inicio = st.time_input(
                "⏰ Hora de Inicio / Actual", 
                value=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).time()
            )

        with col_in2:
            botellas_por_pack = st.number_input(
                "📦 Botellas por Pack", value=6, step=1, key="pack_t1"
            )
            packs_por_pallet = st.number_input(
                "🏗️ Packs por Pallet", value=100, step=10, key="pallet_t1"
            )

    prod_t1 = calcular_produccion_lote(
        jarabe_disponible,
        factor_mezcla,
        vol_ml,
        botellas_por_pack,
        packs_por_pallet,
        bph_real,
    )

    st.session_state.packs_calculados = int(prod_t1["packs"])
    tiempo_fin = datetime.combine(datetime.today(), hora_inicio) + timedelta(
        hours=prod_t1["horas_prod"]
    )

    st.markdown("---")
    st.markdown("#### 📊 2. Proyección de Producción")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(
            "🥤 Bebida Final Total",
            f"{formato_miles(prod_t1['litros_bebida'])} L",
            delta=f"{formato_miles(prod_t1['botellas'])} botellas",
            delta_color="off",
        )
    with kpi2:
        st.metric(
            "📦 Packs Totales",
            formato_miles(prod_t1["packs"]),
            delta=f"{botellas_por_pack} bot/pack",
            delta_color="off",
        )
    with kpi3:
        st.metric(
            "🏗️ Pallets Totales",
            f"{prod_t1['pallets']:.1f}",
            delta=f"{int(packs_por_pallet)} packs/pallet",
            delta_color="off",
        )
    with kpi4:
        st.metric(
            "⏱️ Hora Término Est.",
            tiempo_fin.strftime("%H:%M hrs"),
            delta=f"Duración: {prod_t1['duracion_fmt']}",
            delta_color="normal",
        )

    st.info(
        f"💡 **Resumen del Lote:** A una velocidad real de **{formato_miles(bph_real)} BPH** (OEE: {oee}%), el embotellado de este tanque tomará **{prod_t1['duracion_fmt']}**."
    )

    st.markdown("---")
    st.markdown("#### 📋 3. Insumos y Materiales a Solicitar a Bodega")

    ins_t1 = calcular_insumos_requeridos(
        prod_t1["botellas"],
        prod_t1["packs"],
        prod_t1["pallets"],
        std_preforma_caja,
        std_tapa_caja,
        std_etiqueta_rollo,
        std_film_pack_rollo,
        std_carton_pallet,
        std_pallet_stretcher,
    )

    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        st.markdown(
            f'<div class="insumo-card" style="border-left-color: #0d6efd;"><div class="insumo-title">🧪 Cajas de Preforma</div><div class="insumo-qty">{ins_t1["preformas_cajas"]} Cajas</div><div class="insumo-sub">Exacto: {formato_miles(prod_t1["botellas"])} un.<br>Format: {formato_miles(std_preforma_caja)} u/caja</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="insumo-card" style="border-left-color: #6f42c1;"><div class="insumo-title">🏷️ Rollos de Etiqueta</div><div class="insumo-qty">{ins_t1["etiquetas_rollos"]} Rollos</div><div class="insumo-sub">Format: {formato_miles(std_etiqueta_rollo)} etiquetas/rollo</div></div>',
            unsafe_allow_html=True,
        )

    with ic2:
        st.markdown(
            f'<div class="insumo-card" style="border-left-color: #198754;"><div class="insumo-title">🔘 Cajas de Tapa</div><div class="insumo-qty">{ins_t1["tapas_cajas"]} Cajas</div><div class="insumo-sub">Exacto: {formato_miles(prod_t1["botellas"])} tapas<br>Format: {formato_miles(std_tapa_caja)} u/caja</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="insumo-card" style="border-left-color: #fd7e14;"><div class="insumo-title">📦 Rollos Film Paquete</div><div class="insumo-qty">{ins_t1["film_rollos"]} Rollos</div><div class="insumo-sub">Format: {formato_miles(std_film_pack_rollo)} packs/rollo</div></div>',
            unsafe_allow_html=True,
        )

    with ic3:
        st.markdown(
            f'<div class="insumo-card" style="border-left-color: #20c997;"><div class="insumo-title">📜 Pallets Cartón Corrugado</div><div class="insumo-qty">{ins_t1["carton_pallets"]} Pallet(s)</div><div class="insumo-sub">({int(prod_t1["pallets"])} planchas totales)</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="insumo-card" style="border-left-color: #d63384;"><div class="insumo-title">🌀 Film Envolvedora (Stretch)</div><div class="insumo-qty">{ins_t1["stretcher_rollos"]} Rollos</div><div class="insumo-sub">Format: {std_pallet_stretcher} pallets/rollo</div></div>',
            unsafe_allow_html=True,
        )

# ------------------------------------------
# PESTAÑA 2: BALANCE FINAL DE CIERRE DE LOTE
# ------------------------------------------
with tab2:
    st.subheader("🌊 Balance Total de Producto en Línea (Tanque + Mixer + Tuberías)")
    st.caption("Usa esta pestaña cuando te quede poco jarabe para calcular el remanente exacto.")

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        jarabe_tanque = st.number_input("Jarabe Tanque (L)", value=1500, step=100, key="j_t2")
        bebida_de_jarabe = jarabe_tanque * factor_mezcla
    with col_b:
        litros_mixer = st.number_input("Mixer (L)", value=200, step=20)
    with col_c:
        litros_tuberias = st.number_input("Tuberías (L)", value=1000, step=100)
    with col_d:
        pct_merma = st.number_input("Merma Est. (%)", value=2.0, step=0.5)

    litros_totales_sistema = bebida_de_jarabe + litros_mixer + litros_tuberias
    botellas_sistema = (litros_totales_sistema * 1000) / vol_ml
    packs_sistema = botellas_sistema / botellas_por_pack
    pallets_sistema = packs_sistema / packs_por_pallet
    tiempo_sistema_min = (botellas_sistema / bph_real) * 60 if bph_real > 0 else 0

    st.markdown("---")
    st.markdown("## 📊 Producto Final Producible")

    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Litros TOTALES", f"{formato_miles(litros_totales_sistema)} L")
    res2.metric("Botellas Reales", f"{formato_miles(botellas_sistema)} u")
    res3.metric("Packs Reales", f"{formato_miles(packs_sistema)} packs")
    res4.metric("Tiempo Estimado", f"{int(tiempo_sistema_min)} min")

    st.success(
        f"💡 **Resumen:** Quedan **{pallets_sistema:.1f} Pallets** de producción. Parada de línea proyectada en **{int(tiempo_sistema_min)} minutos**."
    )

    st.markdown("---")
    st.subheader("📋 Insumos Necesarios (Con Merma)")

    factor_merma = 1.0 + (pct_merma / 100.0)
    botellas_rem_merma = botellas_sistema * factor_merma
    packs_rem_merma = packs_sistema * factor_merma

    ins_t2 = calcular_insumos_requeridos(
        botellas_rem_merma,
        packs_rem_merma,
        pallets_sistema,
        std_preforma_caja,
        std_tapa_caja,
        std_etiqueta_rollo,
        std_film_pack_rollo,
        std_carton_pallet,
        std_pallet_stretcher,
    )

    ric1, ric2, ric3 = st.columns(3)
    with ric1:
        st.markdown(
            f'<div class="insumo-card"><div class="insumo-title">🧪 Cajas Preforma</div><div class="insumo-qty">{ins_t2["preformas_cajas"]} Cajas</div><div class="insumo-sub">({formato_miles(botellas_rem_merma)} un. @ {formato_miles(std_preforma_caja)}/caja)</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="insumo-card"><div class="insumo-title">🏷️ Rollos Etiqueta</div><div class="insumo-qty">{ins_t2["etiquetas_rollos"]} Rollos</div><div class="insumo-sub">(@ {formato_miles(std_etiqueta_rollo)}/rollo)</div></div>',
            unsafe_allow_html=True,
        )

    with ric2:
        st.markdown(
            f'<div class="insumo-card"><div class="insumo-title">🔘 Cajas Tapa</div><div class="insumo-qty">{ins_t2["tapas_cajas"]} Cajas</div><div class="insumo-sub">({formato_miles(botellas_rem_merma)} tapas @ {formato_miles(std_tapa_caja)}/caja)</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="insumo-card"><div class="insumo-title">📦 Rollos Film Paquete</div><div class="insumo-qty">{ins_t2["film_rollos"]} Rollos</div><div class="insumo-sub">(@ {formato_miles(std_film_pack_rollo)} packs/rollo)</div></div>',
            unsafe_allow_html=True,
        )

    with ric3:
        st.markdown(
            f'<div class="insumo-card"><div class="insumo-title">📜 Pallet Cartón</div><div class="insumo-qty">{ins_t2["carton_pallets"]} Pallet(s)</div><div class="insumo-sub">({pallets_sistema:.1f} planchas)</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="insumo-card"><div class="insumo-title">🌀 Film Stretch</div><div class="insumo-qty">{ins_t2["stretcher_rollos"]} Rollos</div><div class="insumo-sub">(@ {std_pallet_stretcher} pallets/rollo)</div></div>',
            unsafe_allow_html=True,
        )

# ------------------------------------------
# PESTAÑA 3: FICHA TÉCNICA DE FORMATOS
# ------------------------------------------
with tab3:
    st.subheader("📋 Matriz Operativa de Formatos Línea 2")

    envase_sel = st.selectbox(
        "Seleccione el Tipo de Botella / Envase",
        list(FORMATOS_LINEA_2.keys()),
        key="sel_tab3",
    )
    data_env = FORMATOS_LINEA_2[envase_sel]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("⚖ Preforma", f"{data_env['peso_pref_g']} g")
    col2.metric("🌡️ Temp. Llenado", data_env["temp_llenado"])
    col3.metric("🧼 Etiqueta", data_env["etiqueta"])
    col4.metric("📦 Config. Paquete", data_env["paquete"])

    st.markdown("---")
    st.markdown("#### ⚡ Velocidades Nominales por Equipo (BPH)")

    df_vel = pd.DataFrame(
        [
            {
                "Ergobloc L": f"{data_env['bph_ergobloc']:,}".replace(",", "."),
                "Sleevematic (x2)": (
                    f"{data_env['bph_sleevematic']:,}".replace(",", ".")
                    if data_env["bph_sleevematic"] > 0
                    else "N/A"
                ),
                "Variopac": f"{data_env['bph_variopac']:,}".replace(",", "."),
                "Modulpal": f"{data_env['bph_modulpal']:,}".replace(",", "."),
                "Stretch W.": f"{data_env['bph_stretch']:,}".replace(",", "."),
            }
        ]
    )
    st.dataframe(df_vel, use_container_width=True, hide_index=True)

# ------------------------------------------
# PESTAÑA 4: NOTIFICACIÓN WHATSAPP
# ------------------------------------------
with tab4:
    st.subheader("📲 Generador de Notificación de Turno")

    col1, col2 = st.columns(2)
    with col1:
        opcion_saludo = st.selectbox(
            "Saludo inicial",
            [
                "Buenos días\nFavor notificar:",
                "Buenas tardes\nFavor notificar:",
                "Buenas noches\nFavor notificar:",
                "Favor notificar",
                "Personalizado",
            ],
        )
        saludo_txt = (
            st.text_input("Escribe el saludo", value="Buenos días\nFavor notificar:")
            if opcion_saludo == "Personalizado"
            else opcion_saludo
        )
    with col2:
        turno_sel = st.selectbox("Turno", ["Turno A", "Turno B", "Turno C"])

    col3, col4 = st.columns(2)
    with col3:
        linea_sel = st.text_input("Línea", value="Línea 2")
    with col4:
        op_num = st.text_input("Orden de Producción (OP)", value="6600225198")

    col5, col6 = st.columns(2)
    with col5:
        idx_sab_notif = 0
        if sabor_nombre in LISTA_SABORES:
            idx_sab_notif = LISTA_SABORES.index(sabor_nombre)
        sabor_sel = st.selectbox("Producto / Sabor", LISTA_SABORES, index=idx_sab_notif, key="sab_notif")
        sabor_txt = (
            st.text_input("Escribe el sabor", value="Pap")
            if sabor_sel == "Otro (Escribir manualmente)"
            else sabor_sel
        )
    with col6:
        idx_fmt_notif = 0
        if envase_nombre in LISTA_FORMATOS:
            idx_fmt_notif = LISTA_FORMATOS.index(envase_nombre)

        fmt_sel = st.selectbox("Formato", LISTA_FORMATOS, index=idx_fmt_notif)
        
        # --- LÓGICA DE SIMPLIFICACIÓN DEL FORMATO ---
        # Extrae automáticamente el tamaño y unidad limpios (ej: 600ml, 1.5 Lts, 500ml)
        if fmt_sel == "Otro (Escribir manualmente)":
            fmt_txt = st.text_input("Escribe el formato", value="600ml")
        else:
            if "500" in fmt_sel:
                fmt_txt = "500ml"
            elif "600" in fmt_sel:
                fmt_txt = "600ml"
            elif "1.5" in fmt_sel:
                fmt_txt = "1.5 Lts"
            elif "1.75" in fmt_sel:
                fmt_txt = "1.75 Lts"
            else:
                fmt_txt = fmt_sel.split()[0] + ("ml" if "ml" in fmt_sel.lower() else " Lts")

    prod_completo = f"{sabor_txt} {fmt_txt}".strip()

    col7, col8 = st.columns(2)
    with col7:
        cajas_cant = st.number_input(
            "Cajas / Packs Producidos",
            value=st.session_state.packs_calculados
            if st.session_state.packs_calculados > 0
            else PACKS_DEFECTO_INICIAL,
            step=100,
        )
        cajas_formateadas = formato_miles(cajas_cant)
    with col8:
        fecha_notif = st.text_input(
            "Fecha", value=datetime.now().strftime("%d/%m/%Y")
        )

    mensaje_final = f"{saludo_txt}\n{turno_sel} - {linea_sel}\n{prod_completo}\nOP: {op_num}\nCajas: {cajas_formateadas}\n{fecha_notif}"

    st.markdown("### 📄 Mensaje Generado:")
    
    # Muestra el mensaje en un recuadro limpio que incluye botón automático de copiar
    st.code(mensaje_final, language=None)

    whatsapp_url = (
        f"https://api.whatsapp.com/send?text={urllib.parse.quote(mensaje_final)}"
    )
    st.link_button(
        "📲 Enviar por WhatsApp",
        whatsapp_url,
        type="primary",
        use_container_width=True,
    )
# ------------------------------------------
# PESTAÑA 5: GUÍA Y MANUAL DE CÁLCULOS
# ------------------------------------------
with tab5:
    st.subheader("📚 Manual de Cálculos Operativos - Línea 2")
    st.caption(
        "Aprende paso a paso cómo la aplicación calcula la bebida, los tiempos y los insumos de producción."
    )

    # --- SECCIÓN 1: FACTOR DE MEZCLA ---
    with st.expander("🥤 1. ¿Cómo se calcula el Factor de Mezcla (Rendimiento)?", expanded=True):
        st.markdown("""
        El **Factor de Mezcla** representa cuántos litros de bebida final se obtienen a partir de **1 litro de jarabe preparado**.

        #### 📐 Fórmula:
        `Factor de Mezcla = Partes de Agua + 1 (Parte de Jarabe)`

        #### 💡 Ejemplos según la Tabla CCU:
        * **Rockstar / POP (3 de agua / 1 de jarabe):** 3 + 1 = **4.0**
        * **Crush / Limón Soda (4 de agua / 1 de jarabe):** 4 + 1 = **5.0**
        * **Pepsi / 7Up (5 de agua / 1 de jarabe):** 5 + 1 = **6.0**
        * **Bilz / Pap / Kem (6.125 de agua / 1 de jarabe):** 6.125 + 1 = **7.125**

        ---
        #### 🧪 Ejemplo Práctico:
        Si tienes **7.000 Litros de Jarabe** de *Bilz Regular* (Factor 7.125):
        
        `Litros Bebida = 7.000 L Jarabe × 7.125 = 49.875 Litros de Bebida`
        """)

    # --- SECCIÓN 2: BOTELLAS, PACKS Y PALLETS ---
    with st.expander("📦 2. ¿Cómo se calculan las Unidades, Packs y Pallets?"):
        st.markdown("""
        Una vez conocidos los **Litros Totales de Bebida**, convertimos ese volumen a unidades de empaque.

        #### 📐 Fórmulas:
        1. **Botellas Totales:**  
           `Botellas = (Litros Bebida × 1.000) / Formato (ml)`
        2. **Packs Producidos:**  
           `Packs = Botellas Totales / Botellas por Pack (ej: 6)`
        3. **Pallets Completos:**  
           `Pallets = Packs Totales / Packs por Pallet (ej: 100)`

        ---
        #### 🧪 Ejemplo Práctico (Formato 600 ml - Pack de 6):
        Con los **49.875 Litros** del ejemplo anterior:
        * **Botellas:** (49.875 × 1.000) / 600 = **83.125 botellas**
        * **Packs:** 83.125 / 6 = **13.854 packs**
        * **Pallets:** 13.854 / 100 = **138,5 pallets**
        """)

    # --- SECCIÓN 3: TIEMPOS Y VELOCIDAD EFECTIVA (OEE) ---
    with st.expander("⏱️ 3. ¿Cómo se calcula el Tiempo de Envasado y Término?"):
        st.markdown("""
        El tiempo estimado depende de la **Velocidad Nominal (BPH)** del equipo y de la eficiencia del turno (**OEE %**).

        #### 📐 Fórmulas:
        1. **Velocidad Real (BPH Real):**  
           `BPH Real = BPH Nominal × (OEE % / 100)`
        2. **Horas de Producción:**  
           `Horas = Botellas Totales / BPH Real`

        ---
        #### 🧪 Ejemplo Práctico:
        * **Ergobloc L2 en 600ml:** Velocidad nominal = **60.000 BPH**
        * **OEE del Turno:** **85%**
        * **Velocidad Real:** 60.000 × 0,85 = **51.000 BPH**

        Para envasar **83.125 botellas**:  
        `Horas = 83.125 / 51.000 = 1,63 horas` → **1h 38m**
        """)

    # --- SECCIÓN 4: CÁLCULO DE INSUMOS BODEGA ---
    with st.expander("📦 4. ¿Cómo se calculan los Insumos y Materiales?"):
        st.markdown("""
        Para evitar quiebres de línea, los insumos se aproximan siempre **hacia arriba** (al entero superior más cercano) usando el estándar de cada empaque.

        #### 📐 Fórmulas de Solicitud:
        * **Cajas de Preformas:** `RedondearArriba( Botellas / Preformas por Caja )`
        * **Cajas de Tapas:** `RedondearArriba( Botellas / Tapas por Caja )`
        * **Rollos de Etiqueta:** `RedondearArriba( Botellas / Etiquetas por Rollo )`
        * **Rollos de Film Paquete:** `RedondearArriba( Packs / Packs por Rollo )`

        ---
        #### 💡 Nota de Merma:
        En la pestaña de **Balance Final**, el sistema multiplica las botellas teóricas por un factor de merma (ej: **2%** adicional) antes de calcular las cajas de insumo para cubrir pérdidas en soplado o etiquetado.
        """)

# ------------------------------------------
# PESTAÑA 6: DEFINICIONES Y CRITERIOS MANDATORIOS CIP
# ------------------------------------------
with tab6:
    st.subheader("📚 Pestaña 6: Definiciones y Conceptos Clave de Saneados")
    st.caption("Estándar Oficial NPR-ASC-DOC-16 | Versión 22 (Edición Marzo 2026)")

    # ==========================================
    # SECCIÓN 1: TIEMPOS Y TIPOS DE RECETA
    # ==========================================
    st.markdown("### ⏱️ 1. Tiempos y Métodos de Recetas Disponibles")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Empuje con Agua", "15 min", "Empuje de 15 min")
    col_r2.metric("Agua Fría", "20 min", "Enjuague T° ambiente")
    col_r3.metric("Agua Caliente", "21 min", "Esterilización 85°C")

    col_r4, col_r5, col_r6, col_r7 = st.columns(4)
    col_r4.metric("CIP 3 Pasos", "50 min", "Enjuague-Desinfección-Enjuague")
    col_r5.metric("CIP 5 Pasos", "62 min", "Enjuague-Soda-Desinf.-Enjuague")
    col_r6.metric("CIP 5 Pasos Caliente", "62 min", "+ Termodesinfección")
    col_r7.metric("CIP 7 Pasos Caliente", "73 min", "+ Ácido y Potenciador")

    st.markdown("---")

    # ==========================================
    # SECCIÓN 2: DEFINICIONES MANDATORIAS (GENERALES Y BLYS)
    # ==========================================
    st.markdown("### 📋 2. Definiciones Mandatorias y Criterios Operativos")

    tab_gen, tab_blys, tab_mat = st.tabs(["📌 Criterios Generales", "🍹 Criterios Solo BLYS", "🏭 Reglas de Proceso / Matriz"])

    with tab_gen:
        st.markdown("#### **Criterios Adicionales a la Matriz (Generales)**")
        st.markdown("""
        * **Cada 7 Días (168 hrs máx):** Requiere obligatoriamente al menos un **CIP 5 Pasos**.
        * **Aseo COP (Manual):** Se debe realizar al menos **3 veces por semana** en la línea de envasado.
        * **Línea Detenida ≥ 8 hrs (Sin Saneado al término):** Iniciar con **CIP 3 Pasos** antes de retomar producción (ej: corte de luz imprevisto).
        * **Línea Detenida ≥ 8 hrs (Con Saneado al término):** Realizar enjuague de **Agua Fría** al retomar (ej: detención programada con vaciado de mixer y CIP realizado).
        * **Intervención en contacto con Jarabe/Bebida:** Realizar **Agua Caliente** tras intervenir válvulas, bombas de envío o tuberías.
        * **Desviación en Validación de Saneado:** Aplicar **Agua Fría** adicional solo en caso de desviación Sensorial, Trazas de Químico o Trazas de Azúcar.
        * **Enjuagues:** Todos los enjuagues de agua fría deben realizarse **desde Elaboración**.
        """)

    with tab_blys:
        st.markdown("#### **Criterios Mandatorios Exclusivos para BLYS**")
        st.markdown("""
        * **Producción Continua > 24 hrs:** Debe realizar saneado **CIP 3 Pasos** cada 24 horas.
        * **Línea Detenida ≥ 4 hrs:** Si la línea presenta una detención mayor a 4 horas, se debe realizar **CIP 5 Pasos Caliente** antes de reiniciar operación.
        * **Línea Detenida ≥ 8 hrs (Sin Saneado):** Partir con **CIP 3 Pasos** antes de retomar.
        * **Línea Detenida ≥ 8 hrs (Con Saneado):** Realizar **Agua Fría** antes de retomar.
        * **Intervenciones o Desviaciones:** Aplican las mismas reglas que el criterio general (Agua Caliente para intervenciones y Agua Fría para desviaciones).
        """)

    with tab_mat:
        st.markdown("#### **Definiciones Específicas de Matriz y Elaboración**")
        st.markdown("""
        * **Materia Prima Pungente/Orgánica (Antes):** Realizar **CIP 3 Pasos** antes de fabricar jarabes con MP de olor/sabor penetrante por su naturaleza orgánica.
        * **Pungente 2:** Ingreso mandatorio con **CIP 5 Pasos Caliente**.
        * **Materia Prima Pungente (Después):** Realizar **CIP 5 Pasos Caliente** al término/salida.
        * **Materia Prima Orgánica (Después):** Realizar **CIP 5 Pasos** al término/salida.
        * **Producción Continua Lipton > 24 hrs:** Realizar **CIP 3 Pasos** cada 24 hrs.
        * **Detención Línea Jarabe-Lipton > 4 hrs:** Realizar **CIP 5 Pasos Caliente**.
        * **Línea Rockstar (Tanques 519 y 520):** CIP 3 Pasos después de 24 hrs a los tanques y línea.
        * **Línea 4 Gatorade Zero (> 24 hrs):** CIP 5 Pasos Fríos cada 24 hrs en producción continua.
        * **Saneado de Pasteurizador:** Debe quedar limpio e higienizado **inmediatamente después de su uso**.
        """)

    st.markdown("---")

    # ==========================================
    # SECCIÓN 3: PROTOCOLO DE VALIDACIÓN DE SANEADOS
    # ==========================================
    st.markdown("### 🧪 3. Protocolo Mandatorio de Validación de Saneados")
    
    col_v1, col_v2, col_v3 = st.columns(3)
    
    with col_v1:
        st.info("👅 **Validación Sensorial**")
        st.markdown("""
        * **Aplica a:** Todas las recetas.
        * **Método:** Evaluación contra muestra patrón en la última agua de enjuague.
        * **Exigencia:** Requiere **2 panelistas** (Analista de Calidad + Operador de Elaboración).
        """)

    with col_v2:
        st.warning("🧪 **Trazas de Químico**")
        st.markdown("""
        * **Aplica a:** CIP 3, CIP 5 y CIP 7 Pasos.
        * **Método:** Medición en la última agua de enjuague.
        * **Herramientas:** Indicador de **Fenolftaleína** o **Tiras de Ácido**.
        """)

    with col_v3:
        st.success("🍬 **Trazas de Azúcar**")
        st.markdown("""
        * **Aplica a:** Transición de productos con azúcar hacia productos Zero o Light.
        * **Método:** Medición en la última agua de enjuague.
        * **Herramienta:** Medidor **Reflectoquant**.
        """)
# ------------------------------------------
# PESTAÑA 7: MATRIZ DE CAMBIO DE PRODUCTO Y DIAGNÓSTICO EN TURNO
# ------------------------------------------
with tab7:
    st.subheader("🔄 Pestaña 7: Evaluador Interactivo de Cambio de Producto (L2)")
    st.caption("Matriz de Transición Envasado L2 | NPR-ASC-DOC-16 v22")

    # Lista consolidada de Sabores por Categoría Oficial
    PUNGENTES = ["H2Oh! Toronchello", "Kem Xtreme", "Kem Xtreme Blue Berry", "Kem Xtreme Suggar Free", "Kem Piña Maracuya", "Rockstar", "Rockstar Mango", "Rockstar Sandia"]
    PUNGENTES_2_JUGO = ["Lipton Durazno", "Lipton Limón", "Lipton Te verde Mango Zero", "Lipton limón Zero", "Lipton Raspberry Zero", "Crush 5% Jugo", "Kem Xtreme Flamin Hot"]
    COLOR_FUERTE = ["Pepsi", "Pepsi Zero", "Pepsi Light", "Bilz", "Bilz Zero", "Crush", "Crush Zero", "Crush sin jugo"]
    BLANCOS = ["Seven UP", "Seven Up Zero", "Agua Tónica", "Agua Tónica Zero", "Ginger Ale", "Ginger Ale Light", "Ginger Ale Zero"]
    SIN_RESTRICCION = ["H2Oh! Naranchelo", "H2Oh! Lima Limon", "H2Oh! Limonchelo", "H2Oh! Limoneto", "Kem", "Kem Zero", "Pap", "Pap Zero", "Limón Soda", "Limón Soda Zero"]

    TODOS_LOS_SABORES = sorted(list(set(PUNGENTES + PUNGENTES_2_JUGO + COLOR_FUERTE + BLANCOS + SIN_RESTRICCION)))

    # Selección de Productos
    st.markdown("### 1. Selección de Transición de Producto")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        prod_saliente = st.selectbox("🥤 Producto Saliente (Desde / Fila)", TODOS_LOS_SABORES, index=0, key="eval_saliente")
    with col_p2:
        prod_entrante = st.selectbox("🍹 Producto Entrante (A / Columna)", TODOS_LOS_SABORES, index=1, key="eval_entrante")

    st.markdown("---")
    st.markdown("### 2. Dictamen Operativo del Saneado")

    # Identificación de Familias
    es_sal_pungente = prod_saliente in PUNGENTES or prod_saliente in PUNGENTES_2_JUGO
    es_ent_blanco_sinrest = prod_entrante in BLANCOS or prod_entrante in SIN_RESTRICCION
    
    # Regla Mismo Sabor Zero -> Normal
    es_mismo_sabor_zero_a_norm = (
        ("Zero" in prod_saliente or "Light" in prod_saliente) and
        (prod_saliente.replace(" Zero", "").replace(" Light", "").strip() == prod_entrante.strip())
    )

    # Lógica de Evaluación
    if es_mismo_sabor_zero_a_norm:
        st.info("💧 **PROTOCOLO: EMPUJE CON AGUA FRÍA**")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("⏱️ Tiempo Receta", "15 min", "Empuje continuo")
        c2.metric("📟 Receta HMI", "RN° 1 C/D / RN° 2 S/D")
        c3.metric("🧪 Aseo Jarabería", "Empuje Agua Fría")

        st.markdown("""
        * **Detalle del Procedimiento:** Considerar empuje continuo con agua tratada de **15 minutos** para barrido de edulcorantes/azúcar antes de ingresar la versión normal[cite: 1, 3].
        * **Validación:** Sensorial + Medición de trazas de azúcar con **Reflectoquant**[cite: 4].
        """)

    elif es_sal_pungente and es_ent_blanco_sinrest:
        st.error("🚫 **PROHIBIDO / RESTRICCIÓN DE CALIDAD CRÍTICA**")
        st.markdown("### ⚠️ ***No realizar producción***")
        st.warning("La matriz prohíbe el paso directo de productos Pungentes / Lipton / Jugo hacia productos Blancos o Sin Restricción por riesgo crítico de contaminación sensorial de sabor y olor[cite: 1, 4].")
        st.caption("Acción en turno: Detener cambio de formato y consultar con el Analista o Jefe de Calidad.")

    elif es_sal_pungente:
        st.markdown("### 🔴 **CIP 5 PASOS CALIENTE**")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("⏱️ Tiempo Receta", "62 min", "+ Termodesinfección")
        c2.metric("📟 Receta HMI", "RN° 12 S/D / RN° 13")
        c3.metric("🧪 Aseo Jarabería", "S + Q + A / S + A + Q")

        st.markdown("""
        * **Secuencia CIP:** Enjuague ➔ Detergente Alcalino (Soda) ➔ Desinfectante ➔ Termodesinfección (85°C) ➔ Enjuague final[cite: 3].
        * **Puntos Críticos:** Saneado de alta exigencia para desodorización de matrices aromáticas orgánicas[cite: 4].
        """)

    elif prod_saliente in COLOR_FUERTE:
        st.markdown("### 🟡 **CIP 3 PASOS / CIP 5 PASOS**")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("⏱️ Tiempo Receta", "50 min - 62 min", "Según recirculación")
        c2.metric("📟 Receta HMI", "RN° 10 C/D / RN° 11 S/D")
        c3.metric("🧪 Aseo Jarabería", "S + Q / S + A")

        st.markdown("""
        * **Secuencia CIP:** Enjuague previo ➔ Desinfección / Lavado Alcalino ➔ Enjuague final con verificación de pH/conductividad[cite: 3].
        """)

    else:
        st.markdown("### 🟢 **AGUA CALIENTE / CIP 3 PASOS ESTÁNDAR**")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("⏱️ Tiempo Receta", "21 min - 50 min", "Según matiz de sabor")
        c2.metric("📟 Receta HMI", "RN° 1 C/D / RN° 3 C/D")
        c3.metric("🧪 Aseo Jarabería", "S / S + A")

        st.markdown("""
        * **Secuencia CIP:** Enjuague regular o esterilización térmica a 85°C para productos de la misma familia o baja complejidad[cite: 3].
        """)

    st.markdown("---")

    # ==========================================
    # SECCIÓN 3: VERIFICACIONES Y CHECKLIST DE VALIDACIÓN
    # ==========================================
    st.markdown("### 3. Protocolo Mandatorio de Liberación de Calidad")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("**📋 Pruebas Requeridas en la última agua de enjuague:**")
        
        # Validación Sensorial Obligatoria
        st.checkbox("👅 **Validación Sensorial:** Muestra patrón evaluada por 2 panelistas (Analista + Operador Elaboración)[cite: 4].", value=True)
        
        # Trazas Químicas
        if es_sal_pungente or prod_saliente in COLOR_FUERTE:
            st.checkbox("🧪 **Trazas de Químico:** Prueba de Fenolftaleína o Tiras de Ácido negativa[cite: 4].", value=True)
        
        # Trazas de Azúcar
        if "Zero" in prod_entrante or "Light" in prod_entrante or es_mismo_sabor_zero_a_norm:
            st.checkbox("🍬 **Trazas de Azúcar:** Medición con Reflectoquant en enjuague final (Paso a producto Zero/Light)[cite: 4].", value=True)

    with col_v2:
        st.info("""
        💡 **Nota Técnica Operativa:**
        * Los enjuagues con agua fría siempre deben realizarse **desde Elaboración**.
        * Si el saneado presenta desviación en química, azúcar o sensorial, se debe repetir un enjuague adicional con **Agua Fría**[cite: 3].
        """)

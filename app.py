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
    std_tapa_caja = st.number_input("Tapas por caja", value=50000, step=5000)
    std_etiqueta_rollo = st.number_input("Etiquetas por rollo", value=18000, step=1000)
    std_film_pack_rollo = st.number_input("Packs por rollo film", value=1200, step=100)
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🧪 1. Programación por Jarabe",
        "🌊 2. Balance Final",
        "🍾 3. Ficha Técnica de Formatos",
        "📲 4. Notificación WhatsApp",
        "📚 5. Guía de Cálculos",
    ]
)

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
                "⏰ Hora de Inicio / Actual", value=datetime.now().time()
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
        fmt_txt = (
            st.text_input("Escribe el formato", value="600ml")
            if fmt_sel == "Otro (Escribir manualmente)"
            else fmt_sel
        )

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
    st.markdown(
        f'<div class="whatsapp-box">{mensaje_final}</div>',
        unsafe_allow_html=True,
    )

    whatsapp_url = (
        f"https://api.whatsapp.com/send?text={urllib.parse.quote(mensaje_final)}"
    )
    st.link_button(
        "📲 Enviar por WhatsApp",
        whatsapp_url,
        type="primary",
        use_container_width=True,
    )

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

# --- INICIALIZACIÓN DE SESSION STATE ---
if "packs_calculados" not in st.session_state:
    st.session_state.packs_calculados = 15724

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #dee2e6;
        border-left: 5px solid #0d6efd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
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
""", unsafe_allow_html=True)

# --- BASE DE DATOS OFICIAL LÍNEA 2 CCU (SEGÚN MATRIZ MATRIZ DE FORMATOS) ---
MATRIZ_CCU = {
    "1. 500 ml Rockstar": {
        "ml": 500, "factor": 4.0, "co2": 3.10, "peso_pref": 19.5, "temp": 20, 
        "etiq": "Sleeve Fullbody", "sleevematic": True, "packs_opt": [6, 12],
        "bph_ergobloc": 60000, "bph_variopac": 69000, "pref_caja": 15000
    },
    "2. 500 ml POP (Huevo)": {
        "ml": 500, "factor": 7.125, "co2": 3.20, "peso_pref": 19.5, "temp": 20, 
        "etiq": "Sleeve Fullbody", "sleevematic": True, "packs_opt": [6, 12],
        "bph_ergobloc": 42000, "bph_variopac": 48300, "pref_caja": 15000
    },
    "3. 600 ml BGP": {
        "ml": 600, "factor": 7.125, "co2": 4.20, "peso_pref": 19.5, "temp": 15, 
        "etiq": "BOPP", "sleevematic": False, "packs_opt": [6, 12],
        "bph_ergobloc": 60000, "bph_variopac": 69000, "pref_caja": 15000
    },
    "4. 600 ml AXL": {
        "ml": 600, "factor": 7.125, "co2": 4.20, "peso_pref": 19.5, "temp": 15, 
        "etiq": "BOPP", "sleevematic": False, "packs_opt": [6, 12],
        "bph_ergobloc": 60000, "bph_variopac": 69000, "pref_caja": 15000
    },
    "5. 600 ml Ripples (BOPP)": {
        "ml": 600, "factor": 7.125, "co2": 4.20, "peso_pref": 19.5, "temp": 15, 
        "etiq": "BOPP", "sleevematic": False, "packs_opt": [6, 12],
        "bph_ergobloc": 60000, "bph_variopac": 69000, "pref_caja": 15000
    },
    "5.1. 600 ml Ripples (Sleeve)": {
        "ml": 600, "factor": 7.125, "co2": 4.20, "peso_pref": 19.5, "temp": 15, 
        "etiq": "Sleeve Halfbody", "sleevematic": True, "packs_opt": [6, 12],
        "bph_ergobloc": 60000, "bph_variopac": 69000, "pref_caja": 15000
    },
    "6. 600 ml B&P": {
        "ml": 600, "factor": 7.125, "co2": 3.75, "peso_pref": 19.5, "temp": 20, 
        "etiq": "BOPP", "sleevematic": False, "packs_opt": [6, 12],
        "bph_ergobloc": 60000, "bph_variopac": 69000, "pref_caja": 15000
    },
    "7.1. 1,5 l Carolina (BOPP)": {
        "ml": 1500, "factor": 7.125, "co2": 4.20, "peso_pref": 37.0, "temp": 20, 
        "etiq": "BOPP", "sleevematic": False, "packs_opt": [6],
        "bph_ergobloc": 38000, "bph_variopac": 43700, "pref_caja": 8000
    },
    "7.2. 1,5 l Carolina (Sleeve)": {
        "ml": 1500, "factor": 7.125, "co2": 4.20, "peso_pref": 37.0, "temp": 20, 
        "etiq": "Sleeve Halfbody", "sleevematic": True, "packs_opt": [6],
        "bph_ergobloc": 36000, "bph_variopac": 41400, "pref_caja": 8000
    },
    "8. 1,5 l Genérica": {
        "ml": 1500, "factor": 7.125, "co2": 3.95, "peso_pref": 37.0, "temp": 20, 
        "etiq": "BOPP", "sleevematic": False, "packs_opt": [6],
        "bph_ergobloc": 38000, "bph_variopac": 43700, "pref_caja": 8000
    },
    "9. 1,5 l Crush": {
        "ml": 1500, "factor": 5.0, "co2": 3.95, "peso_pref": 37.0, "temp": 20, 
        "etiq": "BOPP", "sleevematic": False, "packs_opt": [6],
        "bph_ergobloc": 38000, "bph_variopac": 43700, "pref_caja": 8000
    },
    "10. 1,5 l B&P": {
        "ml": 1500, "factor": 7.125, "co2": 3.75, "peso_pref": 37.0, "temp": 20, 
        "etiq": "BOPP", "sleevematic": False, "packs_opt": [6],
        "bph_ergobloc": 38000, "bph_variopac": 42560, "pref_caja": 8000
    },
    "11. 1,75 l Cisne": {
        "ml": 1750, "factor": 7.125, "co2": 4.20, "peso_pref": 47.6, "temp": 20, 
        "etiq": "BOPP", "sleevematic": False, "packs_opt": [6],
        "bph_ergobloc": 34000, "bph_variopac": 39100, "pref_caja": 6000
    }
}

LISTA_SABORES = [
    "Bilz", "Bilz Zero", "Pap", "Pap Zero", "Kem", "Kem Zero", "Kem piña",
    "Pepsi Reducida", "Pepsi Zero", "7Up", "7Up Zero", "Limón Soda",
    "Limón Soda Zero", "Crush", "Crush Zero", "Rockstar Original",
    "Rockstar Sandía", "Rockstar Mango", "POP Huevo", "Otro (Escribir manualmente)"
]

# --- ENCABEZADO ---
st.title("⚡ Control de Producción e Insumos - Línea 2 CCU")
st.caption("Estandarizado según Matriz Oficial de Formatos y Equipos Línea 2")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración del Formato")
    envase_sel = st.selectbox("Seleccionar Envase Matriz", list(MATRIZ_CCU.keys()))
    data_format = MATRIZ_CCU[envase_sel]

    st.subheader("📌 Datos Técnicos de Matriz")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.write(f"**Volumen:** {data_format['ml']} ml")
        st.write(f"**Preforma:** {data_format['peso_pref']} g")
        st.write(f"**Temp. Llenado:** {data_format['temp']} °C")
    with col_sb2:
        st.write(f"**Etiqueta:** {data_format['etiq']}")
        st.write(f"**CO₂ Target:** {data_format['co2']} v/v")
        if data_format['sleevematic']:
            st.warning("⚠️ Requiere Sleevematic")

    st.subheader("⚡ Parámetros Operativos")
    factor_mezcla = st.number_input("Factor de Mezcla", value=data_format["factor"], step=0.1)
    bph_nominal = st.number_input("Velocidad Nominal Ergobloc (BPH)", value=data_format["bph_ergobloc"], step=1000)
    
    st.subheader("Eficiencia de Línea")
    oee = st.slider("OEE / Eficiencia Real (%)", min_value=50, max_value=100, value=100)
    bph_real = bph_nominal * (oee / 100.0)
    st.info(f"Velocidad Real: **{int(bph_real):,} BPH**")

    st.subheader("📦 Capacidades Estándar de Bodega")
    std_preforma_caja = st.number_input("Preformas x Caja", value=data_format["pref_caja"], step=500)
    std_tapa_caja = st.number_input("Tapas x Caja", value=5000, step=500)
    std_etiqueta_rollo = st.number_input("Etiquetas/Sleeves x Rollo", value=10000, step=1000)
    std_film_pack_rollo = st.number_input("Packs x Rollo Film Paquete", value=2700, step=100)
    std_carton_pallet = st.number_input("Planchas Cartón x Pallet", value=400, step=50)
    std_pallet_stretcher = st.number_input("Pallets x Rollo Stretcher", value=35, step=5)

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs([
    "🧪 1. Programación por Jarabe Disponible", 
    "🌊 2. Balance Final de Cierre de Lote",
    "📲 3. Notificación WhatsApp"
])

# ==========================================
# PESTAÑA 1: PROGRAMACIÓN DESDE JARABE
# ==========================================
with tab1:
    st.markdown("### 🧪 Planificación de Lote según Jarabe Preparado")
    
    with st.container():
        st.markdown("#### 📥 1. Parámetros del Tanque y Lote")
        col_in1, col_in2 = st.columns(2)
        
        with col_in1:
            jarabe_disponible = st.number_input("🧪 Jarabe Disponible en Tanque (L)", value=7000, step=500)
            hora_inicio = st.time_input("⏰ Hora de Inicio / Actual", value=datetime.now().time())

        with col_in2:
            opciones_pack = data_format["packs_opt"]
            if len(opciones_pack) > 1:
                botellas_por_pack = st.radio("📦 Formato de Empaquetado (Variopac)", opciones_pack, format_func=lambda x: "3x2 (6 bot/pack)" if x==6 else "4x3 (12 bot/pack)")
            else:
                botellas_por_pack = opciones_pack[0]
                st.info(f"📦 Empaquetado fijo para este envase: **3x2 ({botellas_por_pack} bot/pack)**")

            packs_por_pallet = st.number_input("🏗️ Packs por Pallet", value=100 if data_format['ml']<=600 else 60, step=5, key="pallet_t1")

    # Cálculos principales
    litros_bebida_total = jarabe_disponible * factor_mezcla
    total_botellas = (litros_bebida_total * 1000) / data_format["ml"]
    total_packs = total_botellas / botellas_por_pack
    st.session_state.packs_calculados = int(total_packs)
    total_pallets = total_packs / packs_por_pallet
    
    # Consumo de Resina
    kilos_pet = (total_botellas * data_format["peso_pref"]) / 1000.0

    horas_prod = total_botellas / bph_real if bph_real > 0 else 0
    minutos_totales = int(horas_prod * 60)
    horas_format = minutos_totales // 60
    min_format = minutos_totales % 60
    tiempo_fin = datetime.combine(datetime.today(), hora_inicio) + timedelta(hours=horas_prod)

    st.markdown("---")
    st.markdown("#### 📊 2. Proyección de Producción")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("🥤 Bebida Final Total", f"{int(litros_bebida_total):,} L".replace(",", "."), delta=f"{int(total_botellas):,} botellas".replace(",", "."), delta_color="off")
    with kpi2:
        st.metric("📦 Packs Totales", f"{int(total_packs):,}".replace(",", "."), delta=f"{botellas_por_pack} bot/pack", delta_color="off")
    with kpi3:
        st.metric("🏗️ Pallets Totales", f"{total_pallets:.1f}", delta=f"{int(packs_por_pallet)} packs/pallet", delta_color="off")
    with kpi4:
        st.metric("⏱️ Hora Término Est.", tiempo_fin.strftime("%H:%M hrs"), delta=f"Duración: {horas_format}h {min_format}m", delta_color="normal")

    st.info(f"💡 **Masa de Resina:** Este lote consumirá **{kilos_pet:,.1f} kg** de PET en preformas ({data_format['peso_pref']}g/u). Tiempo de llenado: **{horas_format}h {min_format}m**.")

    st.markdown("---")
    st.markdown("#### 📋 3. Insumos y Materiales a Solicitar a Bodega")

    cajas_preforma = math.ceil(total_botellas / std_preforma_caja)
    cajas_tapa = math.ceil(total_botellas / std_tapa_caja)
    rollos_etiqueta = math.ceil(total_botellas / std_etiqueta_rollo)
    rollos_film = math.ceil(total_packs / std_film_pack_rollo)
    pallets_carton = math.ceil(total_pallets / std_carton_pallet)
    rollos_stretcher = math.ceil(total_pallets / std_pallet_stretcher)

    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        st.markdown(f'<div class="insumo-card" style="border-left-color: #0d6efd;"><div class="insumo-title">🧪 Cajas Preforma ({data_format["peso_pref"]}g)</div><div class="insumo-qty">{cajas_preforma} Cajas</div><div class="insumo-sub">Exacto: {int(total_botellas):,} un. ({std_preforma_caja:,} u/caja)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card" style="border-left-color: #6f42c1;"><div class="insumo-title">🏷️ Rollos ({data_format["etiq"]})</div><div class="insumo-qty">{rollos_etiqueta} Rollos</div><div class="insumo-sub">Format: {std_etiqueta_rollo:,} un/rollo</div></div>', unsafe_allow_html=True)

    with ic2:
        st.markdown(f'<div class="insumo-card" style="border-left-color: #198754;"><div class="insumo-title">🔘 Cajas de Tapa</div><div class="insumo-qty">{cajas_tapa} Cajas</div><div class="insumo-sub">Exacto: {int(total_botellas):,} tapas ({std_tapa_caja:,} u/caja)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card" style="border-left-color: #fd7e14;"><div class="insumo-title">📦 Rollos Film Paquete</div><div class="insumo-qty">{rollos_film} Rollos</div><div class="insumo-sub">Format: {std_film_pack_rollo:,} packs/rollo</div></div>', unsafe_allow_html=True)

    with ic3:
        st.markdown(f'<div class="insumo-card" style="border-left-color: #20c997;"><div class="insumo-title">📜 Pallets Cartón Corrugado</div><div class="insumo-qty">{pallets_carton} Pallet(s)</div><div class="insumo-sub">({int(total_pallets)} planchas totales)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card" style="border-left-color: #d63384;"><div class="insumo-title">🌀 Film Envolvedora (Stretch)</div><div class="insumo-qty">{rollos_stretcher} Rollos</div><div class="insumo-sub">Format: {std_pallet_stretcher} pallets/rollo</div></div>', unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: BALANCE FINAL DE CIERRE DE LOTE
# ==========================================
with tab2:
    st.subheader("🌊 Balance Total de Producto en Línea (Tanque + Mixer + Tuberías)")

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
    botellas_sistema = (litros_totales_sistema * 1000) / data_format["ml"]
    packs_sistema = botellas_sistema / botellas_por_pack
    pallets_sistema = packs_sistema / packs_por_pallet
    tiempo_sistema_min = (botellas_sistema / bph_real) * 60 if bph_real > 0 else 0

    st.markdown("---")
    st.markdown("## 📊 Producto Final Producible")

    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Litros TOTALES", f"{int(litros_totales_sistema):,} L")
    res2.metric("Botellas Reales", f"{int(botellas_sistema):,} u")
    res3.metric("Packs Reales", f"{int(packs_sistema):,} packs")
    res4.metric("Tiempo Estimado", f"{int(tiempo_sistema_min)} min")

    st.success(f"💡 **Resumen:** Quedan **{pallets_sistema:.1f} Pallets** de producción. Parada de línea proyectada en **{int(tiempo_sistema_min)} minutos**.")

    st.markdown("---")
    st.subheader("📋 Insumos Necesarios (Con Merma)")

    factor_merma = 1.0 + (pct_merma / 100.0)
    botellas_rem_merma = botellas_sistema * factor_merma
    packs_rem_merma = packs_sistema * factor_merma

    cajas_pref_rem = math.ceil(botellas_rem_merma / std_preforma_caja)
    cajas_tapa_rem = math.ceil(botellas_rem_merma / std_tapa_caja)
    rollos_etiq_rem = math.ceil(botellas_rem_merma / std_etiqueta_rollo)
    rollos_film_rem = math.ceil(packs_rem_merma / std_film_pack_rollo)
    pallets_carton_rem = math.ceil(pallets_sistema / std_carton_pallet)
    rollos_stretch_rem = math.ceil(pallets_sistema / std_pallet_stretcher)

    ric1, ric2, ric3 = st.columns(3)
    with ric1:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🧪 Cajas Preforma ({data_format["peso_pref"]}g)</div><div class="insumo-qty">{cajas_pref_rem} Cajas</div><div class="insumo-sub">({int(botellas_rem_merma):,} un. @ {std_preforma_caja:,}/caja)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🏷️ Rollos {data_format["etiq"]}</div><div class="insumo-qty">{rollos_etiq_rem} Rollos</div><div class="insumo-sub">(@ {std_etiqueta_rollo:,}/rollo)</div></div>', unsafe_allow_html=True)

    with ric2:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🔘 Cajas Tapa</div><div class="insumo-qty">{cajas_tapa_rem} Cajas</div><div class="insumo-sub">({int(botellas_rem_merma):,} tapas @ {std_tapa_caja:,}/caja)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">📦 Rollos Film Paquete</div><div class="insumo-qty">{rollos_film_rem} Rollos</div><div class="insumo-sub">(@ {std_film_pack_rollo:,} packs/rollo)</div></div>', unsafe_allow_html=True)

    with ric3:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">📜 Pallet Cartón</div><div class="insumo-qty">{pallets_carton_rem} Pallet(s)</div><div class="insumo-sub">({pallets_sistema:.1f} planchas)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🌀 Film Stretch</div><div class="insumo-qty">{rollos_stretch_rem} Rollos</div><div class="insumo-sub">(@ {std_pallet_stretcher} pallets/rollo)</div></div>', unsafe_allow_html=True)

# ==========================================
# PESTAÑA 3: NOTIFICACIÓN WHATSAPP
# ==========================================
with tab3:
    st.subheader("📲 Generador de Notificación de Turno")
    
    col1, col2 = st.columns(2)
    with col1:
        opcion_saludo = st.selectbox(
            "Saludo inicial",
            ["Buenos días\nFavor notificar:", "Buenas tardes\nFavor notificar:", "Buenas noches\nFavor notificar:", "Favor notificar", "Personalizado"]
        )
        saludo_txt = st.text_input("Escribe el saludo", value="Buenos días\nFavor notificar:") if opcion_saludo == "Personalizado" else opcion_saludo
    with col2:
        turno_sel = st.selectbox("Turno", ["Turno A", "Turno B", "Turno C"])

    col3, col4 = st.columns(2)
    with col3:
        linea_sel = st.text_input("Línea", value="Línea 2")
    with col4:
        op_num = st.text_input("Orden de Producción (OP)", value="6600225198")

    col5, col6 = st.columns(2)
    with col5:
        sabor_sel = st.selectbox("Producto / Sabor", LISTA_SABORES)
        sabor_txt = st.text_input("Escribe el sabor", value="Pap") if sabor_sel == "Otro (Escribir manualmente)" else sabor_sel
    with col6:
        fmt_txt = f"{data_format['ml']}ml" if data_format['ml'] < 1000 else f"{data_format['ml']/1000}L"
        st.text_input("Formato Detectado Matriz", value=fmt_txt, disabled=True)

    prod_completo = f"{sabor_txt} {fmt_txt}".strip()

    col7, col8 = st.columns(2)
    with col7:
        cajas_cant = st.number_input(
            "Cajas / Packs Producidos", 
            value=st.session_state.packs_calculados if st.session_state.packs_calculados > 0 else 15724, 
            step=100
        )
        cajas_formateadas = f"{int(cajas_cant):,}".replace(",", ".")
    with col8:
        fecha_notif = st.text_input("Fecha", value=datetime.now().strftime("%d/%m/%Y"))

    mensaje_final = f"{saludo_txt}\n{turno_sel} - {linea_sel}\n{prod_completo}\nOP: {op_num}\nCajas: {cajas_formateadas}\n{fecha_notif}"

    st.markdown("### 📄 Mensaje Generado:")
    st.markdown(f'<div class="whatsapp-box">{mensaje_final}</div>', unsafe_allow_html=True)

    mensaje_encoded = urllib.parse.quote(mensaje_final)
    whatsapp_url = f"https://api.whatsapp.com/send?text={mensaje_encoded}"

    st.markdown(f'''
        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
            <button style="
                background-color: #25d366;
                color: white;
                border: none;
                padding: 14px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                cursor: pointer;
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                📲 Enviar por WhatsApp
            </button>
        </a>
    ''', unsafe_allow_html=True)

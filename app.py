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

# --- ESTILOS CSS PARA CELULAR Y MODO OSCURO/CLARO ---
st.markdown("""
    <style>
    /* Forzar fondo blanco y texto oscuro global */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #ffffff !important;
        color: #212529 !important;
    }
    
    label, .stMarkdown, p, span, h1, h2, h3, h4, h5, h6 {
        color: #212529 !important;
    }

    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #f8f9fa !important;
        color: #212529 !important;
        border: 1px solid #ced4da !important;
    }
    input {
        color: #212529 !important;
    }

    /* Tarjetas de métricas */
    .metric-card {
        background-color: #ffffff !important;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #dee2e6;
        border-left: 5px solid #0d6efd !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #0d6efd !important;
    }
    .metric-label {
        font-size: 12px;
        color: #495057 !important;
        text-transform: uppercase;
        font-weight: 600;
    }

    /* Tarjetas de Insumos */
    .insumo-card {
        background-color: #f1f3f5 !important;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #198754 !important;
        margin-bottom: 10px;
    }
    .insumo-title {
        font-weight: bold;
        color: #198754 !important;
        font-size: 14px;
    }
    .insumo-qty {
        font-size: 20px;
        font-weight: bold;
        color: #212529 !important;
    }
    .insumo-sub {
        color: #6c757d !important;
        font-size: 12px;
    }

    /* Caja de mensaje WhatsApp estilo Chat */
    .whatsapp-box {
        background-color: #e7f7ee !important;
        border: 1px solid #25d366 !important;
        border-left: 6px solid #25d366 !important;
        padding: 16px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 15px;
        color: #111b21 !important;
        white-space: pre-wrap;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DICCIONARIO OFICIAL DE PRODUCTOS ---
PRODUCTOS_PRESET = {
    "Bilz Regular": {"factor": 7.125, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Bilz Zero": {"factor": 7.125, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Pap Regular": {"factor": 7.125, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Pap Zero": {"factor": 7.125, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Kem Regular": {"factor": 7.125, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Kem Zero": {"factor": 7.125, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Kem Piña": {"factor": 7.125, "ml": 350, "bph": 60000, "pref_caja": 15000},
    "Pepsi Regular": {"factor": 6.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Pepsi Zero": {"factor": 6.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "7Up Regular": {"factor": 6.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "7Up Zero": {"factor": 6.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Limón Soda": {"factor": 5.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Limón Soda Zero": {"factor": 5.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Crush Naranja": {"factor": 5.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Crush Zero": {"factor": 5.000, "ml": 600, "bph": 60000, "pref_caja": 15000},
    "Rockstar Original": {"factor": 4.000, "ml": 500, "bph": 60000, "pref_caja": 15000},
    "Rockstar Mango": {"factor": 4.000, "ml": 500, "bph": 60000, "pref_caja": 15000},
    "Watts Durazno reducido": {"factor": 7.125, "ml": 1500, "bph": 38000, "pref_caja": 10000},
    "Más Citrus C/G": {"factor": 7.125, "ml": 2000, "bph": 38000, "pref_caja": 10000},
    "Más Uva": {"factor": 7.125, "ml": 1600, "bph": 38000, "pref_caja": 10000},
    "Limonada Frambuesa": {"factor": 7.125, "ml": 2000, "bph": 38000, "pref_caja": 10000},
    "POP Huevo": {"factor": 7.125, "ml": 500, "bph": 42000, "pref_caja": 15000},
    "Personalizado": {"factor": 7.125, "ml": 600, "bph": 60000, "pref_caja": 15000}
}

# --- LISTAS SEPARADAS PARA EL DESPLEGABLE DE NOTIFICACIÓN ---
LISTA_SABORES = [
    "Bilz",
    "Bilz Zero",
    "Pap",
    "Pap Zero",
    "Kem",
    "Kem Zero",
    "Kem piña",
    "Pepsi Reducida",
    "Pepsi Zero",
    "7Up",
    "7Up Zero",
    "Limón Soda",
    "Limón Soda Zero",
    "Crush",
    "Crush Zero",
    "Rockstar Original",
    "Rockstar Sandía",
    "Rockstar Mango",
    "POP Huevo",
    "Otro (Escribir manualmente)"
]

LISTA_FORMATOS = [
    "600ml",
    "500ml",
    "350ml",
    "1,5",
    "1.5 lts",
    "1.6 lts",
    "2 lts",
    "1.25 L",
    "1.75 L Cisne",
    "Otro (Escribir manualmente)"
]

# --- ENCABEZADO ---
st.title("⚡ Control de Producción e Insumos - Línea 2 CCU")
st.caption("Calculadora en tiempo real para Ergobloc L, Mixer y Pedido a Bodega")

# --- BARRA LATERAL: SELECCIÓN Y CONFIGURACIÓN DE INSUMOS ---
with st.sidebar:
    st.header("⚙️ Configuración del Turno")
    prod_nombre = st.selectbox("Producto a Producir", list(PRODUCTOS_PRESET.keys()))
    preset = PRODUCTOS_PRESET[prod_nombre]

    st.subheader("Parámetros del Producto")
    vol_ml = st.number_input("Volumen Botella (ml)", value=preset["ml"], step=50)
    factor_mezcla = st.number_input("Factor de Mezcla (Jarabe → Bebida)", value=preset["factor"], step=0.1)
    bph_nominal = st.number_input("Velocidad Nominal Ergobloc (BPH)", value=preset["bph"], step=1000)
    
    st.subheader("Eficiencia de Línea")
    oee = st.slider("OEE / Eficiencia Real (%)", min_value=50, max_value=100, value=85)
    bph_real = bph_nominal * (oee / 100.0)
    st.info(f"Velocidad Real: **{int(bph_real):,} BPH**")

    st.subheader("📦 Capacidades Estándar de Bodega")
    std_preforma_caja = st.number_input("Preformas x Caja", value=preset["pref_caja"], step=1000)
    std_tapa_caja = st.number_input("Tapas x Caja", value=5000, step=500)
    std_etiqueta_rollo = st.number_input("Etiquetas x Rollo", value=10000, step=1000)
    std_film_pack_rollo = st.number_input("Packs x Rollo Film Paquete", value=2900, step=100)
    std_carton_pallet = st.number_input("Planchas Cartón x Pallet", value=500, step=50)
    std_pallet_stretcher = st.number_input("Pallets x Rollo Stretcher", value=35, step=5)

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs([
    "🧪 1. Programación por Jarabe Disponible", 
    "🌊 2. Balance Final de Cierre de Lote",
    "📲 3. Notificación WhatsApp"
])

packs_totales_calculados = 0

# ==========================================
# PESTAÑA 1: PROGRAMACIÓN DESDE JARABE
# ==========================================
with tab1:
    st.subheader("Planificación de Lote según Jarabe Preparado")
    
    col1, col2 = st.columns(2)
    with col1:
        jarabe_disponible = st.number_input("Jarabe Disponible en Tanque (L)", value=7000, step=500)
        botellas_por_pack = st.number_input("Botellas por Pack (Ej. 6 para 3x2)", value=6, step=1, key="pack_t1")
        packs_por_pallet = st.number_input("Packs por Pallet", value=100, step=10, key="pallet_t1")
    
    with col2:
        hora_inicio = st.time_input("Hora de Inicio / Actual", value=datetime.now().time())

    # Cálculos Principales
    litros_bebida_total = jarabe_disponible * factor_mezcla
    total_botellas = (litros_bebida_total * 1000) / vol_ml
    total_packs = total_botellas / botellas_por_pack
    packs_totales_calculados = int(total_packs)
    total_pallets = total_packs / packs_por_pallet
    
    horas_prod = total_botellas / bph_real if bph_real > 0 else 0
    tiempo_fin = datetime.combine(datetime.today(), hora_inicio) + timedelta(hours=horas_prod)

    # Métricas Principales
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Bebida Final Total</div><div class="metric-value">{int(litros_bebida_total):,} L</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Pallets Totales</div><div class="metric-value">{total_pallets:.1f}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Packs Totales</div><div class="metric-value">{int(total_packs):,}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Hora Término Est.</div><div class="metric-value">{tiempo_fin.strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Insumos y Materiales a Pedir a Bodega")
    st.caption("Calculado con un 2% adicional para mermas de arranque y pruebas de línea.")

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
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🧪 Cajas de Preforma</div><div class="insumo-qty">{cajas_preforma} Cajas</div><div class="insumo-sub">({int(botellas_con_merma):,} un. @ {std_preforma_caja:,}/caja)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🏷️ Rollos de Etiqueta</div><div class="insumo-qty">{rollos_etiqueta} Rollos</div><div class="insumo-sub">(BOPP / Body / Sleeve @ {std_etiqueta_rollo:,}/rollo)</div></div>', unsafe_allow_html=True)

    with ic2:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🔘 Cajas de Tapa</div><div class="insumo-qty">{cajas_tapa} Cajas</div><div class="insumo-sub">({int(botellas_con_merma):,} tapas @ 5,000/caja)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">📦 Rollos Film Paquete</div><div class="insumo-qty">{rollos_film} Rollos</div><div class="insumo-sub">(Empaquetadora Variopac @ 2,900 packs)</div></div>', unsafe_allow_html=True)

    with ic3:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">📜 Pallet Cartón Corrugado</div><div class="insumo-qty">{pallets_carton} Pallet(s)</div><div class="insumo-sub">({int(total_pallets)} planchas)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🌀 Film Envolvedora (Stretch)</div><div class="insumo-qty">{rollos_stretcher} Rollos</div><div class="insumo-sub">(Envolvedora Stretch W.)</div></div>', unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: BALANCE FINAL DE CIERRE DE LOTE
# ==========================================
with tab2:
    st.subheader("🌊 Balance Total de Producto en Línea (Tanque + Mixer + Tuberías)")
    st.caption("Usa esta pestaña cuando te quede poco jarabe para saber exactamente cuántos pallets finales sacarás y qué insumos necesitas para terminar.")

    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("### 🛢️ 1. Tanque Elaboración")
        jarabe_tanque = st.number_input("Jarabe Restante en Tanque (L)", value=1500, step=100, key="j_t2")
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

    st.markdown("---")
    st.subheader("📋 Insumos Necesarios para Terminar el Lote Actual")

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
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🧪 Cajas de Preforma</div><div class="insumo-qty">{cajas_pref_rem} Cajas</div><div class="insumo-sub">({int(botellas_rem_merma):,} un. @ {std_preforma_caja:,}/caja)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🏷️ Rollos de Etiqueta</div><div class="insumo-qty">{rollos_etiq_rem} Rollos</div><div class="insumo-sub">(BOPP / Body / Sleeve @ {std_etiqueta_rollo:,}/rollo)</div></div>', unsafe_allow_html=True)

    with ric2:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🔘 Cajas de Tapa</div><div class="insumo-qty">{cajas_tapa_rem} Cajas</div><div class="insumo-sub">({int(botellas_rem_merma):,} tapas @ 5,000/caja)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">📦 Rollos Film Paquete</div><div class="insumo-qty">{rollos_film_rem} Rollos</div><div class="insumo-sub">(Empaquetadora Variopac @ 2,900 packs)</div></div>', unsafe_allow_html=True)

    with ric3:
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">📜 Pallet Cartón Corrugado</div><div class="insumo-qty">{pallets_carton_rem} Pallet(s)</div><div class="insumo-sub">({pallets_sistema:.1f} planchas)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insumo-card"><div class="insumo-title">🌀 Film Envolvedora (Stretch)</div><div class="insumo-qty">{rollos_stretch_rem} Rollos</div><div class="insumo-sub">(Envolvedora Stretch W.)</div></div>', unsafe_allow_html=True)

# ==========================================
# PESTAÑA 3: NOTIFICACIÓN RÁPIDA DE WHATSAPP
# ==========================================
with tab3:
    st.subheader("📲 Generador de Notificación de Turno")
    st.caption("Completa los datos para generar el mensaje estandarizado.")

    # Fila 1: Saludo y Turno
    col1, col2 = st.columns(2)
    with col1:
        opcion_saludo = st.selectbox(
            "Saludo inicial",
            [
                "Buenos días\nFavor notificar:",
                "Buenas tardes\nFavor notificar:",
                "Buenas noches\nFavor notificar:",
            ]
        )
        if opcion_saludo == "Personalizado":
            saludo_txt = st.text_input("Escribe el saludo personalizado", value="Buenos días")
        else:
            saludo_txt = opcion_saludo

    with col2:
        turno_sel = st.selectbox("Turno", ["Turno A", "Turno B", "Turno C"])

    # Fila 2: Línea y Orden de Producción (OP) [Cambio 1: OP ahora está aquí]
    col3, col4 = st.columns(2)
    with col3:
        linea_sel = st.text_input("Línea", value="línea 2")
    with col4:
        op_num = st.text_input("Orden de Producción (OP)", value="6600225198")

    # Fila 3: Formato y Producto / Sabor [Cambio 2: Formato primero, luego Producto]
    col5, col6 = st.columns(2)
    with col5:
        fmt_sel = st.selectbox("Formato", LISTA_FORMATOS)
        if fmt_sel == "Otro (Escribir manualmente)":
            fmt_txt = st.text_input("Escribe el formato", value="600ml")
        else:
            fmt_txt = fmt_sel

    with col6:
        sabor_sel = st.selectbox("Producto / Marca / Sabor", LISTA_SABORES)
        if sabor_sel == "Otro (Escribir manualmente)":
            sabor_txt = st.text_input("Escribe el sabor", value="Pap")
        else:
            sabor_txt = sabor_sel

    # Armar combinación directa de Producto + Formato para el mensaje
    prod_completo = f"{sabor_txt} {fmt_txt}".strip()

    # Fila 4: Cajas Producidas y Fecha
    col7, col8 = st.columns(2)
    with col7:
        cajas_cant = st.number_input(
            "Cajas / Packs Producidos", 
            value=packs_totales_calculados if packs_totales_calculados > 0 else 15724, 
            step=100
        )
        cajas_formateadas = f"{int(cajas_cant):,}".replace(",", ".")

    with col8:
        fecha_notif = st.text_input("Fecha", value=datetime.now().strftime("%d/%m/%Y"))

    # Construcción del mensaje final
    if "Buenas tardes" in saludo_txt:
        mensaje_final = f"{saludo_txt} {turno_sel}, {linea_sel}\n{prod_completo}\nOP: {op_num}\nCajas: {cajas_formateadas}\n{fecha_notif}"
    else:
        mensaje_final = f"{saludo_txt}\n{turno_sel} - {linea_sel}\n{prod_completo}\nOP: {op_num}\nCajas: {cajas_formateadas}\n{fecha_notif}"

    # Mensaje generado y botón de WhatsApp integrados abajo
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

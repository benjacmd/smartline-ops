import streamlit as st
import math
from datetime import datetime, timedelta
import pytz

# Configuración de zona horaria de Chile
CHILE_TZ = pytz.timezone('America/Santiago')

# Configuración de la página para celulares
st.set_page_config(
    page_title="SmartLine Ops",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 SmartLine Ops")
st.caption("Calculadora de Producción, Insumos y Reposición de Línea")

st.divider()

# --- DICCIONARIO DE PRODUCTOS PRECONFIGURADOS ---
PRODUCTOS_PRESET = {
    "Personalizado (Manual)": {"factor": 7.125, "ml": 600, "bph": 60000},
    "Bilz 600 ml": {"factor": 7.125, "ml": 600, "bph": 60000},
    "Pap 600 ml": {"factor": 7.125, "ml": 600, "bph": 60000},

}

# --- SECCIÓN 1: SELECCIÓN RÁPIDA DE PRODUCTO ---
st.subheader("1. Selección de Producto")
producto_seleccionado = st.selectbox("Elige el producto para cargar valores automáticos:", list(PRODUCTOS_PRESET.keys()))

preset_actual = PRODUCTOS_PRESET[producto_seleccionado]

st.subheader("2. Parámetros de Mezcla y Línea")

col1, col2 = st.columns(2)

with col1:
    jarabe = st.number_input("Litros de Jarabe (L)", value=16000, step=500)
    factor = st.number_input("Factor de Mezcla (Mixer)", value=preset_actual["factor"], format="%.3f")
    merma_pct = st.number_input("% Merma Operativa (Seguridad)", value=1.5, step=0.5, format="%.1f")

with col2:
    formato_ml = st.number_input("Tamaño Botella (ml)", value=preset_actual["ml"], step=50)
    velocidad_bph = st.number_input("Velocidad Línea (BPH)", value=preset_actual["bph"], step=1000)

st.subheader("3. Capacidades y Stock Actual en Línea")
with st.expander("⚙️ Configurar capacidades de cajas/rollos y stock físico", expanded=False):
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.markdown("**Capacidades por Empaque:**")
        cap_preformas = st.number_input("Preformas por caja", value=14000, step=500)
        cap_tapas = st.number_input("Tapas por caja", value=5000, step=500)
        duracion_film_min = st.number_input("Duración 1 Rollo Film (min)", value=18, step=1)
    
    with col_e2:
        st.markdown("**Stock Actual al Pie de Máquina:**")
        stock_actual_film = st.number_input("Rollos de Film en piso", value=8, step=1)
        stock_actual_tapas = st.number_input("Cajas de Tapas disponibles", value=5, step=1)
        stock_actual_preformas = st.number_input("Cajas de Preformas disponibles", value=3, step=1)

    st.markdown("---")
    st.markdown("**Parámetros de Palletizado:**")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        botellas_por_pack = st.number_input("Bot./Pack", value=12, step=1)
    with col_p2:
        packs_por_pallet = st.number_input("Packs/Pallet", value=132, step=1)
    with col_p3:
        camadas_por_pallet = st.number_input("Camadas/Pallet", value=6, step=1)

# --- SECCIÓN 2: CÁLCULOS MATEMÁTICOS ---
litros_bebida = jarabe * factor
litros_envase = formato_ml / 1000.0
botellas_teoricas = litros_bebida / litros_envase if litros_envase > 0 else 1

# Factor de merma aplicado a insumos
factor_merma = 1 + (merma_pct / 100.0)
botellas_con_merma = botellas_teoricas * factor_merma

# Tiempo de producción
horas_prod = botellas_teoricas / velocidad_bph if velocidad_bph > 0 else 1
minutos_totales = horas_prod * 60

# Cálculos de Insumos Totales (con merma)
cajas_preformas_totales = math.ceil(botellas_con_merma / cap_preformas) if cap_preformas > 0 else 0
cajas_tapas_totales = math.ceil(botellas_con_merma / cap_tapas) if cap_tapas > 0 else 0
rollos_film_totales = math.ceil(minutos_totales / duracion_film_min) if duracion_film_min > 0 else 0

# Faltantes por pedir
faltan_film = max(0, rollos_film_totales - stock_actual_film)
faltan_tapas = max(0, cajas_tapas_totales - stock_actual_tapas)
faltan_preformas = max(0, cajas_preformas_totales - stock_actual_preformas)

# Cálculos de Pallets
total_packs = math.ceil(botellas_teoricas / botellas_por_pack) if botellas_por_pack > 0 else 0
total_pallets = math.ceil(total_packs / packs_por_pallet) if packs_por_pallet > 0 else 0
packs_por_camada = packs_por_pallet / camadas_por_pallet if camadas_por_pallet > 0 else 0
separadores_carton = total_pallets * camadas_por_pallet

# --- SECCIÓN 3: RESULTADOS ---
st.divider()
st.header("📊 Hoja de Ruta Operativa")

m1, m2, m3 = st.columns(3)
m1.metric("Bebida Total", f"{litros_bebida:,.0f} L")
m2.metric("Botellas Finales", f"{int(botellas_teoricas):,} unid.")
m3.metric("Tiempo Total", f"{int(horas_prod)}h {int(minutos_totales % 60)}m")

st.subheader("📦 Control de Insumos y Reposición a Bodega")

col_i1, col_i2, col_i3 = st.columns(3)

with col_i1:
    st.markdown("#### 📦 Preformas")
    st.metric("Total Requerido", f"{cajas_preformas_totales} cajas")
    if faltan_preformas > 0:
        st.error(f"⚠️ Faltan pedir: **{faltan_preformas} cajas**")
    else:
        st.success("✅ Stock suficiente")

with col_i2:
    st.markdown("#### 🥤 Tapas")
    st.metric("Total Requerido", f"{cajas_tapas_totales} cajas")
    if faltan_tapas > 0:
        st.error(f"⚠️ Faltan pedir: **{faltan_tapas} cajas**")
    else:
        st.success("✅ Stock suficiente")

with col_i3:
    st.markdown("#### 🎞️ Film Vario")
    st.metric("Total Requerido", f"{rollos_film_totales} rollos")
    if faltan_film > 0:
        st.error(f"⚠️ Faltan pedir: **{faltan_film} rollos**")
    else:
        st.success("✅ Stock suficiente")

st.subheader("🏗️ Fin de Línea y Palletizado")
col_p1, col_p2, col_p3 = st.columns(3)
col_p1.metric("📦 Packs Totales", f"{total_packs:,} packs")
col_p2.metric("🪵 Pallets Terminados", f"{total_pallets} pallets")
col_p3.metric("🏷️ LPNs Requeridos", f"{total_pallets} etiquetas")

st.markdown(f"""
> **Estructura del Pallet:** {packs_por_camada:.0f} packs por camada | {camadas_por_pallet} camadas | **{separadores_carton}** separadores de cartón.
""")

st.divider()

# --- SECCIÓN 4: RECOMENDACIÓN PROACTIVA CON HORA DE CHILE ---
st.subheader("💡 Alertas de Turno (Hora Chile)")

# Hora actual real de Chile
ahora_chile = datetime.now(CHILE_TZ)
hora_fin = ahora_chile + timedelta(minutes=minutos_totales)
hora_alerta_revision = hora_fin - timedelta(minutes=60)

st.info(f"""
* 🕐 **Hora actual en Chile:** {ahora_chile.strftime('%H:%M')} hrs.
* 🏁 **Fin estimado de corrida:** {hora_fin.strftime('%H:%M')} hrs.
* ⏰ **Conteo Final de Tolva:** A las **{hora_alerta_revision.strftime('%H:%M')} hrs** (1 hora antes), verifica remanente para frenar la carga antes del cambio de producto.
""")

# --- SECCIÓN 5: REPORTE PARA WHATSAPP ---
st.subheader("📱 Reporte Rápido de Línea")

reporte_text = f"""📊 *REPORTE DE LÍNEA - {producto_seleccionado}*
🕐 Inicio/Actual: {ahora_chile.strftime('%H:%M')} hrs | Fin Est.: {hora_fin.strftime('%H:%M')} hrs
🥤 Bebida Total: {litros_bebida:,.0f} L ({int(botellas_teoricas):,} botellas)
🪵 Pallets Totales: {total_pallets} pallets ({total_packs:,} packs)

📦 *PEDIDOS A BODEGA:*
- Preformas: {'✅ OK' if faltan_preformas == 0 else f'Faltan {faltan_preformas} cajas'}
- Tapas: {'✅ OK' if faltan_tapas == 0 else f'Faltan {faltan_tapas} cajas'}
- Film Vario: {'✅ OK' if faltan_film == 0 else f'Faltan {faltan_film} rollos'}
⏰ *Hora límite conteo tolva:* {hora_alerta_revision.strftime('%H:%M')} hrs"""

st.code(reporte_text, language="text")
st.caption("Copiar y pegar este bloque directo en el grupo de WhatsApp de la línea.")

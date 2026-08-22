import streamlit as st
import math
from datetime import datetime, timedelta

# Configuración de la página para celulares
st.set_page_config(
    page_title="SmartLine Ops",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 SmartLine Ops")
st.caption("Calculadora de Producción, Insumos y Palletizado")

st.divider()

# --- SECCIÓN 1: ENTRADA DE DATOS ---
st.subheader("1. Parámetros de Mezcla y Línea")

col1, col2 = st.columns(2)

with col1:
    jarabe = st.number_input("Litros de Jarabe (L)", value=16000, step=500)
    factor = st.number_input("Factor de Mezcla (Mixer)", value=7.125, format="%.3f")

with col2:
    formato_ml = st.selectbox("Tamaño Botella (ml)", [600, 350, 500, 1500, 2000], index=0)
    velocidad_bph = st.number_input("Velocidad Línea (BPH)", value=60000, step=1000)

st.subheader("2. Capacidades de Empaque de Insumos")
with st.expander("⚙️ Ajustar capacidades de insumos y pallets", expanded=True):
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        cap_preformas = st.number_input("Preformas por caja", value=14000, step=500)
        cap_tapas = st.number_input("Tapas por caja", value=5000, step=500)
        duracion_film_min = st.number_input("Duración Rollo Film Vario (min)", value=18, step=1)
    
    with col_e2:
        botellas_por_pack = st.number_input("Botellas por Pack", value=12, step=1)
        packs_por_pallet = st.number_input("Packs por Pallet", value=132, step=1)
        camadas_por_pallet = st.number_input("Camadas por Pallet", value=6, step=1)

# --- SECCIÓN 2: CÁLCULOS MATEMÁTICOS ---
litros_bebida = jarabe * factor
litros_envase = formato_ml / 1000.0
botellas_teoricas = litros_bebida / litros_envase

# Tiempo de producción
horas_prod = botellas_teoricas / velocidad_bph
minutos_totales = horas_prod * 60

# Cálculos de Insumos Primarios
cajas_preformas = math.ceil(botellas_teoricas / cap_preformas)
cajas_tapas = math.ceil(botellas_teoricas / cap_tapas)
rollos_film = math.ceil(minutos_totales / duracion_film_min)

# Cálculos de Palletizado y Empaque Secundario
total_packs = math.ceil(botellas_teoricas / botellas_por_pack)
total_pallets = math.ceil(total_packs / packs_por_pallet)
packs_por_camada = packs_por_pallet / camadas_por_pallet if camadas_por_pallet > 0 else 0
separadores_carton = total_pallets * camadas_por_pallet

# --- SECCIÓN 3: RESULTADOS ---
st.divider()
st.header("📊 Hoja de Ruta Operativa")

# Métricas principales
m1, m2, m3 = st.columns(3)
m1.metric("Bebida Total", f"{litros_bebida:,.0f} L")
m2.metric("Botellas Finales", f"{int(botellas_teoricas):,} unid.")
m3.metric("Tiempo Total", f"{int(horas_prod)}h {int(minutos_totales % 60)}m")

st.subheader("📦 Insumos Directos de Línea")
col_a, col_b, col_c = st.columns(3)
col_a.metric("📦 Preformas", f"{cajas_preformas} cajas")
col_b.metric("🥤 Tapas", f"{cajas_tapas} cajas")
col_c.metric("🎞️ Film Vario", f"{rollos_film} rollos")

st.subheader("🏗️ Fin de Línea: Packs y Palletizado")
col_p1, col_p2, col_p3 = st.columns(3)
col_p1.metric("📦 Packs Totales", f"{total_packs:,} packs")
col_p2.metric("🪵 Pallets Totales", f"{total_pallets} pallets", help=f"1 Pallet = {packs_por_pallet} packs")
col_p3.metric("🏷️ LPNs Requeridos", f"{total_pallets} etiquetas")

# Detalle de la Estructura del Pallet
st.markdown(f"""
> **Estructura por Pallet Completo:**
> * **{packs_por_camada:.0f} Packs** por camada.
> * **{camadas_por_pallet} Camadas** de altura.
> * **Separadores de cartón requeridos:** {separadores_carton} láminas para la tirada.
""")

st.divider()

# --- SECCIÓN 4: RECOMENDACIÓN PROACTIVA ---
st.subheader("💡 Control Proactivo de Turno")

ahora = datetime.now()
hora_fin = ahora + timedelta(minutes=minutos_totales)
hora_alerta_revision = hora_fin - timedelta(minutes=60)

st.info(f"""
* **Inicio simulado (ahora):** {ahora.strftime('%H:%M')} hrs.
* **Fin estimado de corrida:** {hora_fin.strftime('%H:%M')} hrs.
* **⏰ Alerta de Conteo Final:** A las **{hora_alerta_revision.strftime('%H:%M')} hrs** (1 hora antes del término), verifica el stock de tapas/preformas para no sobrecargar la tolva y cuenta los LPNs restantes.
""")

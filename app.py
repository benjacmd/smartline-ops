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
st.caption("Calculadora de Producción e Insumos en Línea")

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
with st.expander("⚙️ Ajustar capacidades de cajas/rollos", expanded=False):
    cap_preformas = st.number_input("Preformas por caja", value=14000, step=500)
    cap_tapas = st.number_input("Tapas por caja", value=5000, step=500)
    duracion_film_min = st.number_input("Duración de 1 Rollo Film Vario (minutos)", value=18, step=1)

# --- SECCIÓN 2: CÁLCULOS MATEMÁTICOS ---
litros_bebida = jarabe * factor
litros_envase = formato_ml / 1000.0
botellas_teoricas = litros_bebida / litros_envase

# Tiempo de producción
horas_prod = botellas_teoricas / velocidad_bph
minutos_totales = horas_prod * 60

# Cálculo de Insumos
cajas_preformas = math.ceil(botellas_teoricas / cap_preformas)
cajas_tapas = math.ceil(botellas_teoricas / cap_tapas)
rollos_film = math.ceil(minutos_totales / duracion_film_min)

# --- SECCIÓN 3: RESULTADOS ---
st.divider()
st.header("📊 Hoja de Ruta Operativa")

# Metricas principales
m1, m2, m3 = st.columns(3)
m1.metric("Bebida Total", f"{litros_bebida:,.0f} L")
m2.metric("Botellas Finales", f"{int(botellas_teoricas):,} unid.")
m3.metric("Tiempo Total", f"{int(horas_prod)}h {int(minutos_totales % 60)}m")

st.subheader("📦 Matriz de Insumos Requeridos")

col_a, col_b, col_c = st.columns(3)
col_a.metric("📦 Preformas", f"{cajas_preformas} cajas", help=f"{cap_preformas:,} unid/caja")
col_b.metric("🥤 Tapas", f"{cajas_tapas} cajas", help=f"{cap_tapas:,} unid/caja")
col_c.metric("🎞️ Film Vario", f"{rollos_film} rollos", help=f"1 rollo c/{duracion_film_min} min")

st.divider()

# --- SECCIÓN 4: RECOMENDACIÓN PROACTIVA DE TURNO ---
st.subheader("💡 Control Proactivo de Turno")

ahora = datetime.now()
hora_fin = ahora + timedelta(minutes=minutos_totales)
hora_alerta_revisión = hora_fin - timedelta(minutes=60)

st.info(f"""
* **Inicio simulado (ahora):** {ahora.strftime('%H:%M')} hrs.
* **Fin estimado de corrida:** {hora_fin.strftime('%H:%M')} hrs.
* **⏰ Alerta de Conteo Final:** A las **{hora_alerta_revisión.strftime('%H:%M')} hrs** (1 hora antes del término), verifica el stock remanente en tolva para evitar sobrecargar tapas o preformas antes del cambio de sabor.
""")

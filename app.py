import streamlit as st
from datetime import datetime, timedelta
import math
import urllib.parse

st.set_page_config(page_title="Control Línea 2 - CCU", layout="wide")

# --- BASE DE DATOS CCU LÍNEA 2 ---
MATRIZ_CCU = {
    "500 ml Rockstar": {"ml": 500, "bph": 60000, "pref_caja": 15000, "pack": 6},
    "500 ml POP (Huevo)": {"ml": 500, "bph": 42000, "pref_caja": 15000, "pack": 6},
    "600 ml BGP / AXL / Ripples": {"ml": 600, "bph": 60000, "pref_caja": 15000, "pack": 6},
    "600 ml B&P": {"ml": 600, "bph": 60000, "pref_caja": 15000, "pack": 6},
    "1,5 L Carolina / Genérica / Crush": {"ml": 1500, "bph": 38000, "pref_caja": 8000, "pack": 6},
    "1,5 L Carolina Sleeve": {"ml": 1500, "bph": 36000, "pref_caja": 8000, "pack": 6},
    "1,75 L Cisne": {"ml": 1750, "bph": 34000, "pref_caja": 6000, "pack": 6}
}

SABORES = ["Bilz", "Bilz Zero", "Pap", "Pap Zero", "Kem", "Kem Zero", "Pepsi", "Pepsi Zero", "7Up", "Limón Soda", "Crush", "Rockstar", "POP Huevo"]

st.title("⚡ Control Línea 2 - CCU")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    envase_sel = st.selectbox("Envase", list(MATRIZ_CCU.keys()))
    fmt = MATRIZ_CCU[envase_sel]
    
    factor_mezcla = st.number_input("Factor Mezcla", value=7.125, step=0.1)
    bph_nominal = st.number_input("Velocidad Ergobloc (BPH)", value=fmt["bph"], step=1000)
    oee = st.slider("OEE / Eficiencia (%)", 50, 100, 100)
    bph_real = bph_nominal * (oee / 100.0)

# --- PANEL PRINCIPAL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧪 Programación por Jarabe")
    jarabe = st.number_input("Jarabe Disponible (L)", value=7000, step=500)
    bot_pack = st.selectbox("Botellas por Pack", [6, 12], index=0 if fmt["pack"]==6 else 1)
    pack_pallet = st.number_input("Packs por Pallet", value=100 if fmt['ml']<=600 else 60, step=5)

    # Cálculos rápidos
    litros_total = jarabe * factor_mezcla
    botellas = (litros_total * 1000) / fmt["ml"]
    packs = botellas / bot_pack
    pallets = packs / pack_pallet
    horas = (botellas / bph_real) if bph_real > 0 else 0
    fin_est = datetime.now() + timedelta(hours=horas)

with col2:
    st.subheader("📊 Resultados Proyectados")
    c_a, c_b = st.columns(2)
    c_a.metric("Bebida Total", f"{int(litros_total):,} L")
    c_b.metric("Botellas", f"{int(botellas):,} u")
    c_a.metric("Packs Reales", f"{int(packs):,} pk")
    c_b.metric("Pallets Total", f"{pallets:.1f}")
    
    st.success(f"⏱️ **Tiempo estimado:** {int(horas)}h {int((horas%1)*60)}m | **Término:** {fin_est.strftime('%H:%M hrs')}")

st.divider()

# --- PEDIDO A BODEGA ---
st.subheader("📦 Pedido a Bodega (Insumos Estándar)")
b1, b2, b3, b4 = st.columns(4)
b1.metric("Preformas", f"{math.ceil(botellas / fmt['pref_caja'])} Cajas", f"{fmt['pref_caja']:,} u/caja")
b2.metric("Tapas", f"{math.ceil(botellas / 5000)} Cajas", "5.000 u/caja")
b3.metric("Etiquetas", f"{math.ceil(botellas / 10000)} Rollos", "10.000 u/rollo")
b4.metric("Film Paquete", f"{math.ceil(packs / 2700)} Rollos", "2.700 pk/rollo")

st.divider()

# --- WHATSAPP ---
st.subheader("📲 Notificación de Turno")
wc1, wc2, wc3, wc4 = st.columns(4)
turno = wc1.selectbox("Turno", ["Turno A", "Turno B", "Turno C"])
sabor = wc2.selectbox("Sabor", SABORES)
op = wc3.text_input("OP", value="6600225198")
packs_real = wc4.number_input("Packs Producidos", value=int(packs), step=100)

msg = f"Favor notificar:\n{turno} - Línea 2\n{sabor} {fmt['ml']}ml\nOP: {op}\nCajas: {packs_real:,}\n{datetime.now().strftime('%d/%m/%Y')}".replace(",", ".")

st.code(msg, language="text")

url_wa = f"https://api.whatsapp.com/send?text={urllib.parse.quote(msg)}"
st.markdown(f'<a href="{url_wa}" target="_blank"><button style="background:#25d366;color:white;border:none;padding:10px 20px;border-radius:5px;font-weight:bold;cursor:pointer;width:100%;">📲 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)

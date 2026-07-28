import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Control Marketplace", page_icon="📊", layout="centered")

st.title("Control de Llamadas y Pagos")
st.caption("Marketplace")

# --- Configuración y Tarifa ---
st.header("Configuración y Tarifa")
col_mes, col_sem = st.columns(2)

with col_mes:
    mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=6)

with col_sem:
    semana = st.selectbox("Semana:", ["Semana 1", "Semana 2", "Semana 3", "Semana 4"])

precio_llamada = st.number_input("Precio/Llamada ($):", value=1.20, step=0.10, format="%.2f")

st.divider()

# --- Registro Diario ---
st.header("Registro Diario")

dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

total_mensajes = 0
total_llamadas = 0

for dia in dias:
    st.subheader(dia)
    c1, c2 = st.columns(2)
    with c1:
        msg = st.number_input(f"Mensajes ({dia})", min_value=0, value=63 if dia == "Lunes" else 0, key=f"msg_{dia}")
    with c2:
        llm = st.number_input(f"Llamadas Válidas ({dia})", min_value=0, value=7 if dia == "Lunes" else 0, key=f"llm_{dia}")
    
    total_mensajes += msg
    total_llamadas += llm

st.divider()

# --- Guardar y Resumen ---
if st.button("Guardar Datos de la Semana", type="primary", use_container_width=True):
    st.success("¡Datos registrados correctamente!")

monto_total = total_llamadas * precio_llamada

st.subheader(f"Resumen de Cobro ({semana})")
st.info(f"**Total Mensajes:** {total_mensajes}\n\n**Total Llamadas Válidas:** {total_llamadas}")
st.metric(label=f"Monto a Cobrar esta {semana}", value=f"${monto_total:.2f}")

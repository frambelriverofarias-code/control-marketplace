import subprocess
import sys

# Forzar la instalación automática si falta el módulo
try:
    import st_gsheets_connection
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "st-gsheets-connection"])
    import st_gsheets_connection

from st_gsheets_connection import GSheetsConnection
import streamlit as st
import pandas as pd
from st_gsheets_connection import GSheetsConnection

# 1. Configuración de página centrada
st.set_page_config(
    page_title="Control de Llamadas y Pagos - Marketplace",
    page_icon="📋",
    layout="centered"
)

# Estilo CSS para ajustar márgenes y formato compacto
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 650px;
    }
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Conexión con Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    conn = None

st.title("Control de Llamadas y Pagos")

# 3. Pestañas principales
tab1, tab2 = st.tabs(["Registro y Cobros", "Reporte Mensual"])

with tab1:
    # --- SECCIÓN 1: Configuración y Tarifa ---
    with st.container(border=True):
        st.subheader("Configuración y Tarifa")
        
        col_mes, col_semana = st.columns(2)
        with col_mes:
            mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=6)
        with col_semana:
            semana = st.selectbox("Semana:", ["Semana 1", "Semana 2", "Semana 3", "Semana 4"], index=3)
        
        precio_llamada = st.number_input("Precio/Llamada ($):", min_value=0.0, value=1.20, step=0.10, format="%.2f")

    # --- SECCIÓN 2: Registro Diario ---
    with st.container(border=True):
        st.subheader("Registro Diario")
        
        # Encabezados de la mini-tabla
        h1, h2, h3 = st.columns([2, 3, 3])
        h1.caption("**Día**")
        h2.caption("**Mensajes**")
        h3.caption("**Llamadas Válidas**")

        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        total_mensajes = 0
        total_llamadas = 0
        registro_dias = {}

        for dia in dias:
            c_dia, c_msg, c_llm = st.columns([2, 3, 3])
            c_dia.write(f"**{dia}:**")
            
            msg = c_msg.number_input(f"Msg_{dia}", min_value=0, value=0, label_visibility="collapsed")
            llm = c_llm.number_input(f"Llm_{dia}", min_value=0, value=0, label_visibility="collapsed")
            
            registro_dias[dia] = {"mensajes": msg, "llamadas": llm}
            total_mensajes += msg
            total_llamadas += llm

        st.markdown("---")
        guardar = st.button("Guardar Datos de la Semana", use_container_width=True, type="primary")

        # LÓGICA DE GUARDADO EN GOOGLE SHEETS
        if guardar:
            monto_semana = total_llamadas * precio_llamada
            
            nuevo_registro = pd.DataFrame([{
                "Mes": mes,
                "Semana": semana,
                "Precio Llamada": precio_llamada,
                "Total Mensajes": total_mensajes,
                "Total Llamadas": total_llamadas,
                "Monto Cobrar": monto_semana
            }])
            
            if conn:
                try:
                    # Leer datos existentes para no sobreescribir
                    existing_data = conn.read()
                    updated_df = pd.concat([existing_data, nuevo_registro], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success(f"¡Datos de {mes} ({semana}) guardados exitosamente en Google Sheets!")
                except Exception as err:
                    st.error(f"Error al conectar con Google Sheets: {err}")
            else:
                st.warning("No se ha detectado la configuración de credenciales de Google Sheets en Render.")

    # --- SECCIÓN 3: Resumen de Cobro ---
    with st.container(border=True):
        st.subheader("Resumen de Cobro de la Semana")
        
        st.write(f"Total Mensajes ({semana}): **{total_mensajes}**")
        st.write(f"Total Llamadas Válidas ({semana}): **{total_llamadas}**")
        
        monto_total = total_llamadas * precio_llamada
        st.markdown(f"### **Monto a Cobrar esta Semana: ${monto_total:.2f}**")

with tab2:
    with st.container(border=True):
        st.subheader("Reporte Mensual")
        if conn:
            try:
                datos_hoja = conn.read()
                st.dataframe(datos_hoja, use_container_width=True)
            except Exception:
                st.info("Sin registros cargados aún en Google Sheets.")
        else:
            st.info("Configura las credenciales de Google Sheets para ver el historial.")

import os
import json
import streamlit as st
import pandas as pd
from st_gsheets_connection import GSheetsConnection

# URL de tu hoja de Google Sheets
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1NbCJ0tNwbAKVkUBk-A1RaeL4kfVw-b_O2cDq92UDedk/edit"

st.set_page_config(page_title="Control Marketplace", layout="wide")

# 1. Configuración de conexión leyendo de la Variable de Entorno de Render
gcp_json_str = os.getenv("GCP_SERVICE_ACCOUNT")

if gcp_json_str:
    try:
        creds_dict = json.loads(gcp_json_str)
        conn = st.connection(
            "gsheets",
            type=GSheetsConnection,
            service_account_info=creds_dict
        )
    except Exception as e:
        st.error(f"Error al procesar la variable GCP_SERVICE_ACCOUNT: {e}")
        st.stop()
else:
    # Si no encuentra la variable de entorno, intenta cargar por defecto
    conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📊 Control de Ventas / Marketplace")

# 2. Leer los datos actuales de la hoja (ttl=0 para tiempo real sin caché)
try:
    df_actual = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
    st.subheader("Registros Actuales")
    st.dataframe(df_actual, use_container_width=True)
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# 3. Formulario para ingresar nuevos registros
st.divider()
st.subheader("➕ Agregar Nuevo Registro")

with st.form("nuevo_registro_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        producto = st.text_input("Producto / Ítem")
    with col2:
        monto = st.number_input("Monto / Precio ($)", min_value=0.0, step=0.5)
        
    enviar = st.form_submit_button("💾 Guardar Registro", use_container_width=True)

    if enviar:
        if not producto:
            st.warning("Por favor, ingresa el nombre del producto.")
        else:
            # Crear la nueva fila de datos
            nuevo_dato = pd.DataFrame([{"Producto": producto, "Monto": monto}])
            
            # Combinar la lista existente con el nuevo dato
            df_actualizado = pd.concat([df_actual, nuevo_dato], ignore_index=True)
            
            # Sobrescribir / Actualizar en Google Sheets
            conn.update(spreadsheet=SPREADSHEET_URL, data=df_actualizado)
            
            st.success(f"¡'{producto}' guardado con éxito en Google Sheets!")
            st.rerun()  # Recarga la app para reflejar el cambio de inmediato

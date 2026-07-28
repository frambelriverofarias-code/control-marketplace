import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control Marketplace", layout="wide")
st.title("Control de Marketplace")

# 1. Crear la conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Cargar los datos guardados en tiempo real (ttl=0 evita memoria caché previa)
try:
    df_actual = conn.read(ttl=0)
except Exception as e:
    df_actual = pd.DataFrame(columns=["Cuenta", "Producto", "Precio", "Estado"])

# 3. Mostrar la tabla interactiva de datos existentes
st.subheader("Registros en Google Sheets")
st.dataframe(df_actual, use_container_width=True)

st.divider()

# 4. Formulario de registro de datos
st.subheader("Añadir nuevo registro")

with st.form("nuevo_registro", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        cuenta = st.text_input("Cuenta / Perfil")
        producto = st.text_input("Producto")
    with col2:
        precio = st.number_input("Precio ($)", min_value=0.0, format="%.2f")
        estado = st.selectbox("Estado", ["Activo", "Pausado", "Vendido", "Revisión"])

    boton_guardar = st.form_submit_button("Guardar de forma permanente")

# 5. Lógica para guardar la información permanentemente
if boton_guardar:
    if cuenta and producto:
        nueva_fila = pd.DataFrame([{
            "Cuenta": cuenta,
            "Producto": producto,
            "Precio": precio,
            "Estado": estado
        }])
        
        # Concatenar el registro nuevo con los existentes y actualizar la hoja
        df_actualizado = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(data=df_actualizado)
        
        st.success("¡Guardado correctamente en Google Sheets!")
        st.rerun()
    else:
        st.warning("Escribe al menos la Cuenta y el Producto.")

import streamlit as st

# 1. Configuración de página centrada y limpia
st.set_page_config(
    page_title="Control de Llamadas y Pagos - Marketplace",
    page_icon="📋",
    layout="centered"
)

# Estilo CSS opcional para ajustar márgenes y bordes compactos
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

st.title("Control de Llamadas y Pagos")

# 2. Pestañas principales
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
        
        # Diccionario o lista para capturar valores
        datos_dias = {}
        total_mensajes = 0
        total_llamadas = 0

        # Para simular los valores por defecto de tu imagen de referencia
        valores_ejemplo = {
            "Lunes": (63, 7),
            "Martes": (0, 0),
            "Miércoles": (0, 0),
            "Jueves": (0, 0),
            "Viernes": (0, 0),
            "Sábado": (0, 0),
            "Domingo": (0, 0)
        }

        for dia in dias:
            c_dia, c_msg, c_llm = st.columns([2, 3, 3])
            c_dia.write(f"**{dia}:**")
            
            val_msg_def, val_llm_def = valores_ejemplo.get(dia, (0, 0))
            
            msg = c_msg.number_input(f"Msg_{dia}", min_value=0, value=val_msg_def, label_visibility="collapsed")
            llm = c_llm.number_input(f"Llm_{dia}", min_value=0, value=val_llm_def, label_visibility="collapsed")
            
            total_mensajes += msg
            total_llamadas += llm

        st.markdown("---")
        guardar = st.button("Guardar Datos de la Semana", use_container_width=True, type="primary")

        if guardar:
            st.success(f"¡Datos guardados para {mes} - {semana}!")

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
        st.info("Aquí podrás consultar el acumulado de cobros e historial por mes.")

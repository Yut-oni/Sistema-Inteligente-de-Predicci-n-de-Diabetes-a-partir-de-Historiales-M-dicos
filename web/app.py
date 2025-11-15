# web/app.py
import streamlit as st
from auth import registrar_paciente, registrar_medico, login_usuario
from medico_dashboard import mostrar_dashboard_medico
from paciente_dashboard import mostrar_dashboard_paciente
from database import inicializar_bd

st.set_page_config(page_title="Sistema Inteligente de Predicción de Diabetes", layout="wide")

inicializar_bd()

if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    opcion = st.sidebar.selectbox("Selecciona una opción", ["Iniciar Sesión", "Registrar Médico", "Registrar Paciente"])

    if opcion == "Registrar Médico":
        registrar_medico()
    elif opcion == "Registrar Paciente":
        registrar_paciente()
    else:
        login_usuario()
else:
    tipo = st.session_state["tipo"]
    usuario = st.session_state["usuario"]

    st.sidebar.success(f"Sesión activa: {usuario['nombre']} ({tipo})")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["logueado"] = False
        st.session_state["usuario"] = None
        st.session_state["tipo"] = None
        st.rerun()

    if tipo == "Médico":
        mostrar_dashboard_medico(usuario["id"])
    else:
        mostrar_dashboard_paciente(usuario["id"])

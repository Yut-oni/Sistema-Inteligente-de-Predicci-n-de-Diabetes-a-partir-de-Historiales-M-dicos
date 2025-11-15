import streamlit as st
from database import conectar_bd
from prediccion import modulo_prediccion
from confirmacion_medica import modulo_confirmacion_medica

# ============================
# Estilos personalizados
# ============================
st.markdown("""
    <style>
        .main {
            background-color: #f9fafc;
        }
        .stSelectbox, .stNumberInput, .stTextInput, .stDateInput {
            border-radius: 10px;
        }
        div[data-testid="stExpander"] {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            background-color: #ffffff;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }
        .card {
            background-color: #ffffff;
            padding: 20px 25px;
            border-radius: 15px;
            box-shadow: 0px 3px 8px rgba(0,0,0,0.1);
            margin-top: 15px;
            margin-bottom: 15px;
        }
        .titulo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1a73e8;
        }
        .subtitulo {
            font-size: 1.1rem;
            color: #333;
            font-weight: 600;
            margin-top: 10px;
        }
        .info {
            color: #555;
            font-size: 0.95rem;
        }
    </style>
""", unsafe_allow_html=True)


def mostrar_dashboard_medico(medico_id):
    st.markdown("<h1 class='titulo'>Panel del Médico</h1>", unsafe_allow_html=True)
    st.write("Bienvenido doctor.")

    # ============================
    # Menú del médico
    # ============================
    opcion = st.radio(
        "Menú del Médico:",
        [
            "Pacientes",
            "Historial General",
            "Confirmar Diagnósticos Pendientes"
        ],
        horizontal=True
    )

    # ===================================================
    # VISTA: PACIENTES Y PREDICCIÓN
    # ===================================================
    if opcion == "Pacientes":
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes ORDER BY nombre ASC")
        pacientes = cursor.fetchall()
        cursor.close()
        conexion.close()

        st.markdown("<div class='subtitulo'>Seleccione un paciente para evaluación</div>", unsafe_allow_html=True)

        if not pacientes:
            st.info("No hay pacientes registrados aún.")
            return

        nombres = [f"{p['nombre']} (DNI: {p['dni']})" for p in pacientes]
        seleccion = st.selectbox("Seleccione un paciente:", nombres)

        paciente = next((p for p in pacientes if f"{p['nombre']} (DNI: {p['dni']})" == seleccion), None)

        if paciente:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Datos del Paciente")
            st.write(f"Nombre: {paciente['nombre']}")
            st.write(f"Género: {paciente['genero']}")
            st.write(f"Edad: {paciente['edad']}")
            st.write(f"DNI: {paciente['dni']}")
            st.markdown("</div>", unsafe_allow_html=True)


            st.markdown("### Nueva Predicción de Diabetes")
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            modulo_prediccion(paciente_id=paciente["id"], medico_id=medico_id)
            st.markdown("</div>", unsafe_allow_html=True)

    # ===================================================
    # VISTA: HISTORIAL GENERAL
    # ===================================================
    elif opcion == "Historial General":
        st.markdown("<div class='subtitulo'>Historial Médico General</div>", unsafe_allow_html=True)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    hm.id,
                    hm.fecha,
                    p.nombre AS paciente,
                    p.dni,
                    p.edad,
                    hm.glucosa,
                    hm.presion_sanguinea,
                    hm.insulina,
                    hm.bmi,
                    hm.embarazos,
                    hm.resultado_prediccion,
                    hm.observaciones,
                    m.nombre AS medico
                FROM historial_medico hm
                INNER JOIN pacientes p ON hm.paciente_id = p.id
                INNER JOIN medicos m ON hm.medico_id = m.id
                ORDER BY hm.fecha DESC
            """)
            historiales = cursor.fetchall()
            cursor.close()
            conexion.close()

            if not historiales:
                st.info("No hay historiales.")
                return

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)

            with col1:
                filtro_nombre = st.text_input("Buscar por nombre del paciente:")
            with col2:
                filtro_dni = st.text_input("Buscar por DNI:")
            with col3:
                filtro_fecha = st.date_input("Filtrar por fecha:", value=None)

            st.markdown("</div>", unsafe_allow_html=True)

            filtrados = historiales
            if filtro_nombre:
                filtrados = [h for h in filtrados if filtro_nombre.lower() in h["paciente"].lower()]
            if filtro_dni:
                filtrados = [h for h in filtrados if filtro_dni.lower() in (h["dni"] or "").lower()]
            if filtro_fecha:
                filtrados = [h for h in filtrados if h["fecha"].date() == filtro_fecha]

            if filtrados:
                st.dataframe(filtrados, use_container_width=True, height=500)
            else:
                st.warning("No se encontraron resultados.")

        except Exception as e:
            st.error(f"Error al cargar el historial médico: {e}")

    # ===================================================
    # VISTA: CONFIRMAR DIAGNÓSTICOS
    # ===================================================
    elif opcion == "Confirmar Diagnósticos Pendientes":
        modulo_confirmacion_medica()

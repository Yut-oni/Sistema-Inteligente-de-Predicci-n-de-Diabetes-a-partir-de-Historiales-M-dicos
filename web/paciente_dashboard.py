import streamlit as st
from database import conectar_bd

# ============================
# 🎨 Estilos visuales
# ============================
st.markdown("""
    <style>
        .main {
            background-color: #f5f7fa;
        }

        h1, h2, h3 {
            color: #2b4162;
            font-family: 'Helvetica Neue', sans-serif;
        }

        .encabezado {
            background: linear-gradient(120deg, #5a8dee, #4e73df);
            padding: 25px;
            border-radius: 12px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.15);
        }

        .tarjeta {
            background-color: white;
            border-radius: 12px;
            padding: 25px;
            margin-top: 20px;
            box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
        }

        div[data-testid="stExpander"] {
            border-radius: 10px;
            background-color: #ffffff;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        }

        .positivo {
            color: #2e7d32;
            font-weight: 600;
        }

        .negativo {
            color: #c62828;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)


# ============================
# 🩺 PANEL DEL PACIENTE
# ============================
def mostrar_dashboard_paciente(paciente_id):
    st.markdown(
        "<div class='encabezado'><h1>Panel del Paciente</h1><p>Consulta tus resultados médicos y seguimiento de salud.</p></div>",
        unsafe_allow_html=True
    )

    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT fecha, resultado_prediccion, glucosa, presion_sanguinea, insulina, bmi, edad, embarazos
        FROM historial_medico
        WHERE paciente_id = %s
        ORDER BY fecha DESC
    """, (paciente_id,))
    historial = cursor.fetchall()
    cursor.close()
    conexion.close()

    if not historial:
        st.info("Aún no hay registros médicos disponibles.")
        return

    # ============================
    # TARJETA RESUMEN
    # ============================
    st.markdown("<div class='tarjeta'>", unsafe_allow_html=True)
    st.subheader("Últimos valores registrados")

    ultimo = historial[0]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Glucosa (mg/dL)", ultimo["glucosa"])
    with col2:
        st.metric("Presión (mmHg)", ultimo["presion_sanguinea"])
    with col3:
        st.metric("BMI", ultimo["bmi"])
    st.caption(f"Última actualización: {ultimo['fecha'].strftime('%d/%m/%Y %H:%M')}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ============================
    # HISTORIAL DETALLADO
    # ============================
    st.markdown("<div class='tarjeta'>", unsafe_allow_html=True)
    st.subheader("Historial de Predicciones")

    for h in historial: 
        # Determinar color del texto según el resultado
        es_positivo = "Negativo" not in h["resultado_prediccion"]
        clase = "negativo" if es_positivo else "positivo"
        resultado_html = f"<span class='{clase}'>{h['resultado_prediccion']}</span>"

        with st.expander(f"{h['fecha'].strftime('%d/%m/%Y %H:%M')} — {h['resultado_prediccion']}"):
            st.markdown(
                f"""
                <p><strong>Resultado:</strong> {resultado_html}</p>
                <p><strong>Glucosa:</strong> {h['glucosa']} mg/dL</p>
                <p><strong>Presión Sanguínea:</strong> {h['presion_sanguinea']} mmHg</p>
                <p><strong>Insulina:</strong> {h['insulina']} μU/ml</p>
                <p><strong>Índice de Masa Corporal (BMI):</strong> {h['bmi']}</p>
                <p><strong>Edad:</strong> {h['edad']} años</p>
                <p><strong>Embarazos:</strong> {h['embarazos']}</p>
                """,
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

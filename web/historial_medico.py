import streamlit as st
from database import conectar_bd

def modulo_historial_medico():
    st.title("Historial Médico de Predicciones")

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                he.id,
                he.fecha,
                he.embarazos,
                he.glucosa,
                he.presion_sanguinea,
                he.grosor_piel,
                he.insulina,
                he.bmi,
                he.pedigree,
                he.edad,
                he.resultado_prediccion,
                he.probabilidad,
                he.outcome,
                he.observaciones
            FROM historial_entrenamiento he
            ORDER BY he.fecha DESC
        """)

        historiales = cursor.fetchall()
        cursor.close()
        conexion.close()

        if not historiales:
            st.info("No hay registros de predicciones todavía.")
            return

        st.subheader("Buscar historial")

        col1, col2 = st.columns(2)
        filtro_id = col1.text_input("Por ID:")
        filtro_fecha = col2.date_input("Por fecha:", value=None)

        filtrados = historiales

        if filtro_id:
            filtrados = [h for h in filtrados if str(h["id"]) == filtro_id]

        if filtro_fecha:
            filtrados = [h for h in filtrados if h["fecha"].date() == filtro_fecha]

        if filtrados:
            st.dataframe(filtrados, use_container_width=True)
        else:
            st.warning("No se encontraron resultados con esos filtros.")

    except Exception as e:
        st.error(f"Error al cargar el historial médico: {e}")

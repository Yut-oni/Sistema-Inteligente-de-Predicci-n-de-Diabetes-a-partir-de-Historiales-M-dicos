import streamlit as st
from web.database import conectar_bd

def mostrar_historial():
    st.subheader("📊 Historial de Predicciones")

    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, pa.nombre AS paciente, m.nombre AS medico, p.resultado, p.probabilidad, p.fecha
        FROM predicciones p
        JOIN pacientes pa ON p.paciente_id = pa.id
        JOIN medicos m ON p.medico_id = m.id
        ORDER BY p.fecha DESC;
    """)
    datos = cursor.fetchall()
    cursor.close()
    conexion.close()

    st.dataframe(datos, use_container_width=True)

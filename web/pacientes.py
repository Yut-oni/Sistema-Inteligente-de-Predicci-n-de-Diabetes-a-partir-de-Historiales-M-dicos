# web/pacientes.py
import streamlit as st
import mysql.connector
from database import conectar_bd

def registrar_paciente():
    st.subheader("🧑‍🤝‍🧑 Registrar Paciente")
    nombre = st.text_input("Nombre completo del paciente")
    genero = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
    edad = st.number_input("Edad", min_value=0, max_value=120, step=1)
    dni = st.text_input("DNI")

    if st.button("Registrar Paciente"):
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO pacientes (nombre, genero, edad, dni)
                VALUES (%s, %s, %s, %s)
            """, (nombre, genero, edad, dni))
            conexion.commit()
            st.success("✅ Paciente registrado correctamente.")
        except mysql.connector.Error as err:
            st.error(f"❌ Error al registrar paciente: {err}")
        finally:
            cursor.close()
            conexion.close()

def listar_pacientes():
    st.subheader("📋 Lista de Pacientes Registrados")
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes ORDER BY fecha_registro DESC")
        pacientes = cursor.fetchall()

        if pacientes:
            for p in pacientes:
                st.markdown(f"**🧍 {p['nombre']}** — {p['genero']}, {p['edad']} años — DNI: {p['dni']}")
        else:
            st.info("No hay pacientes registrados aún.")
    except mysql.connector.Error as err:
        st.error(f"❌ Error al cargar pacientes: {err}")
    finally:
        cursor.close()
        conexion.close()

# web/auth.py
import streamlit as st
import mysql.connector
from database import conectar_bd
import hashlib

# =============================
# FUNCIONES AUXILIARES
# =============================
def hash_password(password):
    """Encripta la contraseña con SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# =============================
# REGISTRO DE PACIENTE
# =============================
def registrar_paciente():
    st.subheader("🧍 Registro de Paciente")

    nombre = st.text_input("Nombre completo", key="nombre_pac")
    genero = st.selectbox("Género", ["Masculino", "Femenino"], key="genero_pac")
    edad = st.number_input("Edad", 1, 120, key="edad_pac")
    dni = st.text_input("DNI", key="dni_pac")
    correo = st.text_input("Correo electrónico", key="correo_pac")
    contrasena = st.text_input("Contraseña", type="password", key="pass_pac")

    if st.button("Registrar Paciente"):
        if nombre and correo and contrasena and dni:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Asegurar que las columnas existen
            try:
                cursor.execute("""
                    ALTER TABLE pacientes 
                    ADD COLUMN IF NOT EXISTS correo VARCHAR(100),
                    ADD COLUMN IF NOT EXISTS contrasena VARCHAR(255);
                """)
            except:
                pass

            # Insertar paciente si no existe
            cursor.execute("SELECT * FROM pacientes WHERE correo = %s OR dni = %s", (correo, dni))
            existente = cursor.fetchone()

            if existente:
                st.warning("⚠️ Ya existe un paciente con ese correo o DNI.")
            else:
                cursor.execute("""
                    INSERT INTO pacientes (nombre, genero, edad, dni, correo, contrasena)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nombre, genero, edad, dni, correo, hash_password(contrasena)))
                conexion.commit()
                st.success("✅ Paciente registrado correctamente.")

            cursor.close()
            conexion.close()
        else:
            st.warning("Completa todos los campos.")

# =============================
# REGISTRO DE MÉDICO
# =============================
def registrar_medico():
    st.subheader("🩺 Registro de Médico")

    nombre = st.text_input("Nombre completo", key="nombre_med")
    correo = st.text_input("Correo electrónico", key="correo_med")
    contrasena = st.text_input("Contraseña", type="password", key="pass_med")
    especialidad = st.text_input("Especialidad", key="esp_med")

    if st.button("Registrar Médico"):
        if nombre and correo and contrasena and especialidad:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar si ya existe el médico
            cursor.execute("SELECT * FROM medicos WHERE correo = %s", (correo,))
            if cursor.fetchone():
                st.warning("⚠️ Ya existe un médico con ese correo.")
            else:
                cursor.execute("""
                    INSERT INTO medicos (nombre, correo, contrasena, especialidad)
                    VALUES (%s,%s,%s,%s)
                """, (nombre, correo, hash_password(contrasena), especialidad))
                conexion.commit()
                st.success("✅ Médico registrado correctamente.")

            cursor.close()
            conexion.close()
        else:
            st.warning("Completa todos los campos.")

# =============================
# LOGIN (MÉDICO / PACIENTE)
# =============================
def login_usuario():
    st.subheader("🔐 Inicio de Sesión")

    tipo_usuario = st.radio("Tipo de usuario", ["Médico", "Paciente"], horizontal=True)
    correo = st.text_input("Correo electrónico", key=f"login_{tipo_usuario}_correo")
    contrasena = st.text_input("Contraseña", type="password", key=f"login_{tipo_usuario}_pass")

    if st.button("Iniciar Sesión"):
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        tabla = "medicos" if tipo_usuario == "Médico" else "pacientes"
        pass_col = "contrasena"

        cursor.execute(f"SELECT * FROM {tabla} WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario and usuario[pass_col] == hash_password(contrasena):
            st.session_state["usuario"] = usuario
            st.session_state["tipo"] = tipo_usuario
            st.session_state["logueado"] = True
            st.success(f"✅ Bienvenido {usuario['nombre']}")
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")

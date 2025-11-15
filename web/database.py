# web/database.py
import mysql.connector
import streamlit as st
import pandas as pd
import os

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "LOGGIN1212",
    "port": 3306
}

DB_NAME = "boradbearch"

def inicializar_bd():
    """Crea la base de datos, tablas y migra CSV a tabla de entrenamiento."""
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        # 1️⃣ Crear la base de datos
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute(f"USE {DB_NAME};")

        # 2️⃣ Crear tabla de médicos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100),
                correo VARCHAR(100) UNIQUE,
                contrasena VARCHAR(255),
                especialidad VARCHAR(100)
            );
        """)

        # 3️⃣ Crear tabla de pacientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100),
                genero VARCHAR(20),
                edad INT,
                dni VARCHAR(20),
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 4️⃣ Crear tabla de historiales pendientes (para predicciones)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_medico (
                id INT AUTO_INCREMENT PRIMARY KEY,
                paciente_id INT,
                medico_id INT,
                embarazos INT,
                glucosa FLOAT,
                presion FLOAT,
                grosor_piel FLOAT,
                insulina FLOAT,
                bmi FLOAT,
                pedigree FLOAT,
                edad INT,
                resultado_prediccion VARCHAR(50),
                probabilidad FLOAT,
                estado_confirmacion VARCHAR(30) DEFAULT 'Falta confirmar',
                outcome INT DEFAULT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
                FOREIGN KEY (medico_id) REFERENCES medicos(id)
            );
        """)

        # 5️⃣ Crear tabla de entrenamiento (solo confirmados)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_entrenamiento (
                id INT AUTO_INCREMENT PRIMARY KEY,
                embarazos INT,
                glucosa FLOAT,
                presion FLOAT,
                grosor_piel FLOAT,
                insulina FLOAT,
                bmi FLOAT,
                pedigree FLOAT,
                edad INT,
                outcome INT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conexion.commit()

        # 6️⃣ Migrar CSV a historial_entrenamiento si está vacío
        cursor.execute("SELECT COUNT(*) FROM historial_entrenamiento;")
        count = cursor.fetchone()[0]

        if count == 0:
            csv_path = "data/diabetes.csv"
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                # Renombrar columnas según tabla
                df = df.rename(columns={
                    "Pregnancies": "embarazos",
                    "Glucose": "glucosa",
                    "BloodPressure": "presion",
                    "SkinThickness": "grosor_piel",
                    "Insulin": "insulina",
                    "BMI": "bmi",
                    "DiabetesPedigreeFunction": "pedigree",
                    "Age": "edad",
                    "Outcome": "outcome"
                })

                for _, row in df.iterrows():
                    cursor.execute("""
                        INSERT INTO historial_entrenamiento
                        (embarazos, glucosa, presion, grosor_piel, insulina, bmi, pedigree, edad, outcome)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        int(row["embarazos"]), float(row["glucosa"]), float(row["presion"]),
                        float(row["grosor_piel"]), float(row["insulina"]), float(row["bmi"]),
                        float(row["pedigree"]), int(row["edad"]), int(row["outcome"])
                    ))
                conexion.commit()
                st.sidebar.success(f"✅ CSV migrado a historial_entrenamiento ({len(df)} registros).")
            else:
                st.sidebar.warning("⚠️ CSV no encontrado, no se migraron datos.")
        else:
            st.sidebar.info(f"ℹ️ Ya existen {count} registros en historial_entrenamiento.")

        cursor.close()
        conexion.close()

    except mysql.connector.Error as err:
        st.error(f"❌ Error en la base de datos: {err}")

def conectar_bd():
    """Devuelve una conexión activa al esquema principal."""
    return mysql.connector.connect(database=DB_NAME, **DB_CONFIG)

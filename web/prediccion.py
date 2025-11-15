import streamlit as st
import joblib
import numpy as np
from datetime import datetime
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
import os
from sklearn.ensemble import RandomForestClassifier
from database import conectar_bd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "diabetes_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "diabetes_scaler.pkl")


# Reentrenamiento del modelo
def reentrenar_modelo():
    try:
        st.info("Reentrenando modelo con datos confirmados...")

        conexion = conectar_bd()
        df = pd.read_sql("""
            SELECT embarazos, glucosa, presion,
                   grosor_piel, insulina, bmi, pedigree, edad, outcome
            FROM historial_entrenamiento
        """, conexion)
        conexion.close()

        if df.empty:
            st.warning("No existen datos confirmados para entrenar.")
            return

        X = df[["embarazos", "glucosa", "presion", "grosor_piel",
                "insulina", "bmi", "pedigree", "edad"]]
        y = df["outcome"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        rf = RandomForestClassifier(random_state=42)

        param_grid = {
            'n_estimators': [100, 150],
            'max_depth': [6, 8, None]
        }

        grid = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
        grid.fit(X_scaled, y)

        modelo_final = grid.best_estimator_
        accuracy = modelo_final.score(X_scaled, y)

        joblib.dump(modelo_final, MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)

        st.success(f"Modelo reentrenado exitosamente. Exactitud: {accuracy*100:.2f}%")

    except Exception as e:
        st.error(f"Error al reentrenar modelo: {e}")


# Módulo principal de predicción
def modulo_prediccion(paciente_id, medico_id):

    st.write("Datos clínicos del paciente")

    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pacientes WHERE id = %s", (paciente_id,))
    paciente = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not paciente:
        st.error("Paciente no encontrado")
        return

    genero = paciente.get("genero", "Masculino")
    edad = paciente.get("edad", 0)

    st.write(f"Paciente: {paciente['nombre']} ({genero}, {edad} años)")

    embarazos = st.number_input(
        "Cantidad de embarazos",
        min_value=0,
        step=1,
        value=0
    ) if genero.lower() in ["femenino", "mujer"] else 0

    glucosa = st.number_input("Nivel de glucosa", min_value=0.0)
    presion = st.number_input("Presión arterial", min_value=0.0)
    grosor_piel = st.number_input("Grosor de piel", min_value=0.0)
    insulina = st.number_input("Nivel de insulina", min_value=0.0)
    bmi = st.number_input("Índice de masa corporal (BMI)", min_value=0.0)
    pedigree = st.number_input("Función de pedigrí", min_value=0.0)

    if st.button("Realizar predicción"):
        try:
            # Validación SOLO de los campos clínicos que NO deben ser 0
            campos_invalidos = [glucosa, presion, grosor_piel, insulina, bmi, pedigree]

            if any(v == 0 for v in campos_invalidos):
                st.error("Digite los datos correctamente")
                return

            # Cargar modelo
            modelo = joblib.load(MODEL_PATH)
            scaler = joblib.load(SCALER_PATH)

            entrada = np.array([[embarazos, glucosa, presion, grosor_piel,
                                 insulina, bmi, pedigree, edad]])

            entrada_scaled = scaler.transform(entrada)

            prediccion = modelo.predict(entrada_scaled)[0]
            probabilidad = modelo.predict_proba(entrada_scaled)[0][1]

            resultado = "Positivo (Diabetes)" if prediccion == 1 else "Negativo (Sin Diabetes)"

            st.success(f"Resultado: {resultado}")
            st.info(f"Probabilidad estimada: {probabilidad * 100:.2f}%")

            observacion = f"EL PACIENTE TIENE {probabilidad*100:.2f}% DE CONTRAER DIABETES"

            # Guardar en BD
            conexion = conectar_bd()
            cursor = conexion.cursor()

            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO historial_medico
                (paciente_id, medico_id, embarazos, glucosa, presion_sanguinea,
                 grosor_piel, insulina, bmi, pedigree, edad,
                 resultado_prediccion, probabilidad,
                 estado_confirmacion, outcome, fecha, observaciones)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s)
            """, (
                paciente_id, medico_id, embarazos, glucosa, presion, grosor_piel,
                insulina, bmi, pedigree, edad,
                resultado, float(probabilidad),
                "Falta confirmar", None, fecha, observacion
            ))

            conexion.commit()
            cursor.close()
            conexion.close()

            st.success("Predicción guardada correctamente.")

        except Exception as e:
            st.error(f"Error al procesar predicción: {e}")

    st.divider()
    st.write("Reentrenamiento del modelo")

    if st.button("Reentrenar modelo"):
        reentrenar_modelo()

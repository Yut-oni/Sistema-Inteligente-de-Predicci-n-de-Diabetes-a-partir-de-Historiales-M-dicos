# web/confirmacion_medica.py
import streamlit as st
from database import conectar_bd
from datetime import datetime
from prediccion import reentrenar_modelo  # asegúrate que esta función exista en prediccion.py

# estilos (ajusta colores si quieres)
st.markdown(
    """
    <style>
    .card {
        background-color: var(--background-color, #0e1117);
        border-radius: 12px;
        padding: 16px;
        margin: 10px 6px;
        border: 1px solid rgba(255,255,255,0.03);
    }
    .patient-name { font-size: 1.1rem; font-weight:700; color:#a5d8ff; }
    .small { color: #b9c0c7; font-size:0.9rem; }
    .badge-high { color:#ff6b6b; font-weight:700; }
    .badge-low { color:#6be39a; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

def modulo_confirmacion_medica():
    st.title("Confirmación de predicciones pendientes")

    try:
        conn = conectar_bd()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT 
                hm.id, hm.paciente_id, hm.medico_id, hm.embarazos, hm.glucosa,
                hm.presion_sanguinea, hm.grosor_piel, hm.insulina, hm.bmi,
                hm.pedigree, hm.edad, hm.resultado_prediccion, hm.probabilidad,
                hm.fecha, hm.observaciones, p.nombre AS nombre_paciente
            FROM historial_medico hm
            LEFT JOIN pacientes p ON hm.paciente_id = p.id
            WHERE hm.estado_confirmacion = 'Falta confirmar'
            ORDER BY hm.fecha DESC
        """)
        pendientes = cur.fetchall()
        cur.close()
        conn.close()

        if not pendientes:
            st.info("No hay predicciones pendientes.")
            return

        # Renderizar en rejilla de 2 columnas
        cols_per_row = 2
        for i in range(0, len(pendientes), cols_per_row):
            row = pendientes[i:i+cols_per_row]
            cols = st.columns(len(row))
            for col, registro in zip(cols, row):
                with col:
                    # tarjeta
                    st.markdown("<div class='card'>", unsafe_allow_html=True)

                    # encabezado: avatar emoji + nombre
                    st.markdown(
                        f"<div style='display:flex; align-items:center; gap:10px;'>"
                        f"<div style='font-size:34px;'>👤</div>"
                        f"<div><div class='patient-name'>{registro.get('nombre_paciente') or 'Paciente sin nombre'}</div>"
                        f"<div class='small'>ID registro: {registro['id']} • Paciente ID: {registro['paciente_id']}</div></div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    st.markdown("<hr/>", unsafe_allow_html=True)

                    # datos en dos columnas internas
                    c1, c2 = st.columns([1,1])
                    with c1:
                        st.markdown(f"**Glucosa:** {registro.get('glucosa')}")
                        st.markdown(f"**Presión:** {registro.get('presion_sanguinea')}")
                        st.markdown(f"**BMI:** {registro.get('bmi')}")
                    with c2:
                        st.markdown(f"**Edad:** {registro.get('edad')}")
                        st.markdown(f"**Embarazos:** {registro.get('embarazos')}")
                        st.markdown(f"**Insulina:** {registro.get('insulina')}")

                    st.markdown("<hr/>", unsafe_allow_html=True)

                    # probabilidad / riesgo
                    prob = registro.get('probabilidad') or 0.0
                    riesgo_class = "badge-high" if prob >= 0.5 else "badge-low"
                    riesgo_text = "Alta" if prob >= 0.5 else "Baja"
                    st.markdown(
                        f"<div class='small'>Probabilidad: "
                        f"<span class='{riesgo_class}'>{prob*100:.2f}% ({riesgo_text})</span></div>",
                        unsafe_allow_html=True
                    )

                    # observaciones (si existen)
                    obs = registro.get('observaciones')
                    st.markdown("<div style='margin-top:8px;'><div class='small'>Observación automática:</div></div>", unsafe_allow_html=True)
                    st.write(obs if obs else "Sin observación.")

                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                    # botón con key único por registro id
                    btn_key = f"confirm_btn_{registro['id']}"
                    if st.button(f"Confirmar diagnóstico (ID {registro['id']})", key=btn_key):
                        # calcular outcome
                        outcome = 1 if prob >= 0.5 else 0

                        # insertar en historial_entrenamiento (sin observaciones)
                        conn2 = conectar_bd()
                        cur2 = conn2.cursor()
                        cur2.execute("""
                            INSERT INTO historial_entrenamiento
                            (embarazos, glucosa, presion, grosor_piel, insulina, bmi,
                             pedigree, edad, outcome, fecha)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (
                            registro.get('embarazos'),
                            registro.get('glucosa'),
                            registro.get('presion_sanguinea'),
                            registro.get('grosor_piel'),
                            registro.get('insulina'),
                            registro.get('bmi'),
                            registro.get('pedigree'),
                            registro.get('edad'),
                            outcome,
                            datetime.now()
                        ))

                        # actualizar historial_medico
                        cur2.execute("""
                            UPDATE historial_medico
                            SET estado_confirmacion=%s, outcome=%s
                            WHERE id=%s
                        """, ("Confirmado", outcome, registro['id']))

                        conn2.commit()
                        cur2.close()
                        conn2.close()

                        st.success("Diagnóstico confirmado y añadido al historial de entrenamiento.")
                        # reentrenar y refrescar la página
                        try:
                            reentrenar_modelo()
                            st.info("Modelo reentrenado con los nuevos datos.")
                        except Exception as e:
                            st.warning(f"No se pudo reentrenar automáticamente: {e}")

                        st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

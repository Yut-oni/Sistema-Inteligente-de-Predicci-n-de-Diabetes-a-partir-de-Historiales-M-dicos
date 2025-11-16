# 🧠 Sistema Inteligente de Predicción de Diabetes a partir de Historiales Médicos

Este sistema permite **predecir la probabilidad de que un paciente
padezca diabetes** utilizando historiales médicos reales y modelos de
machine learning.\
Incluye una **aplicación web en Streamlit**, una **base de datos
integrada**, y dashboards en **Power BI** para análisis visual de los
datos.


------------------------------------------------------------------------

## 📁 Estructura del Proyecto

    ├── .venv/                      # Entorno virtual de Python
    ├── data/                       # Archivos de datos (CSV)
    │   └── diabetes.csv
    ├── models/                     # Modelos entrenados (PKL)
    │   ├── diabetes_model.pkl
    │   └── diabetes_scaler.pkl
    ├── notebooks/                  # Notebooks para análisis o entrenamiento
    ├── web/                        # Código principal de la aplicación web
    │   ├── app.py
    │   ├── database.py
    │   ├── historial_medico.py
    │   ├── paciente_dashboard.py
    │   ├── medico_dashboard.py
    │   ├── prediccion.py
    │   └── requirements.txt
    ├── patients.db                 # Base de datos SQLite (opcional)
    ├── train_model.py              # Script para entrenar el modelo
    ├── requirements.txt            # Dependencias principales
    ├── start.sh                    # Script para iniciar la aplicación
    └── README.md                   # Este archivo

------------------------------------------------------------------------

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio

``` bash
git clone https://github.com/Yut-oni/Sistema-Inteligente-de-Prediccion-de-Diabetes.git
cd "Sistema Inteligente de Predicción de Diabetes a partir de Historiales Médicos"
```

### 2. Crear y activar entorno virtual

``` bash
python -m venv .venv
```

**Windows**

``` bash
.\.venv\Scriptsctivate
```

### 3. Instalar dependencias

``` bash
pip install -r web/requirements.txt
```

### 4. Ejecutar la aplicación

``` bash
streamlit run web/app.py
```

------------------------------------------------------------------------

## 🗄️ Conexión a Base de Datos MySQL (Railway)

Si se desea usar una base de datos remota, configurar variables de
entorno:

    DB_HOST=
    DB_NAME=
    DB_USER=
    DB_PASSWORD=
    DB_PORT=

⚠️ **Por seguridad no se incluyen contraseñas en este repositorio.**\
Configúralas localmente o mediante Railway Variables.

------------------------------------------------------------------------

## 📊 Uso con Power BI

1.  Abrir **Power BI Desktop**.\
2.  Conectar a MySQL usando los datos configurados.\
3.  Crear visualizaciones recomendadas:

### 📌 Gráficos sugeridos

-   **Pacientes con y sin diabetes** --- columna `outcome`
-   **Pacientes embarazadas vs no embarazadas** --- columna `embarazo`
-   **Probabilidad de diabetes por paciente** --- columna `probabilidad`
-   **Registros por fecha** --- columna `fecha_registro`

### 🖼️ Ejemplo de dashboards


------------------------------------------------------------------------

## 🧪 Entrenamiento del Modelo

Para regenerar el modelo:

``` bash
python train_model.py
```

------------------------------------------------------------------------

## 👤 Autor

**Jean Mario Paredes Lázaro**

------------------------------------------------------------------------

## 📝 Notas adicionales

-   Toda la lógica del sistema está en la carpeta **web/**.
-   Las dependencias específicas están en **web/requirements.txt**.
-   Este proyecto es para fines educativos y de investigación.

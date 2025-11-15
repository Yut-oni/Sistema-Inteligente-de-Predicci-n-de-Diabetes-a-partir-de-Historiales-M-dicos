# train_model.py
import os
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# Crear carpeta models si no existe
os.makedirs("models", exist_ok=True)

# 1 Cargar el dataset
df = pd.read_csv("data/diabetes.csv")

print("Shape del dataset:", df.shape)
print("Columnas:", df.columns.tolist())

# 2 Separar características y variable objetivo
X = df.drop("Outcome", axis=1)
y = df["Outcome"]

# 3 Dividir en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4 Escalar características
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5 Entrenar modelo con búsqueda de hiperparámetros
rf = RandomForestClassifier(random_state=42)
param_grid = {
    'n_estimators': [100, 150],
    'max_depth': [6, 8, None]
}

grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train_scaled, y_train)

best_model = grid_search.best_estimator_
print(" Mejores parámetros:", grid_search.best_params_)

# 6 Evaluar modelo
y_pred = best_model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n Precisión del modelo: {accuracy*100:.2f}%")
print("\n Reporte de Clasificación:\n", classification_report(y_test, y_pred))
print("\nMatriz de Confusión:\n", confusion_matrix(y_test, y_pred))

# 7 Guardar modelo y escalador
joblib.dump(best_model, "models/diabetes_model.pkl")
joblib.dump(scaler, "models/diabetes_scaler.pkl")

print("\n Modelo guardado en 'models/diabetes_model.pkl'")
print(" Scaler guardado en 'models/diabetes_scaler.pkl'")

"""Compara tres modelos (árbol, bosque y red neuronal) sobre los seis datasets.

Mide qué tan bien predice cada uno y también cuánto cuesta tenerlo:
tiempo de entrenamiento, tiempo de predicción y tamaño del archivo.

Uso (desde esta carpeta):
    python comparar_modelos.py
"""

import os
import tempfile
import time

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import f1_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

NUMERICAS = [
    "distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm", "volumen_l",
    "fragil", "refrigerado", "valor_declarado_mxn", "hora_salida",
]
CATEGORICAS = ["prioridad", "zona_destino", "clima", "trafico"]
OBJETIVO = "medio_recomendado"
ARCHIVOS = [f"envios{i}" for i in range(1, 7)]
BASE = "envios5"  # dataset con la misma distribución que el original


def preparar(escalar):
    """Mismo preprocesamiento que los scripts de entrenamiento."""
    pasos_numericos = [("imputar", SimpleImputer(strategy="median"))]
    if escalar:
        pasos_numericos.append(("escalar", StandardScaler()))
    return ColumnTransformer([
        ("numericas", Pipeline(pasos_numericos), NUMERICAS),
        ("categoricas", Pipeline([
            ("imputar", SimpleImputer(strategy="most_frequent")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]), CATEGORICAS),
    ])


def crear_modelos():
    return {
        "arbol": Pipeline([
            ("preparacion", preparar(escalar=False)),
            ("modelo", DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=42)),
        ]),
        "bosque": Pipeline([
            ("preparacion", preparar(escalar=False)),
            ("modelo", RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)),
        ]),
        "red": Pipeline([
            ("preparacion", preparar(escalar=True)),
            ("modelo", MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=800, random_state=42)),
        ]),
    }


def cargar(nombre):
    return pd.read_csv(f"datos/{nombre}.csv")


def tamano_mb(modelo):
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "modelo.joblib")
        joblib.dump(modelo, ruta)
        return os.path.getsize(ruta) / 1024 / 1024


def experimento_1():
    """Cada modelo se entrena y se prueba con el mismo archivo (80 % / 20 %)."""
    filas = []
    for archivo in ARCHIVOS:
        datos = cargar(archivo)
        x, y = datos[NUMERICAS + CATEGORICAS], datos[OBJETIVO]
        x_ent, x_pru, y_ent, y_pru = train_test_split(
            x, y, test_size=0.2, stratify=y, random_state=42
        )
        for nombre, modelo in crear_modelos().items():
            inicio = time.perf_counter()
            modelo.fit(x_ent, y_ent)
            t_entreno = time.perf_counter() - inicio

            inicio = time.perf_counter()
            pred = modelo.predict(x_pru)
            t_pred = (time.perf_counter() - inicio) / len(x_pru) * 1000

            fila = {
                "archivo": archivo,
                "modelo": nombre,
                "exactitud": round((pred == y_pru).mean(), 3),
                "f1_macro": round(f1_score(y_pru, pred, average="macro", zero_division=0), 3),
                "entreno_s": round(t_entreno, 1),
                "pred_ms_por_envio": round(t_pred, 4),
                "tamano_mb": round(tamano_mb(modelo), 2),
            }
            for medio in sorted(y.unique()):
                fila[f"recall_{medio}"] = round(
                    recall_score(y_pru, pred, labels=[medio], average="macro", zero_division=0), 3
                )
            filas.append(fila)
            print(f"  {archivo} / {nombre} listo", flush=True)
    return pd.DataFrame(filas)


def experimento_2():
    """Los modelos se entrenan con BASE y se prueban con todos los archivos."""
    base = cargar(BASE)
    x, y = base[NUMERICAS + CATEGORICAS], base[OBJETIVO]
    x_ent, x_pru, y_ent, y_pru = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
    )
    modelos = crear_modelos()
    for modelo in modelos.values():
        modelo.fit(x_ent, y_ent)

    filas = []
    for archivo in ARCHIVOS:
        if archivo == BASE:
            x_prueba, y_prueba = x_pru, y_pru  # el 20 % que no vio
        else:
            datos = cargar(archivo)
            x_prueba, y_prueba = datos[NUMERICAS + CATEGORICAS], datos[OBJETIVO]
        fila = {"archivo": archivo}
        for nombre, modelo in modelos.items():
            fila[nombre] = round((modelo.predict(x_prueba) == y_prueba).mean(), 3)
        filas.append(fila)
    return pd.DataFrame(filas)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 30)

    print("Experimento 1: entrenar y probar con el mismo archivo")
    resultado_1 = experimento_1()
    resultado_1.to_csv("resultados_experimento1.csv", index=False)

    print("\nExperimento 2: entrenar con", BASE, "y probar con todos")
    resultado_2 = experimento_2()
    resultado_2.to_csv("resultados_experimento2.csv", index=False)

    print("\n" + "=" * 70)
    print("EXPERIMENTO 1")
    print(resultado_1.to_string(index=False))
    print("\n" + "=" * 70)
    print(f"EXPERIMENTO 2 (entrenado con {BASE}; exactitud en cada archivo)")
    print(resultado_2.to_string(index=False))

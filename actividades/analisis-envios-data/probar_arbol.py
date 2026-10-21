import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

modelo = joblib.load("modelo_medios.joblib")

NUMERICAS = [
    "distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm", "volumen_l",
    "fragil", "refrigerado", "valor_declarado_mxn", "hora_salida",
]
CATEGORICAS = ["prioridad", "zona_destino", "clima", "trafico"]
OBJETIVO = "medio_recomendado"

for i in range(1, 7):
    datos = pd.read_csv(f"datos/envios{i}.csv")
    real = datos[OBJETIVO]
    prediccion = modelo.predict(datos[NUMERICAS + CATEGORICAS])

    mayoritaria = real.value_counts(normalize=True).iloc[0]
    print("=" * 60)
    print(f"envios{i}.csv")
    print(f"Exactitud: {(prediccion == real).mean():.1%}  (siempre la clase mayoritaria: {mayoritaria:.1%})")
    print(classification_report(real, prediccion, digits=3, zero_division=0))
    etiquetas = sorted(set(real) | set(prediccion))
    print("Filas = real, columnas = predicho")
    print(pd.DataFrame(
        confusion_matrix(real, prediccion, labels=etiquetas),
        index=etiquetas, columns=etiquetas,
    ))
    print()

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, export_text

datos = pd.read_csv("envios_medios.csv")

NUMERICAS = [
    "distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm", "volumen_l",
    "fragil", "refrigerado", "valor_declarado_mxn", "hora_salida",
]
CATEGORICAS = ["prioridad", "zona_destino", "clima", "trafico"]
OBJETIVO = "medio_recomendado"

x = datos[NUMERICAS + CATEGORICAS]
y = datos[OBJETIVO]

x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
    x, y, test_size=0.2, stratify=y, random_state=42
)

preparacion = ColumnTransformer([
    ("numericas", "passthrough", NUMERICAS),
    ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
])

modelo = Pipeline([
    ("preparacion", preparacion),
    ("arbol", DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=42)),
])

modelo.fit(x_entreno, y_entreno)

prediccion = modelo.predict(x_prueba)
print(f"Exactitud: {(prediccion == y_prueba).mean():.1%}")
print(classification_report(y_prueba, prediccion, digits=3))

etiquetas = sorted(y.unique())
print(pd.DataFrame(
    confusion_matrix(y_prueba, prediccion, labels=etiquetas),
    index=etiquetas, columns=etiquetas,
))

nombres = [n.split("__", 1)[1] for n in modelo.named_steps["preparacion"].get_feature_names_out()]
print(export_text(modelo.named_steps["arbol"], feature_names=nombres, max_depth=3))

joblib.dump(modelo, "modelo_medios.joblib")
print("Modelo guardado en modelo_medios.joblib")
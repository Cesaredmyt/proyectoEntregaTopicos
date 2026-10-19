import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, export_text

from entrenar_arbol import CATEGORICAS, NUMERICAS, OBJETIVO

pd.set_option("display.width", 200)
pd.set_option("display.max_rows", None)


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


datos = pd.read_csv("envios_medios.csv")
x = datos[NUMERICAS + CATEGORICAS]
y = datos[OBJETIVO]
x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
    x, y, test_size=0.2, stratify=y, random_state=42
)
modelo = joblib.load("modelo_medios.joblib")

# ---------------------------------------------------------------------------
titulo("Importancia de cada columna (las dummies de una categoría se suman)")
nombres = [n.split("__", 1)[1] for n in modelo.named_steps["preparacion"].get_feature_names_out()]
importancias = pd.Series(modelo.named_steps["arbol"].feature_importances_, index=nombres)
print("Con las columnas separadas (como las ve el árbol):")
print((importancias.sort_values(ascending=False) * 100).round(2))

por_columna = {}
for nombre, valor in importancias.items():
    original = next((c for c in CATEGORICAS if nombre.startswith(c + "_")), nombre)
    por_columna[original] = por_columna.get(original, 0) + valor
por_columna = pd.Series(por_columna).sort_values(ascending=False)
print("\nPor columna original (14 columnas):")
print((por_columna * 100).round(2))
print(f"\nColumnas con importancia 0: {list(por_columna[por_columna == 0].index)}")

titulo("Primeras preguntas del árbol (paso 8)")
print(export_text(modelo.named_steps["arbol"], feature_names=nombres, max_depth=3))

# ---------------------------------------------------------------------------
titulo("Quitar una columna y volver a medir (mismos 2000 envíos de prueba)")


def entrenar(numericas, categoricas):
    preparacion = ColumnTransformer([
        ("numericas", "passthrough", numericas),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), categoricas),
    ])
    arbol = Pipeline([
        ("preparacion", preparacion),
        ("arbol", DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=42)),
    ])
    arbol.fit(x_entreno[numericas + categoricas], y_entreno)
    prediccion = arbol.predict(x_prueba[numericas + categoricas])
    return (prediccion == y_prueba).mean()


base = entrenar(NUMERICAS, CATEGORICAS)
print(f"Con las 14 columnas: {base:.1%}")
filas = []
for columna in NUMERICAS + CATEGORICAS:
    exactitud = entrenar([c for c in NUMERICAS if c != columna], [c for c in CATEGORICAS if c != columna])
    filas.append({"columna quitada": columna, "exactitud": exactitud,
                  "cambio (puntos)": (exactitud - base) * 100})
tabla = pd.DataFrame(filas).sort_values("cambio (puntos)")
tabla["exactitud"] = (tabla["exactitud"] * 100).round(1).astype(str) + " %"
tabla["cambio (puntos)"] = tabla["cambio (puntos)"].round(2)
print(tabla.to_string(index=False))

# ---------------------------------------------------------------------------
titulo("Pregunta 3: zona_destino, distancia y el dron en el centro")
print("Distancia por zona:")
print(datos.groupby("zona_destino")["distancia_km"].agg(["min", "median", "max"]).round(1))
centro = datos[datos["zona_destino"] == "centro"]
print(f"\nEnvíos al centro: {len(centro)}; con distancia mayor a 15 km: {int((centro['distancia_km'] > 15).sum())}")
print(f"Drones en el centro: {int(((datos['zona_destino'] == 'centro') & (datos['medio_recomendado'] == 'dron')).sum())}")
drones_modelo = pd.Series(modelo.predict(x_prueba), index=x_prueba.index)
en_centro = x_prueba["zona_destino"] == "centro"
print(f"Veces que el modelo dice dron en envíos de centro (prueba): {int(((drones_modelo == 'dron') & en_centro).sum())} de {int(en_centro.sum())}")
print("Zona de destino en el CSV que el modelo ve: se usa en alguna pregunta del árbol completo:",
      any(n.startswith("zona_destino") and v > 0 for n, v in importancias.items()))
print("\nZona vs distancia: ¿la distancia ya dice la zona?")
datos_tmp = datos.assign(rango=pd.cut(datos["distancia_km"], [0, 6, 15, 30, 100]))
print(pd.crosstab(datos_tmp["rango"], datos_tmp["zona_destino"], normalize="index").round(2))

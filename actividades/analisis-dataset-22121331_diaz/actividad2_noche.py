import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from entrenar_arbol import CATEGORICAS, NUMERICAS, OBJETIVO

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)
datos = pd.read_csv("envios_medios.csv")


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


# ---------------------------------------------------------------------------
# Pregunta 4: ¿cuántas preguntas "hora <= X" necesita un árbol para la noche?
# ---------------------------------------------------------------------------
titulo("Pregunta 4: árbol que solo ve la hora y debe adivinar si es de noche")
datos["es_noche"] = ((datos["hora_salida"] < 6) | (datos["hora_salida"] >= 21)).astype(int)
for profundidad in (1, 2):
    arbol = DecisionTreeClassifier(max_depth=profundidad, random_state=42)
    arbol.fit(datos[["hora_salida"]], datos["es_noche"])
    acierto = (arbol.predict(datos[["hora_salida"]]) == datos["es_noche"]).mean()
    print(f"Con {profundidad} nivel(es) de preguntas: acierta {acierto:.1%}")

# ---------------------------------------------------------------------------
# Para pensar: ¿ayuda la columna es_noche al modelo?
# ---------------------------------------------------------------------------
titulo("Para pensar: modelo sin y con la columna es_noche (mismos envíos de prueba)")

x_entreno_t, x_prueba_t, y_entreno, y_prueba = train_test_split(
    datos[NUMERICAS + CATEGORICAS + ["es_noche"]], datos[OBJETIVO],
    test_size=0.2, stratify=datos[OBJETIVO], random_state=42,
)


def evaluar(numericas, profundidad):
    preparacion = ColumnTransformer([
        ("numericas", "passthrough", numericas),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
    ])
    modelo = Pipeline([
        ("preparacion", preparacion),
        ("arbol", DecisionTreeClassifier(max_depth=profundidad, min_samples_leaf=5, random_state=42)),
    ])
    modelo.fit(x_entreno_t[numericas + CATEGORICAS], y_entreno)
    prediccion = pd.Series(modelo.predict(x_prueba_t[numericas + CATEGORICAS]), index=y_prueba.index)
    de_noche = x_prueba_t["es_noche"] == 1
    return {
        "exactitud": (prediccion == y_prueba).mean(),
        "exactitud de noche": (prediccion[de_noche] == y_prueba[de_noche]).mean(),
        "errores de noche": int((prediccion[de_noche] != y_prueba[de_noche]).sum()),
        "recall dron": recall_score(y_prueba, prediccion, labels=["dron"], average=None, zero_division=0)[0],
        "precision dron": precision_score(y_prueba, prediccion, labels=["dron"], average=None, zero_division=0)[0],
        "moto->dron": int(((y_prueba == "moto") & (prediccion == "dron")).sum()),
        "moto->dron de noche": int(((y_prueba == "moto") & (prediccion == "dron") & de_noche).sum()),
    }


print(f"Envíos de prueba: {len(y_prueba)}, de noche: {int((x_prueba_t['es_noche'] == 1).sum())}")
for profundidad in (8,):
    filas = {
        "sin es_noche": evaluar(NUMERICAS, profundidad),
        "con es_noche": evaluar(NUMERICAS + ["es_noche"], profundidad),
    }
    print(f"\nProfundidad máxima del árbol: {profundidad}")
    print(pd.DataFrame(filas).T.round(3))

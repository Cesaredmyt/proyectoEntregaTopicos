import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from entrenar_arbol import CATEGORICAS, NUMERICAS, OBJETIVO
from usar_modelo import es_posible

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


# Misma separación que en el paso 4 de la guía.
datos = pd.read_csv("envios_medios.csv")
x = datos[NUMERICAS + CATEGORICAS]
y = datos[OBJETIVO]
x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
    x, y, test_size=0.2, stratify=y, random_state=42
)

modelo = joblib.load("modelo_medios.joblib")
resultados = x_prueba.assign(real=y_prueba, predicho=modelo.predict(x_prueba))
resultados["noche"] = (resultados["hora_salida"] < 6) | (resultados["hora_salida"] >= 21)
errores = resultados[resultados["real"] != resultados["predicho"]]

# ---------------------------------------------------------------------------
titulo("Pregunta 1: errores y confusiones más frecuentes")
print(f"Envíos de prueba: {len(resultados)}")
print(f"Errores: {len(errores)} ({len(errores) / len(resultados):.1%})")
print(f"Exactitud: {(resultados['real'] == resultados['predicho']).mean():.1%}")
confusiones = errores.groupby(["real", "predicho"]).size().sort_values(ascending=False)
print("\nTodas las confusiones (real -> predicho):")
print(confusiones)
print("\nMatriz de confusión completa (filas: real, columnas: predicho):")
print(pd.crosstab(resultados["real"], resultados["predicho"]))
print(f"\nVeces que confunde bicicleta con camioneta (en cualquier sentido): "
      f"{len(errores[errores['real'].isin(['bicicleta', 'camioneta']) & errores['predicho'].isin(['bicicleta', 'camioneta'])])}")

# ---------------------------------------------------------------------------
titulo("Pregunta 2: eran moto y el modelo mandó a dron")
moto_dron = errores[(errores["real"] == "moto") & (errores["predicho"] == "dron")]
print(f"Total: {len(moto_dron)}")
print(f"De noche: {int(moto_dron['noche'].sum())}")
imposible = ~moto_dron.apply(lambda fila: es_posible("dron", fila), axis=1)
print(f"Dron imposible según las reglas del negocio (las reglas lo corrigen): {int(imposible.sum())}")
print(f"Dron posible según las reglas (las reglas NO lo corrigen): {int((~imposible).sum())}")
print("\nPor qué es imposible el dron en los que sí se corrigen:")
razones = pd.DataFrame({
    "noche": moto_dron["noche"],
    "clima distinto de despejado": moto_dron["clima"] != "despejado",
    "zona centro": moto_dron["zona_destino"] == "centro",
    "pesa más de 2.5 kg": moto_dron["peso_kg"] > 2.5,
    "volumen mayor a 12 L": moto_dron["volumen_l"] > 12,
    "distancia mayor a 15 km": moto_dron["distancia_km"] > 15,
    "refrigerado": moto_dron["refrigerado"] == 1,
})
print(razones.sum())
no_corregidos = moto_dron[~imposible]
print("\nLos que las reglas NO corrigen:")
print(no_corregidos[["distancia_km", "peso_kg", "volumen_l", "fragil", "valor_declarado_mxn",
                     "prioridad", "zona_destino", "clima", "hora_salida", "trafico"]])
print("\nResumen de esos casos:")
print(no_corregidos[["distancia_km", "peso_kg", "volumen_l", "fragil", "valor_declarado_mxn"]].describe().round(2))
print(no_corregidos["prioridad"].value_counts())
print(no_corregidos["zona_destino"].value_counts())
print(no_corregidos["clima"].value_counts())
print("\nPara comparar: todas las motos de la prueba")
motos = resultados[resultados["real"] == "moto"]
print(motos[["distancia_km", "peso_kg", "volumen_l", "fragil", "valor_declarado_mxn"]].describe().round(2))
print(motos["prioridad"].value_counts(normalize=True).round(2))

# ---------------------------------------------------------------------------
titulo("Pregunta 3: eran moto y el modelo mandó a bicicleta")
moto_bici = errores[(errores["real"] == "moto") & (errores["predicho"] == "bicicleta")]
print(f"Total: {len(moto_bici)}")
print(moto_bici[["distancia_km", "peso_kg", "volumen_l", "fragil", "valor_declarado_mxn",
                 "prioridad", "zona_destino", "clima", "hora_salida", "trafico"]])
print(f"\nCuántos están a 1 km o menos del límite de 7 km (6 a 7): "
      f"{int(((moto_bici['distancia_km'] >= 6) & (moto_bici['distancia_km'] <= 7)).sum())}")
print(f"Distancia: mín {moto_bici['distancia_km'].min():.1f}, mediana {moto_bici['distancia_km'].median():.1f}, "
      f"máx {moto_bici['distancia_km'].max():.1f}")
print(f"Cuántos ya son imposibles para bicicleta (las reglas los corrigen): "
      f"{int((~moto_bici.apply(lambda fila: es_posible('bicicleta', fila), axis=1)).sum())}")

bicis_bien = resultados[(resultados["real"] == "bicicleta") & (resultados["predicho"] == "bicicleta")]
columnas = ["distancia_km", "peso_kg", "volumen_l", "fragil", "valor_declarado_mxn", "hora_salida"]
print("\nMedianas: moto mal mandada a bici vs bicicletas bien acertadas")
print(pd.DataFrame({
    "moto -> bici": moto_bici[columnas].median(),
    "bici acertada": bicis_bien[columnas].median(),
}).round(2))
for columna in ["prioridad", "zona_destino", "clima", "trafico", "noche"]:
    print(f"\n{columna} (proporción):")
    print(pd.DataFrame({
        "moto -> bici": moto_bici[columna].value_counts(normalize=True),
        "bici acertada": bicis_bien[columna].value_counts(normalize=True),
    }).round(2))

# ---------------------------------------------------------------------------
titulo("Otro random_state: ¿cambia el análisis?")
filas = []
for semilla in (1, 7, 42, 99, 2024):
    xe, xp, ye, yp = train_test_split(x, y, test_size=0.2, stratify=y, random_state=semilla)
    otro = Pipeline([
        ("preparacion", ColumnTransformer([
            ("numericas", "passthrough", NUMERICAS),
            ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
        ])),
        ("arbol", DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=42)),
    ]).fit(xe, ye)
    pred = pd.Series(otro.predict(xp), index=yp.index)
    mal = pd.DataFrame({"real": yp[yp != pred], "predicho": pred[yp != pred]})
    top = mal.groupby(["real", "predicho"]).size().sort_values(ascending=False)
    filas.append({
        "random_state": semilla,
        "errores": len(mal),
        "exactitud": round((yp == pred).mean(), 3),
        "confusión #1": f"{top.index[0][0]}->{top.index[0][1]} ({top.iloc[0]})",
        "confusión #2": f"{top.index[1][0]}->{top.index[1][1]} ({top.iloc[1]})",
        "moto->dron": int(((yp == "moto") & (pred == "dron")).sum()),
    })
print(pd.DataFrame(filas).to_string(index=False))

# ---------------------------------------------------------------------------
titulo("Extra 1: camionetas reales que el modelo manda a bicicleta")
cami_bici = errores[(errores["real"] == "camioneta") & (errores["predicho"] == "bicicleta")]
print(f"Total: {len(cami_bici)}")
print(cami_bici[["distancia_km", "peso_kg", "volumen_l", "refrigerado", "zona_destino", "clima", "prioridad", "hora_salida"]])
puede_ir_en_bici = cami_bici.apply(lambda fila: es_posible("bicicleta", fila), axis=1)
puede_ir_en_moto = cami_bici.apply(lambda fila: es_posible("moto", fila), axis=1)
print(f"Para estos, la bicicleta es posible según las reglas: {int(puede_ir_en_bici.sum())} de {len(cami_bici)}")
print(f"Para estos, la moto es posible según las reglas: {int(puede_ir_en_moto.sum())} de {len(cami_bici)}")
print(f"Los corregirían las reglas del negocio: {int((~puede_ir_en_bici).sum())}")

# ---------------------------------------------------------------------------
titulo("Extra 2: ¿cambiar el modelo ataca moto -> bicicleta? (bosque de árboles)")
from sklearn.ensemble import RandomForestClassifier

bosque = Pipeline([
    ("preparacion", ColumnTransformer([
        ("numericas", "passthrough", NUMERICAS),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
    ])),
    ("bosque", RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)),
]).fit(x_entreno, y_entreno)
pred_bosque = pd.Series(bosque.predict(x_prueba), index=y_prueba.index)
print(f"Exactitud del árbol: {(resultados['real'] == resultados['predicho']).mean():.1%}   "
      f"del bosque: {(pred_bosque == y_prueba).mean():.1%}")
print(f"Errores del árbol: {len(errores)}   del bosque: {int((pred_bosque != y_prueba).sum())}")
print(f"moto -> bicicleta: árbol {len(moto_bici)}   bosque {int(((y_prueba == 'moto') & (pred_bosque == 'bicicleta')).sum())}")
print(f"moto -> dron:      árbol {len(moto_dron)}   bosque {int(((y_prueba == 'moto') & (pred_bosque == 'dron')).sum())}")

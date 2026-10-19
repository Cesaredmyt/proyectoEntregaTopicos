import subprocess
import sys
import tempfile
from pathlib import Path

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


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


datos = pd.read_csv("envios_medios.csv")
columnas = NUMERICAS + CATEGORICAS
x = datos[columnas]
y = datos[OBJETIVO]
# Misma separación de siempre: los mismos 2000 envíos de prueba.
x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
    x, y, test_size=0.2, stratify=y, random_state=42
)
print(f"Entrenamiento: {len(x_entreno)}, prueba: {len(x_prueba)}, drones en la prueba: {(y_prueba == 'dron').sum()}")
print("Reparto en entrenamiento:", y_entreno.value_counts().to_dict())


def evaluar(x_ent, y_ent, x_test=x_prueba, y_test=y_prueba, class_weight=None):
    """Entrena un árbol igual al del paso 6 y lo mide con los envíos de prueba."""
    modelo = Pipeline([
        ("preparacion", ColumnTransformer([
            ("numericas", "passthrough", NUMERICAS),
            ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
        ])),
        ("arbol", DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=42,
                                         class_weight=class_weight)),
    ]).fit(x_ent[columnas], y_ent)
    pred = pd.Series(modelo.predict(x_test[columnas]), index=x_test.index)
    dijo_dron = pred == "dron"
    es_dron = y_test == "dron"
    aciertos_dron = int((dijo_dron & es_dron).sum())
    imposibles = int(sum(not es_posible(m, fila) for m, (_, fila) in zip(pred, x_test.iterrows())))
    dron_idx = list(modelo.classes_).index("dron")
    prob_dron = modelo.predict_proba(x_test[columnas])[:, dron_idx]
    dron_de_mas = x_test[dijo_dron & ~es_dron]
    return {
        "envíos de entrenamiento": len(x_ent),
        "% dron al entrenar": round((y_ent == "dron").mean() * 100, 1),
        "exactitud": round((pred == y_test).mean() * 100, 1),
        "precision dron": round(aciertos_dron / max(int(dijo_dron.sum()), 1), 3),
        "recall dron": round(aciertos_dron / int(es_dron.sum()), 3),
        "veces que dice dron": int(dijo_dron.sum()),
        "drones de más": int((dijo_dron & ~es_dron).sum()),
        "drones de más que las reglas corrigen": int(sum(not es_posible("dron", f) for _, f in dron_de_mas.iterrows())),
        "drones que no encontró": int((~dijo_dron & es_dron).sum()),
        "sugerencias imposibles": imposibles,
        "prob. media de dron": round(float(prob_dron.mean()), 3),
    }


def con_y(x_, y_):
    return x_.assign(**{OBJETIVO: y_})


entreno = con_y(x_entreno, y_entreno)
mayor = int(y_entreno.value_counts().max())     # moto
menor = int(y_entreno.value_counts().min())     # dron

estrategias = {}
estrategias["Sin balancear"] = evaluar(x_entreno, y_entreno)

# 1. Quitar ejemplos sobrantes: todas las clases quedan del tamaño de la más chica.
quitar = entreno.groupby(OBJETIVO, group_keys=False).sample(n=menor, random_state=42)
estrategias["1. Quitar sobrantes"] = evaluar(quitar[columnas], quitar[OBJETIVO])

# 2. Repetir solo los drones hasta igualar a la moto.
drones = entreno[entreno[OBJETIVO] == "dron"]
repetir_dron = pd.concat([entreno, drones.sample(n=mayor - len(drones), replace=True, random_state=42)])
estrategias["2. Repetir solo drones"] = evaluar(repetir_dron[columnas], repetir_dron[OBJETIVO])

# 3. Repetir todas las clases chicas hasta igualar a la moto.
partes = [g.sample(n=mayor, replace=True, random_state=42) if len(g) < mayor else g
          for _, g in entreno.groupby(OBJETIVO)]
repetir_todas = pd.concat(partes)
estrategias["3. Repetir todas las chicas"] = evaluar(repetir_todas[columnas], repetir_todas[OBJETIVO])

# 4. Dar más peso a las clases chicas sin tocar los datos.
estrategias["4. class_weight balanced"] = evaluar(x_entreno, y_entreno, class_weight="balanced")

# 5. Conseguir drones nuevos con el generador (otra semilla), solo para entrenar.
with tempfile.TemporaryDirectory() as carpeta:
    nuevos_csv = Path(carpeta) / "nuevos.csv"
    subprocess.run([sys.executable, "generar_dataset.py", "--filas", "40000", "--semilla", "7",
                    "--salida", str(nuevos_csv)], check=True, capture_output=True)
    nuevos = pd.read_csv(nuevos_csv)
nuevos_drones = nuevos[nuevos[OBJETIVO] == "dron"].sample(n=mayor - len(drones), random_state=42)
con_nuevos = pd.concat([entreno, nuevos_drones[columnas + [OBJETIVO]]])
estrategias["5. Drones nuevos (generador)"] = evaluar(con_nuevos[columnas], con_nuevos[OBJETIVO])

titulo("Parte B: tabla por estrategia (mismos 2000 envíos de prueba, 190 drones)")
tabla = pd.DataFrame(estrategias).T
print(tabla.to_string())

# ---------------------------------------------------------------------------
titulo("Trampa: balancear ANTES de separar")
completo = datos.copy()
drones_todos = completo[completo[OBJETIVO] == "dron"]
mayor_todos = int(completo[OBJETIVO].value_counts().max())
trampa = pd.concat([completo, drones_todos.sample(n=mayor_todos - len(drones_todos), replace=True, random_state=42)])
x_t, y_t = trampa[columnas + ["id_envio"]], trampa[OBJETIVO]
xe_t, xp_t, ye_t, yp_t = train_test_split(x_t, y_t, test_size=0.2, stratify=y_t, random_state=42)
resultado_trampa = evaluar(xe_t, ye_t, x_test=xp_t, y_test=yp_t)
copias = int(xp_t["id_envio"].isin(xe_t["id_envio"]).sum())
copias_dron = int((xp_t["id_envio"].isin(xe_t["id_envio"]) & (yp_t == "dron")).sum())
print(f"Envíos de prueba: {len(xp_t)}, drones en la prueba: {(yp_t == 'dron').sum()}")
print(f"Envíos de prueba que ya estaban (iguales) en el entrenamiento: {copias} ({copias / len(xp_t):.1%})")
print(f"De los drones de la prueba, ya vistos en el entrenamiento: {copias_dron}")
print(pd.DataFrame({"Honesto (sin balancear)": estrategias["Sin balancear"],
                    "Trampa (balanceo antes)": resultado_trampa}).to_string())

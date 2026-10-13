import pandas as pd

from usar_modelo import LIMITES, es_posible

datos = pd.read_csv("envios_medios.csv")
pd.set_option("display.width", 200)


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


titulo("Porcentaje de cada medio según el clima")
print((pd.crosstab(datos["clima"], datos["medio_recomendado"], normalize="index") * 100).round(1))

titulo("Porcentaje de cada medio según la zona de destino")
print((pd.crosstab(datos["zona_destino"], datos["medio_recomendado"], normalize="index") * 100).round(1))

titulo("Conteo de envíos por zona y medio")
print(pd.crosstab(datos["zona_destino"], datos["medio_recomendado"]))

titulo("Conteo de drones por clima y zona")
drones = datos[datos["medio_recomendado"] == "dron"]
print(pd.crosstab(drones["clima"], drones["zona_destino"]))

titulo("Mínimo, mediana y máximo por medio")
columnas = ["distancia_km", "peso_kg", "volumen_l"]
print(datos.groupby("medio_recomendado")[columnas].agg(["min", "median", "max"]).round(1))

titulo("LIMITES del negocio")
print(pd.DataFrame(LIMITES).T)

titulo("Etiquetas que rompen las reglas del negocio")
imposibles = datos[~datos.apply(lambda fila: es_posible(fila["medio_recomendado"], fila), axis=1)]
print(f"Total: {len(imposibles)} de {len(datos)}")

titulo("Distancia media por zona")
print(datos.groupby("zona_destino")["distancia_km"].agg(["min", "median", "mean", "max"]).round(1))

titulo("Bicicleta: distancia media en cada zona")
bicis = datos[datos["medio_recomendado"] == "bicicleta"]
print(bicis.groupby("zona_destino")["distancia_km"].agg(["count", "mean", "max"]).round(1))

titulo("Porcentaje de envíos de 7 km o menos, por zona")
print((datos.assign(cerca=datos["distancia_km"] <= 7).groupby("zona_destino")["cerca"].mean() * 100).round(1))

titulo("Camionetas para viajes de menos de 2 km")
cortas = datos[(datos["medio_recomendado"] == "camioneta") & (datos["distancia_km"] < 2)]
print(f"Total: {len(cortas)}")
razon_peso = cortas["peso_kg"] > LIMITES["moto"]["peso_kg"]
razon_volumen = cortas["volumen_l"] > LIMITES["moto"]["volumen_l"]
razon_frio = cortas["refrigerado"] == 1
con_razon = razon_peso | razon_volumen | razon_frio
print(f"Por peso (más de 25 kg): {razon_peso.sum()}")
print(f"Por volumen (más de 90 L): {razon_volumen.sum()}")
print(f"Por refrigerado: {razon_frio.sum()}")
print(f"Con al menos una razón clara: {con_razon.sum()}")
print(f"Sin razón clara: {(~con_razon).sum()}")
sin_razon = cortas[~con_razon]
print(sin_razon[["distancia_km", "peso_kg", "volumen_l", "refrigerado", "prioridad", "clima", "trafico", "hora_salida", "valor_declarado_mxn", "fragil"]].describe().round(1))
print(sin_razon["clima"].value_counts())
print(sin_razon["prioridad"].value_counts())

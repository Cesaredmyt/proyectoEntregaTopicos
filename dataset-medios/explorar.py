import pandas as pd

datos = pd.read_csv("envios_medios.csv")

print(datos.shape)
print(datos.head())
print(datos["medio_recomendado"].value_counts())
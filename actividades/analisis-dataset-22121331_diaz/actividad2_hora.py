import matplotlib

matplotlib.use("Agg")  # dibuja en un archivo, sin abrir ventana
import matplotlib.pyplot as plt
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 200)

datos = pd.read_csv("envios_medios.csv")


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


titulo("Envíos por hora de salida y medio")
tabla = pd.crosstab(datos["hora_salida"], datos["medio_recomendado"])
print(tabla)

titulo("Drones a las 3:00")
print(tabla.loc[3, "dron"])

titulo("Horas sin ningún dron")
print(tabla.index[tabla["dron"] == 0].tolist())

titulo("Envíos de noche (antes de las 6 o desde las 21)")
noche = (datos["hora_salida"] < 6) | (datos["hora_salida"] >= 21)
print(f"De noche: {noche.sum()} de {len(datos)}")
print(f"Porcentaje: {noche.mean() * 100:.1f} %")

tabla.plot(kind="bar", stacked=True, figsize=(12, 6))
plt.title("Medio recomendado por hora de salida")
plt.xlabel("Hora de salida")
plt.ylabel("Número de envíos")
plt.legend(title="Medio")
plt.tight_layout()
plt.savefig("actividad2_hora.png", dpi=150)
print("\nGráfica guardada en actividad2_hora.png")

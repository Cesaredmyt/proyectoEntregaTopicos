import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000/entregas/cotizar/"

km = sys.argv[1] if len(sys.argv) > 1 else "12"
kg = sys.argv[2] if len(sys.argv) > 2 else "3"

url = BASE + "?" + urllib.parse.urlencode({"km": km, "kg": kg})

try:
    with urllib.request.urlopen(url) as respuesta:
        datos = json.load(respuesta)
    print("Medio sugerido:", datos["medio"])
    print("Motivo:", datos["motivo"])
except urllib.error.HTTPError as error:
    print("El servidor rechazó los datos (código", error.code, "):", json.load(error)["error"])
except urllib.error.URLError:
    print("No se pudo conectar con el servidor. ¿Está corriendo runserver?")
import socket
import math

from .reglas import elegir_medio
from django.http import HttpResponse, JsonResponse

COPIA = socket.gethostname()

visitas_en_memoria = 0

def hola(request):
    return HttpResponse("Hola. Plataforma de entregas (aún sin pedidos).")

def estado(request):
    return JsonResponse({
        "servicio": "entregas",
        "version": 1,
        "medios_disponibles": ["camioneta", "moto", "bicicleta", "dron"],
        "atendido_por": COPIA,
    })

def visitas(request):
    request.session["visitas"] = request.session.get("visitas", 0) + 1
    return JsonResponse({
        "atendido_por": COPIA,
        "visitas": request.session["visitas"],
    })

def visitas_mal(request):
    global visitas_en_memoria
    visitas_en_memoria += 1
    return JsonResponse({
        "atendido_por": COPIA,
        "visitas": visitas_en_memoria,
    })

def cotizar(request):
    try:
        km = float(request.GET.get("km"))
        kg = float(request.GET.get("kg"))
    except (TypeError, ValueError):
        return JsonResponse(
            {"error": "km y kg son obligatorios y deben ser numeros"},
            status=400,
        )

    if not (math.isfinite(km) and math.isfinite(kg)) or km < 0 or kg < 0:
        return JsonResponse(
            {"error": "km y kg deben ser numeros positivos"},
            status=400,
        )

    medio, motivo = elegir_medio(km, kg)
    return JsonResponse({"km": km, "kg": kg, "medio": medio, "motivo": motivo})
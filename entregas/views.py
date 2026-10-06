import socket
import math

from .reglas import elegir_medio
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import UltimoFolio

COPIA = socket.gethostname()

visitas_en_memoria = 0
ultimo_folio_en_memoria = None

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

def cliente(request):
    return render(request, "entregas/cliente.html")


def _leer_folio(request):
    folio = (request.GET.get("folio") or "").strip()
    if not folio or len(folio) > 50:
        return None
    return folio


ERROR_FOLIO = {"error": "folio es obligatorio (maximo 50 caracteres)"}


# Version con el error: guarda el folio en una variable global del proceso.
def ultimo_mal(request):
    global ultimo_folio_en_memoria
    folio = _leer_folio(request)
    if folio is None:
        return JsonResponse(ERROR_FOLIO, status=400)
    ultimo_folio_en_memoria = folio
    return JsonResponse({"atendido_por": COPIA, "guardado": folio})


def ultimo_ver_mal(request):
    return JsonResponse({"atendido_por": COPIA, "folio": ultimo_folio_en_memoria})


# Version arreglada: el folio vive en la base de datos, que comparten todas las copias.
def ultimo(request):
    folio = _leer_folio(request)
    if folio is None:
        return JsonResponse(ERROR_FOLIO, status=400)
    UltimoFolio.objects.update_or_create(pk=1, defaults={"folio": folio})
    return JsonResponse({"atendido_por": COPIA, "guardado": folio})


def ultimo_ver(request):
    registro = UltimoFolio.objects.filter(pk=1).first()
    return JsonResponse({
        "atendido_por": COPIA,
        "folio": registro.folio if registro else None,
    })

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from .reglas import es_posible

RUTA_MODELO = Path(__file__).resolve().parent / "modelo" / "modelo_medios.joblib"

CAMPOS_NUMERICOS = [
    "distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm", "volumen_l",
    "fragil", "refrigerado", "valor_declarado_mxn", "hora_salida",
]
CAMPOS_TEXTO = ["prioridad", "zona_destino", "clima", "trafico"]
CAMPOS = CAMPOS_NUMERICOS + CAMPOS_TEXTO


@dataclass(frozen=True)
class Sugerencia:
    medio: str
    motivo: str


class RecomendadorIA(ABC):
    @abstractmethod
    def sugerir(self, paquete: dict) -> Sugerencia:
        pass


class RecomendadorArbol(RecomendadorIA):
    """El modelo responde probabilidades; la plataforma solo entiende Sugerencia."""

    def __init__(self, ruta=RUTA_MODELO):
        self._modelo = joblib.load(ruta)

    def sugerir(self, paquete):
        datos = pd.DataFrame([paquete], columns=CAMPOS)
        probabilidades = self._modelo.predict_proba(datos)[0]
        ranking = sorted(zip(self._modelo.classes_, probabilidades), key=lambda par: -par[1])
        preferido = ranking[0][0]

        for medio, confianza in ranking:
            if es_posible(medio, paquete):
                motivo = f"árbol de decisión, confianza {confianza:.0%}"
                if medio != preferido:
                    motivo += f"; se descartó {preferido} por las reglas del negocio"
                return Sugerencia(medio, motivo)
        return Sugerencia("camioneta", "ningún medio sugerido era posible")


@lru_cache(maxsize=1)
def obtener_recomendador() -> RecomendadorIA:
    return RecomendadorArbol()
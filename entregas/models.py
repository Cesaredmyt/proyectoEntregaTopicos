from django.db import models


class UltimoFolio(models.Model):
    """Guarda el ultimo folio consultado en la base de datos (compartida por todas las copias)."""

    folio = models.CharField(max_length=50)
    consultado_en = models.DateTimeField(auto_now=True)

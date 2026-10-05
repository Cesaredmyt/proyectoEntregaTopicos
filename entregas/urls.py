from django.urls import path
from . import views

urlpatterns = [
    path("hola/", views.hola, name="hola"),
    path("estado/", views.estado, name="estado"),
    path("visitas/", views.visitas, name="visitas"),
    path("visitas-mal/", views.visitas_mal, name="visitas_mal"),
]

from django.urls import path
from . import views

urlpatterns = [
    path("hola/", views.hola, name="hola"),
    path("estado/", views.estado, name="estado"),
    path("visitas/", views.visitas, name="visitas"),
    path("visitas-mal/", views.visitas_mal, name="visitas_mal"),
    path("cotizar/", views.cotizar, name="cotizar"),
    path("cliente/", views.cliente, name="cliente"),
    path("ultimo-mal/", views.ultimo_mal, name="ultimo_mal"),
    path("ultimo-mal/ver/", views.ultimo_ver_mal, name="ultimo_ver_mal"),
    path("ultimo/", views.ultimo, name="ultimo"),
    path("ultimo/ver/", views.ultimo_ver, name="ultimo_ver"),
]

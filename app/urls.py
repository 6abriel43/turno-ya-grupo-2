"""Rutas públicas de la aplicación principal."""

from django.urls import path
from . import views
from .views import TurnoCreateView

app_name = "app"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("medicos/", views.ListaMedicosView.as_view(), name="lista_medicos"),
    # TODO:
    path('turno/nuevo/', TurnoCreateView.as_view(), name='crear_turno'),

    path('ausencias/', views.AusenciaListView.as_view(), name='lista_ausencias'),
    path('recordatorios/', views.RecordatorioListView.as_view(), name='lista_recordatorios'),
    # path("medicos/<int:pk>/", views.DetalleMedicoView.as_view(), name="detalle_medico"),
    # path("turnos/", views.ListaTurnosView.as_view(), name="lista_turnos"),
    # path("turnos/<int:pk>/cancelar/", views.CancelarTurnoView.as_view(), name="cancelar_turno"),
]

   
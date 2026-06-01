"""Rutas públicas de la aplicación principal."""

from django.urls import path
from . import views
from .views import ListaMedicosView, TurnoCreateView, DetalleMedicoView, ListaPacientesView

app_name = "app"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("medicos/", ListaMedicosView.as_view(), name="lista_medicos"),
    path("medicos/<int:pk>/", DetalleMedicoView.as_view(), name="detalle_medico"),
    path("pacientes/", ListaPacientesView.as_view(), name="lista_pacientes"),
    path('turnos/nuevo/', TurnoCreateView.as_view(), name='crear_turno'),
    path('turnos/', views.ListaTurnosView.as_view(), name='lista_turnos'),
    path('turnos/<int:pk>/cancelar/', views.CancelarTurnoView.as_view(), name='cancelar_turno'),
    path('ausencias/', views.AusenciaListView.as_view(), name='lista_ausencias'),
    path('recordatorios/', views.RecordatorioListView.as_view(), name='lista_recordatorios'),
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro'),
]    

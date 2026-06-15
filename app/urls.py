"""Rutas publicas de la aplicacion principal."""

from django.urls import path

from . import views

app_name = "app"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("medicos/", views.ListaMedicosView.as_view(), name="lista_medicos"),
    path("medicos/<int:pk>/", views.DetalleMedicoView.as_view(), name="detalle_medico"),
    path("pacientes/", views.ListaPacientesView.as_view(), name="lista_pacientes"),
    path("pacientes/<int:paciente_id>/historial/", views.HistorialPacienteListView.as_view(), name="historial_paciente"),
    path("turno/nuevo/", views.TurnoCreateView.as_view(), name="crear_turno"),
    path("turnos/", views.ListaTurnosView.as_view(), name="lista_turnos"),
    path("turnos/<int:pk>/cancelar/", views.CancelarTurnoView.as_view(), name="cancelar_turno"),
    path("turnos/<int:pk>/observacion/", views.ObservacionUpdateView.as_view(), name="editar_observacion"),
    path("ausencias/", views.AusenciaListView.as_view(), name="lista_ausencias"),
    path("recordatorios/", views.RecordatorioListView.as_view(), name="lista_recordatorios"),
    path("registro/", views.RegistroUsuarioView.as_view(), name="registro"),
]

"""Rutas raiz del proyecto y delegacion hacia la app principal."""

from django.contrib import admin
from django.urls import include, path

from app import views as app_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", app_views.HomeView.as_view(), name="home"),
    path("ausencias/", app_views.AusenciaListView.as_view(), name="lista_ausencias"),
    path("recordatorios/", app_views.RecordatorioListView.as_view(), name="lista_recordatorios"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("app.urls", namespace="app")),
]

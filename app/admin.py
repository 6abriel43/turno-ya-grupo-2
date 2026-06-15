"""Configuracion basica del admin para los modelos de la app."""

from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Medico, Paciente, Turno


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "matricula", "especialidad", "obra_social")
    list_filter = ("especialidad", "obra_social")
    search_fields = ("nombre", "apellido", "matricula")

    def save_model(self, request, obj, form, change):
        errores = obj.validate()
        if errores:
            raise ValidationError(errores)

        if obj.nombre:
            obj.nombre = obj.nombre.strip()
        if obj.apellido:
            obj.apellido = obj.apellido.strip()
        if obj.matricula:
            obj.matricula = obj.matricula.strip()

        super().save_model(request, obj, form, change)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "dni", "email", "telefono")
    list_filter = ("obra_social",)
    search_fields = ("nombre", "apellido", "dni", "email")

    def save_model(self, request, obj, form, change):
        errores = obj.validate()
        if errores:
            raise ValidationError(errores)

        if obj.nombre:
            obj.nombre = obj.nombre.strip()
        if obj.apellido:
            obj.apellido = obj.apellido.strip()
        if obj.dni:
            obj.dni = obj.dni.strip()
        if obj.email:
            obj.email = obj.email.strip()
        if obj.telefono:
            obj.telefono = obj.telefono.strip()

        super().save_model(request, obj, form, change)


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ("fecha_hora", "medico", "paciente", "estado")
    list_filter = ("estado", "medico", "fecha_hora")
    search_fields = (
        "motivo",
        "paciente__nombre",
        "paciente__apellido",
        "medico__nombre",
        "medico__apellido",
    )

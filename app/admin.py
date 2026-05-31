"""Configuración básica del admin para los modelos de la app."""

from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Medico, Paciente

# TODO: reemplazar por @admin.register con list_display, list_filter, search_fields

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    # 1. list_display: Define las columnas visibles en la tabla principal
    list_display = ('apellido', 'nombre', 'matricula', 'especialidad', 'obra_social')
    
    # 2. list_filter: Crea un panel lateral derecho para filtrar registros
    list_filter = ('especialidad', 'obra_social')
    
    # 3. search_fields: Agrega una barra de búsqueda superior (busca coincidencias parciales)
    search_fields = ('apellido', 'nombre', 'matricula')

    # 4. Patrón de negocio
    def save_model(self, request, obj, form, change):
        """
        Sobrescribimos el método de guardado nativo del Admin para forzar
        que pase por nuestra validación de negocio antes de tocar la base de datos.
        """
        errores = obj.validate()
        if errores:
            # Si el validate devuelve errores, abortamos la transacción
            raise ValidationError(errores)
        
        if obj.nombre: obj.nombre = obj.nombre.strip()
        if obj.apellido: obj.apellido = obj.apellido.strip()
        if obj.matricula: obj.matricula = obj.matricula.strip()
        
        super().save_model(request, obj, form, change)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'dni', 'obra_social', 'telefono')
    list_filter = ('obra_social',)
    search_fields = ('apellido', 'nombre', 'dni')

    def save_model(self, request, obj, form, change):
        errores = obj.validate()
        if errores:
            raise ValidationError(errores)
        
        if obj.nombre: obj.nombre = obj.nombre.strip()
        if obj.apellido: obj.apellido = obj.apellido.strip()
        if obj.dni: obj.dni = obj.dni.strip()
        if obj.email: obj.email = obj.email.strip()
        if obj.telefono: obj.telefono = obj.telefono.strip()
        
        super().save_model(request, obj, form, change)
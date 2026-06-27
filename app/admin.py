"""Configuracion basica del admin para los modelos de la app."""

from django.contrib import admin
from .models import Turno, Medico, Paciente, Ausencia, Especialidad, ObraSocial, Recordatorio, FranjaHoraria

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_hora', 'medico', 'paciente', 'estado')
    list_filter = ('estado', 'medico', 'fecha_hora')
    search_fields = ('paciente__dni', 'paciente__apellido', 'medico__apellido')
    date_hierarchy = 'fecha_hora'

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'apellido', 'nombre', 'especialidad', 'cantidad_turnos')
    list_filter = ('especialidad', 'obra_social')
    search_fields = ('apellido', 'matricula')

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('dni', 'apellido', 'nombre', 'obra_social', 'telefono')
    search_fields = ('dni', 'apellido')

@admin.register(Ausencia) 
class AusenciaAdmin(admin.ModelAdmin):
    list_display = ('medico', 'motivo', 'fecha_inicio', 'fecha_fin')
    list_filter = ('medico', 'fecha_inicio')
    search_fields = ('medico__apellido', 'motivo')
    date_hierarchy = 'fecha_inicio'

@admin.register(Especialidad)  
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(ObraSocial)  
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sigla')
    search_fields = ('nombre', 'sigla')
    list_filter = ('nombre',)

@admin.register(Recordatorio)  
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = ('id', 'turno', 'asunto', 'fecha_envio', 'leido')
    list_filter = ('leido', 'fecha_envio', 'tipo')
    search_fields = ('asunto', 'turno__paciente__apellido')
    date_hierarchy = 'fecha_envio'
    readonly_fields = ('fecha_envio',)  

@admin.register(FranjaHoraria)  
class FranjaHorariaAdmin(admin.ModelAdmin):
    list_display = ('dia', 'hora_inicio', 'hora_fin', 'duracion_en_minutos')
    list_filter = ('dia',)
    filter_horizontal = ('medicos',) 

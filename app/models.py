"""Modelos de dominio de TurnoYa."""

from __future__ import annotations
from django.db import models
from django.utils import timezone

class Medico(models.Model):
    """Representa a un profesional médico disponible para turnos."""

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100)

    class Meta:
        ordering = ["apellido", "nombre"]

    def __str__(self):
        """Retorna una etiqueta legible para listados y admin."""
        return f"Dr/a. {self.apellido}, {self.nombre}"

    def nombre_completo(self):
        """Retorna nombre y apellido concatenados."""
        return f"{self.nombre} {self.apellido}"

    def cantidad_turnos(self):
        """Retorna la cantidad total de turnos asociados a este médico."""
        if not hasattr(self, "turno_set"):
            return 0
        return self.turno_set.count()

    @classmethod
    def validate(cls, nombre, apellido, matricula, especialidad):
        """
        Valida los datos del médico. Retorna una lista de errores.
        Si la lista está vacía, los datos son válidos.
        """
        errors = []

        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")

        if not apellido or not apellido.strip():
            errors.append("El apellido es obligatorio.")

        if not matricula or not matricula.strip():
            errors.append("La matrícula es obligatoria.")

        if not especialidad or not especialidad.strip():
            errors.append("La especialidad es obligatoria.")

        return errors

    @classmethod
    def new(cls, nombre, apellido, matricula, especialidad):
        """
        Crea y persiste un nuevo médico si los datos son válidos.
        Retorna (instancia, errors). Si hay errores, instancia es None.
        """
        errors = cls.validate(nombre, apellido, matricula, especialidad)
        if errors:
            return None, errors

        medico = cls.objects.create(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            matricula=matricula.strip(),
            especialidad=especialidad.strip(),
        )
        return medico, []

    def update(self, nombre, apellido, matricula, especialidad):
        """
        Actualiza los datos del médico si los datos son válidos.
        Retorna una lista de errores. Si está vacía, la actualización fue exitosa.
        """
        errors = self.__class__.validate(nombre, apellido, matricula, especialidad)
        if errors:
            return errors

        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.matricula = matricula.strip()
        self.especialidad = especialidad.strip()
        self.save()
        return []

    # TODO: Agregar los siguientes modelos:
    # class Especialidad(models.Model): ...  ← extraer especialidad a FK
    # class Paciente(models.Model): ...
        
    #FALTA IMPLEMENTAR ClinicaManager()    
    """MODELO TURNO"""
class Turno(models.Model):
    """Representa a un profesional médico disponible para turnos."""
    fecha_hora = models.DateTimeField()
    motivo = models.CharField(max_length=255, blank=True, default="")
    estado = models.CharField(max_length=20, default="PENDIENTE")
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name="turnos")
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="turnos")
    objects = models.Manager()
    analitica = ClinicaManager()

    class Meta:
        ordering = ["fecha_hora"]
        verbose_name_plural = "turnos"
    
    def __str__(self) -> str:
        return f"Turno: {self.fecha_hora} - Paciente: {self.paciente.apellido}"
    
    def validate(self) -> list[str]:
        errors = []
        if not self.fecha_hora or not self.medico or not self.paciente:
            errors.append("Datos incompletos.")
        if self.fecha_hora and self.fecha_hora < timezone.now():
            errors.append("No se pueden solicitar turnos en fechas pasadas.")
        return errors
    
    @classmethod
    def new(cls, **kwargs) -> tuple[Turno | None, list[str]]:
        instancia = cls(**kwargs)
        errors = instancia.validate()
        if errors: 
            return None, errors
        instancia.save()
        return instancia, []
    
    def update(self, **kwargs) -> list[str]:
        for key, value in kwargs.items(): setattr(self, key, value)
        errors = self.validate()
        if errors: return errors
        self.save()
        return []
    
    """METODOS PARA CANCELAR/ACEPTAR TURNOS"""
    def cancelar(self) -> list[str]:
        """Cancela el turno actual."""
        #Regla de negocio: No cancelar si el turno ya pasó
        if self.fecha_hora < timezone.now():
            return ["No se puede cancelar un turno que ya ha finalizado."]
        self.estado = "CANCELADO"
        self.save()
        return []

    def aceptar(self) -> list[str]:
        """Acepta el turno actual."""
        #Regla de negocio: Solo pasar a aceptado si está pendiente
        if self.estado != "PENDIENTE":
            return [f"El turno no puede ser aceptado porque su estado actual es {self.estado}."]    
        self.estado = "ACEPTADO"
        self.save()
        return []


''''MODELO AUSENCIA + RECORDATORIO'''

class Ausencia(models.Model):
    """Registra las ausencias de un médico."""
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name="ausencias")
    motivo = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        ordering = ["-fecha_inicio"]
        verbose_name_plural = "Ausencias"

    def __str__(self) -> str:
        return f"Ausencia {self.medico} ({self.fecha_inicio})"

    def validate(self) -> list[str]:
        errors = []
        if not self.medico: errors.append("Médico obligatorio.")
        if not self.fecha_inicio or not self.fecha_fin or self.fecha_inicio > self.fecha_fin:
            errors.append("Fechas inválidas.")
        return errors

    @classmethod
    def new(cls, **kwargs) -> tuple[Ausencia | None, list[str]]:
        instancia = cls(**kwargs)
        errors = instancia.validate()
        if errors: return None, errors
        instancia.save()
        return instancia, []

    def update(self, **kwargs) -> list[str]:
        for key, value in kwargs.items(): setattr(self, key, value)
        errors = self.validate()
        if errors: return errors
        self.save()
        return []

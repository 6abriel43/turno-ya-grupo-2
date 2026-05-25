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
    
class Especialidad(models.Model):
    """Representa la especialidad médica (Ej: Pediatría, Cardiología)."""

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "especialidades"

    def __str__(self):
        return self.nombre
    
    @classmethod
    def validate(cls, nombre):
        """
        Validate, valida datos de la especialidad, en caso de que esté vacio
        los datos son válidos, en caso de que no, retorna una lista con errores.
        """
        errors = []
        if not nombre or not nombre.strip():
            errors.append("El nombre de la especialidad es obligatorio.")
        elif len(nombre.strip()) < 4:
            errors.append("El nombre de la especialidad debe tener al menos 4 caracteres.")
        return errors
    
    @classmethod
    def new(cls, nombre, descripcion=None):
        """
        crea la nueva especialidad si lso datos son válidos.
        la instancia es None, en caso de errores, retorna la instancia y el error.
        """
        errors = cls.validate(nombre)
        if errors:
            return None, errors
        especialidad = cls.objects.create(
            nombre=nombre.strip(),
            descripcion=descripcion.strip() if descripcion else None
        )
        return especialidad, []
    
    def update(self, nombre, descripcion=None):
        """
        si los datos son válidos, actualiza la especialidad.
        en caso de error, retorna lista de errores, caso contrario retorna lista vacia.
        """
        errors = self.__class__.validate(nombre)
        if errors:
            return errors
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip() if descripcion else None
        self.save()
        return []
    
class ObraSocial(models.Model):
    """Representa la cobertura médica del paciente (Ej: OSDE, PAMI)."""

    nombre = models.CharField(max_length=100, unique=True)
    sigla = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "obras sociales"

    def __str__(self):
        if self.sigla:
            return f"{self.sigla} - {self.nombre}"
        return self.nombre
    
    @classmethod
    def validate(cls, nombre):
        """
        Valida datos, en caso de errores retorna lista con errores
        en caso contrario, retorna lista vacia.
        """
        errors = []
        if not nombre or not nombre.strip():
            errors.append("El nombre de la obra social es obligatorio.")
        elif len(nombre.strip()) < 3:
            errors.append("El nombre de la obra social debe tener al menos 3 caracteres.")
        return errors
    
    @classmethod
    def new(cls, nombre, sigla=None):
        """
        crea la nueva obra social en caso de que los datos sean válidos
        en caso contrario retorna instancia y errores.
        """
        errors = cls.validate(nombre)
        if errors:
            return None, errors
        obra_social = cls.objects.create(
            nombre=nombre.strip(),
            sigla=sigla.strip().upper() if sigla else None
        )
        return obra_social, []
    
    def update(self, nombre, sigla=None):
        """
        en caso de que los datos son válidos, actualiza la obra social
        en caso contrario retorna lista de errores.
        """
        errors = self.__class__.validate(nombre)
        if errors:
            return errors
        self.nombre = nombre.strip()
        self.sigla = sigla.strip().upper() if sigla else None
        self.save()
        return []
"""Modelos de dominio de TurnoYa."""

from __future__ import annotations
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Medico(models.Model):
    """Representa a un profesional médico."""

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="medico")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    especialidad = models.ForeignKey('Especialidad', on_delete=models.PROTECT, related_name="medicos")
    obra_social = models.ForeignKey('ObraSocial', on_delete=models.PROTECT, related_name="medicos")

    class Meta:
        ordering = ["apellido", "nombre"]
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

    def __str__(self) -> str:
        return f"Dr/a. {self.apellido}, {self.nombre}"


    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def cantidad_turnos(self) -> int:
        """Retorna la cantidad total de turnos asociados a este médico."""
        if not hasattr(self, "turnos"):
            return 0
        return self.turnos.count()

    def validate(self) -> list[str]:
        # Valida los datos del médico, retorna una lista de errores o una lista vacía si no hay errores.
        errors = []
        if not self.usuario: errors.append("El usuario es obligatorio.")
        if not self.nombre or not self.nombre.strip(): errors.append("El nombre es obligatorio.")
        if not self.apellido or not self.apellido.strip(): errors.append("El apellido es obligatorio.")
        if not self.matricula or not self.matricula.strip(): errors.append("La matrícula es obligatoria.")
        if not self.especialidad: errors.append("La especialidad es obligatoria.")
        if not self.obra_social: errors.append("La obra social es obligatoria.")
        return errors


    @classmethod
    def new(cls, **kwargs) -> tuple[Medico | None, list[str]]:
        instancia = cls(**kwargs)
        errors = instancia.validate()
        if errors: return None, errors
        if instancia.nombre: instancia.nombre = instancia.nombre.strip()
        if instancia.apellido: instancia.apellido = instancia.apellido.strip()
        if instancia.matricula: instancia.matricula = instancia.matricula.strip()
        instancia.save()
        return instancia, []


    def update(self, **kwargs) -> list[str]:
        for key, value in kwargs.items(): setattr(self, key, value)
        errors = self.validate()
        if errors: return errors
        if self.nombre: self.nombre = self.nombre.strip()
        if self.apellido: self.apellido = self.apellido.strip()
        if self.matricula: self.matricula = self.matricula.strip()
        self.save()
        return []

    
class Paciente(models.Model):
        """Representa a un paciente."""

        usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="paciente")
        nombre = models.CharField(max_length=100)
        apellido = models.CharField(max_length=100)
        dni = models.CharField(max_length=20, unique=True)
        email = models.EmailField()
        telefono = models.CharField(max_length=20, blank=True, default="")
        obra_social = models.ForeignKey('ObraSocial', on_delete=models.PROTECT, related_name="pacientes")

        class Meta:
            ordering = ["apellido", "nombre"]
            verbose_name = "Paciente"
            verbose_name_plural = "Pacientes"

        def __str__(self) -> str:
            return f"{self.apellido}, {self.nombre}"

        def validate(self) -> list[str]:
            # Valida los datos del paciente, retorna una lista de errores o una lista vacía si no hay errores.
            errors = []
            if not self.usuario: errors.append("El usuario es obligatorio.")
            if not self.nombre or not self.nombre.strip(): errors.append("El nombre es obligatorio.")
            if not self.apellido or not self.apellido.strip(): errors.append("El apellido es obligatorio.")
            if not self.dni or not self.dni.strip(): errors.append("El DNI es obligatorio.")
            if not self.dni.isdigit(): errors.append("El DNI debe contener solo números.")
            if not self.obra_social: errors.append("La obra social es obligatoria.")
            return errors

        @classmethod
        def new(cls, **kwargs) -> tuple[Paciente | None, list[str]]:
            instancia = cls(**kwargs)
            errors = instancia.validate()
            if errors: return None, errors
            if instancia.nombre: instancia.nombre = instancia.nombre.strip()
            if instancia.apellido: instancia.apellido = instancia.apellido.strip()
            if instancia.dni: instancia.dni = instancia.dni.strip()
            if instancia.email: instancia.email = instancia.email.strip()
            if instancia.telefono: instancia.telefono = instancia.telefono.strip()
            instancia.save()
            return instancia, []

        def update(self, **kwargs) -> list[str]:
            for key, value in kwargs.items(): setattr(self, key, value)
            errors = self.validate()
            if errors: return errors
            if self.nombre: self.nombre = self.nombre.strip()
            if self.apellido: self.apellido = self.apellido.strip()
            if self.dni: self.dni = self.dni.strip()
            if self.email: self.email = self.email.strip()
            if self.telefono: self.telefono = self.telefono.strip()
            self.save()
            return []

        def obtener_nombre_completo(self) -> str:
            """Retorna el nombre completo en formato natural (Nombre Apellido)."""
            return f"{self.nombre} {self.apellido}".strip()

class FranjaHoraria(models.Model):
    """Representa un horario semanal de atencion."""

    DIAS = [
        ("LUN", "Lunes"),
        ("MAR", "Martes"),
        ("MIE", "Miercoles"),
        ("JUE", "Jueves"),
        ("VIE", "Viernes"),
        ("SAB", "Sabado"),
        ("DOM", "Domingo"),
    ]

    dia = models.CharField(max_length=3, choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    medicos = models.ManyToManyField(Medico, related_name="franjas", blank=True)

    class Meta:
        ordering = ["dia", "hora_inicio"]
        verbose_name_plural = "franjas horarias"

    def __str__(self):
        return f"{self.get_dia_display()} {self.hora_inicio} - {self.hora_fin}"

    @classmethod
    def validate(cls, dia, hora_inicio, hora_fin):
        errors = []
        dias_validos = [dia_valido[0] for dia_valido in cls.DIAS]

        if not dia:
            errors.append("El dia es obligatorio.")
        elif dia not in dias_validos:
            errors.append("El dia no es valido.")

        if not hora_inicio:
            errors.append("La hora de inicio es obligatoria.")

        if not hora_fin:
            errors.append("La hora de fin es obligatoria.")

        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            errors.append("La hora de inicio debe ser menor que la hora de fin.")

        return errors

    @classmethod
    def new(cls, dia, hora_inicio, hora_fin):
        errors = cls.validate(dia, hora_inicio, hora_fin)
        if errors:
            return None, errors

        franja = cls.objects.create(
            dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )
        return franja, []

    def update(self, dia, hora_inicio, hora_fin):
        errors = self.__class__.validate(dia, hora_inicio, hora_fin)
        if errors:
            return errors

        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.save()
        return []

    def duracion_en_minutos(self):
        minutos_inicio = self.hora_inicio.hour * 60 + self.hora_inicio.minute
        minutos_fin = self.hora_fin.hour * 60 + self.hora_fin.minute
        return minutos_fin - minutos_inicio


'''---'''
class EstadisticasClinicaQuerySet(models.QuerySet):
    def metricas_del_dia(self) -> dict:
        """Calcula en el servidor las estadísticas requeridas para la Home."""
        hoy = timezone.now().date()
        turnos_hoy = self.filter(fecha_hora__date=hoy)
        return {
            'total_turnos_hoy': turnos_hoy.count(),
            'turnos_aceptados': turnos_hoy.filter(estado="ACEPTADO").count(),
            'turnos_pendientes': turnos_hoy.filter(estado="PENDIENTE").count(),
            'total_ausencias_activas': Ausencia.objects.filter(
                fecha_inicio__lte=hoy, 
                fecha_fin__gte=hoy
            ).count()
        }

class ClinicaManager(models.Manager):
    def get_queryset(self):
        return EstadisticasClinicaQuerySet(self.model, using=self._db)

    def obtener_panel_home(self) -> dict:
        return self.get_queryset().metricas_del_dia()


    #FALTA IMPLEMENTAR ClinicaManager()    
    """MODELO TURNO"""
class Turno(models.Model):
    """Representa a un profesional médico disponible para turnos."""
    fecha_hora = models.DateTimeField()
    motivo = models.CharField(max_length=255, blank=True, default="")
    estado = models.CharField(max_length=20, default="PENDIENTE")
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name="turnos")
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="turnos")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="turnos_creados")
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

    def esta_pendiente(self) -> bool:
        return self.estado == "PENDIENTE"

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
    
    def tiene_detalles(self) -> bool:
        """Determina si la especialidad cuenta con una descripción cargada."""
        return bool(self.descripcion and self.descripcion.strip())
    
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
    
    def obtener_identificador_comercial(self) -> str:
        """Retorna la sigla si existe, de lo contrario el nombre completo."""
        return self.sigla if self.sigla else self.nombre
    
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

    def es_vigente(self) -> bool:
        """Retorna True si la ausencia está ocurriendo en el día de hoy."""
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_fin

'''---'''

class Recordatorio(models.Model):
    """Notificaciones."""
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name="recordatorios")
    fecha_envio = models.DateTimeField()
    tipo = models.CharField(max_length=50)
    usuarios = models.ManyToManyField(User, related_name="recordatorios")
    asunto = models.CharField(max_length=255)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha_envio"]
        verbose_name_plural = "Recordatorios"

    def __str__(self) -> str:
        return f"Recordatorio: {self.asunto} ({self.fecha_envio.strftime('%d/%m/%Y')})"

    def validate(self) -> list[str]:
        errors = []
        if not self.turno or not self.fecha_envio or not self.asunto:
            errors.append("Datos incompletos.")
        return errors

    @classmethod
    def new(cls, **kwargs) -> tuple[Recordatorio | None, list[str]]:
        usuarios_lista = kwargs.pop('usuarios', [])
        instancia = cls(**kwargs)
        errors = instancia.validate()
        if errors: return None, errors
        instancia.save()
        if usuarios_lista: instancia.usuarios.set(usuarios_lista)
        return instancia, []

    def update(self, **kwargs) -> list[str]:
        usuarios_lista = kwargs.pop('usuarios', None)
        for key, value in kwargs.items(): setattr(self, key, value)
        errors = self.validate()
        if errors: return errors
        self.save()
        if usuarios_lista is not None: self.usuarios.set(usuarios_lista)
        return []

    def marcar_como_leido(self) -> list[str]:
        """Método de negocio requerido por la entrega intermedia."""
        self.leido = True
        self.save()
        return []

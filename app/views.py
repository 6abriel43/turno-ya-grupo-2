"""Vistas iniciales para navegar médicos y pantalla de inicio."""

from django.views.generic import ListView, TemplateView, CreateView, View, DetailView, UpdateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from .models import Medico, Turno, Paciente, Especialidad, ObraSocial, Ausencia, Recordatorio
from django.utils import timezone
from .forms import TurnoForm, RegistroPacienteForm, PerfilMedicoForm, PerfilPacienteForm
from django.db.models import Q
from django.contrib import messages
from app.forms import AusenciaForm
from datetime import datetime, time, timedelta


class RolRequiredMixin(UserPassesTestMixin):
    """Permite el acceso a médicos, pacientes o superusuarios según el rol configurado."""
    allowed_roles = ()

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        if "medico" in self.allowed_roles and hasattr(user, "medico"):
            return True
        if "paciente" in self.allowed_roles and hasattr(user, "paciente"):
            return True
        return False

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class MedicoRequiredMixin(RolRequiredMixin):
    allowed_roles = ("medico",)

class PacienteRequiredMixin(RolRequiredMixin):
    allowed_roles = ("paciente",)

class HomeView(LoginRequiredMixin, TemplateView):
    """Vista de inicio de la clínica potenciada con las estadísticas de tu Manager."""
    template_name = "clinica/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Estadisticas de datos base:
        context['total_medicos'] = Medico.objects.count()
        context['total_pacientes'] = Paciente.objects.count()
        context['total_turnos'] = Turno.objects.count()

        try:
            context['metrics'] = Turno.analitica.obtener_panel_home()
        except AttributeError:
            context['metrics'] = {
                'total_turnos_hoy': 0,
                'turnos_aceptados': 0,
                'turnos_pendientes': 0,
                'total_ausencias_activas': 0
            }
        context['fecha_hoy'] = timezone.now().date()
        
        #Aelrtas de reprogramacion de turno para pacientes
        if hasattr(self.request.user, 'paciente'):
            context['reprogramaciones_alertas'] = Turno.objects.filter(
                paciente__usuario=self.request.user,
                estado='REPROGRAMACION_PENDIENTE'
            ).select_related('medico') #optimización select_related para evitar el problema N+1 queries al leer el apellido del médico en la alerta

        return context

class ListaMedicosView(LoginRequiredMixin, ListView):
    """Lista todos los médicos."""

    model = Medico
    template_name = "clinica/lista_medicos.html"
    context_object_name = "medicos"

    def get_queryset(self):
        """Permite filtrar por especialidad y obra social."""
        queryset = Medico.objects.select_related("especialidad", "obra_social").order_by("apellido", "nombre")
        especialidad = self.request.GET.get('especialidad')
        obra_social = self.request.GET.get('obra_social')

        if especialidad:
            queryset = queryset.filter(especialidad__id=especialidad)
        if obra_social:
            queryset = queryset.filter(obra_social__id=obra_social)

        return queryset
    
    def get_context_data(self, **kwargs):
        """Agrega al contexto las listas de especialidades y obras sociales para los filtros."""
        context = super().get_context_data(**kwargs)
        context['especialidades'] = Especialidad.objects.all().order_by("nombre")
        context['obras_sociales'] = ObraSocial.objects.all().order_by("nombre")
        context['especialidad_seleccionada'] = self.request.GET.get("especialidad", "")
        context['obra_social_seleccionada'] = self.request.GET.get("obra_social", "")
        return context
    


# TODO: implementar las siguientes vistas:
# class DetalleMedicoView(...): ...
# class ListaTurnosView(...): ...
# class NuevoTurnoView(...): ...
# class CancelarTurnoView(...): ...
# class ListaPacientesView(...): ...

class DetalleMedicoView(LoginRequiredMixin, DetailView):
    """Muestra el detalle de un médico específico."""

    model = Medico
    template_name = "clinica/detalle_medico.html"
    context_object_name = "medico"

    def get_queryset(self):
        return Medico.objects.select_related("especialidad", "obra_social").prefetch_related("franjas", "ausencias")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ausencias"] = self.object.ausencias.all().order_by("-fecha_inicio")
        return context

class ListaPacientesView(LoginRequiredMixin, MedicoRequiredMixin, ListView):
    """Lista todos los pacientes."""

    model = Paciente
    template_name = "clinica/lista_pacientes.html"
    context_object_name = "pacientes"

    def get_queryset(self):
        """Permite filtrar por DNI o apellido."""
        queryset = super().get_queryset()
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(dni__icontains=query) | Q(apellido__icontains=query)
            )

        return queryset


class HistorialPacienteListView(LoginRequiredMixin, MedicoRequiredMixin, ListView):
    model = Turno
    template_name = "clinica/historial_paciente.html"
    context_object_name = "turnos"

    def get_queryset(self):
        paciente_id = self.kwargs["paciente_id"]
        queryset = Turno.objects.select_related("paciente", "medico").filter(
            paciente_id=paciente_id,
            estado__in=["ACEPTADO", "CONFIRMADO", "FINALIZADO"],
        )
        if not self.request.user.is_superuser:
            queryset = queryset.filter(medico=self.request.user.medico)
        return queryset.order_by("-fecha_hora")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["paciente"] = get_object_or_404(Paciente, pk=self.kwargs["paciente_id"])
        return context


class ObservacionUpdateView(LoginRequiredMixin, MedicoRequiredMixin, UpdateView):
    model = Turno
    fields = ["observaciones"]
    template_name = "clinica/observacion_form.html"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Turno.objects.all()
        return Turno.objects.filter(medico=self.request.user.medico)

    def get_success_url(self):
        return reverse("app:historial_paciente", kwargs={"paciente_id": self.object.paciente_id})


class TurnoCreateView(LoginRequiredMixin, PacienteRequiredMixin, CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'clinica/turno_form.html'
    success_url = reverse_lazy('app:mis_turnos') 

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.paciente = self.request.user.paciente
        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        #asignamos automaticamente quien creo el turno
        form.instance.paciente = self.request.user.paciente
        return super().form_valid(form)

class ListaTurnosView(LoginRequiredMixin, MedicoRequiredMixin, ListView):
    model = Turno
    template_name = "clinica/lista_turnos.html"
    context_object_name = "turnos"

    def get_queryset(self):
        queryset = Turno.objects.select_related('medico', 'paciente').order_by('-fecha_hora')
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(medico=self.request.user.medico)   

class MisTurnosView(LoginRequiredMixin, PacienteRequiredMixin, ListView):
    model = Turno
    template_name = "clinica/lista_turnos.html"
    context_object_name = "turnos"

    def get_queryset(self):
        return Turno.objects.filter(paciente=self.request.user.paciente).order_by('-fecha_hora')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Mis turnos'
        context['subtitulo'] = 'Aquí verás los turnos que solicitaste.'
        return context

class AceptarTurnoView(LoginRequiredMixin, MedicoRequiredMixin, View):
    """Acepta un turno pendiente desde la vista del médico."""

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk)
        if not request.user.is_superuser and turno.medico != request.user.medico:
            raise PermissionDenied

        errors = turno.aceptar()
        if errors:
            messages.error(request, errors[0])
        else:
            messages.success(request, "Turno aceptado correctamente.")

        return redirect("app:lista_turnos")


class CancelarTurnoView(LoginRequiredMixin, PacienteRequiredMixin, View):
    """Cancela un turno dado su pk mediante POST."""

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, paciente__usuario=request.user)
        errors = turno.cancelar()

        if errors:
            messages.error(request, errors[0])
            return redirect("app:home")

        messages.success(request, "Turno cancelado correctamente.")
        return redirect("app:home")

'''VISTAS AUSENCIA + RECORDATORIO'''
class AusenciaListView(LoginRequiredMixin, MedicoRequiredMixin, ListView):
    """Vista para listar el historial de ausencias del personal médico."""
    model = Ausencia
    template_name = "clinica/ausencias_list.html"
    context_object_name = "lista_ausencias"
    ordering = ['-fecha_inicio']

    def get_queryset(self):
        queryset = Ausencia.objects.select_related("medico").order_by("-fecha_inicio")
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(medico=self.request.user.medico)

class RecordatorioListView(LoginRequiredMixin, MedicoRequiredMixin, ListView):
    """Vista para el panel de control y seguimiento de recordatorios."""
    model = Recordatorio
    template_name = "clinica/recordatorios_list.html"
    context_object_name = "lista_recordatorios"
    ordering = ['-fecha_envio']

    def get_queryset(self):
        queryset = Recordatorio.objects.select_related("turno", "turno__paciente", "turno__medico").order_by("-fecha_envio")
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(turno__medico=self.request.user.medico)

class RegistroUsuarioView(CreateView):
    """Vista basada en clase para el alta de nuevos usuarios en el sistema."""
    form_class = RegistroPacienteForm
    template_name = 'registro/registro.html'
    success_url = reverse_lazy('app:home')

    def form_valid(self, form):
        """Pipeline de éxito cuando el formulario pasa las validaciones."""
        return super().form_valid(form)
    
"EDITAR INFORMACION DE PERFIL DE USUARIO"
class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    """Vista inteligente para que médicos y pacientes editen su propio perfil."""
    template_name = 'registro/perfil.html'
    success_url = reverse_lazy('app:home')

    def get_form_class(self):
        """Elige el formulario correcto según el rol del usuario logueado."""
        if hasattr(self.request.user, 'medico'):
            return PerfilMedicoForm
        return PerfilPacienteForm

    def get_object(self, queryset=None):
        """Retorna el objeto (Medico o Paciente) que corresponde al usuario actual."""
        if self.request.user.is_superuser:
            raise PermissionDenied
        if hasattr(self.request.user, 'medico'):
            return self.request.user.medico
        return self.request.user.paciente
    
class AusenciaCreateView(LoginRequiredMixin, MedicoRequiredMixin, CreateView):
    model = Ausencia
    form_class = AusenciaForm
    template_name = 'clinica/ausencia_form.html'
    success_url = reverse_lazy('app:home')

    def form_valid(self, form):
        if not hasattr(self.request.user, 'medico') and not self.request.user.is_superuser:
            raise PermissionDenied
        if hasattr(self.request.user, 'medico'):
            form.instance.medico = self.request.user.medico
        response = super().form_valid(form)
        
        #REPROGRAMACIÓN AUTOMÁTICA 
        #Buscamos turnos del médico que caigan en ese rango de fechas
        from django.utils import timezone
        inicio_dt = timezone.make_aware(datetime.combine(self.object.fecha_inicio, time.min))
        fin_dt = timezone.make_aware(datetime.combine(self.object.fecha_fin, time.max))
        
        turnos_afectados = Turno.objects.filter(
            medico=self.object.medico,
            fecha_hora__range=(inicio_dt, fin_dt)
        ).exclude(estado='CANCELADO')
        for turno in turnos_afectados:
            turno.estado = 'REPROGRAMACION_PENDIENTE'
            # Propuesta automatizada base: Se mueve el turno exactamente 1 semana más adelante
            turno.nueva_fecha_hora = turno.fecha_hora + timedelta(days=7)
            turno.save()
            
        messages.success(self.request, f"Ausencia registrada. Se han afectado {turnos_afectados.count()} turnos para reprogramación.")
        return response

class MisRecordatoriosView(LoginRequiredMixin, ListView):
    """Bandeja de entrada para que el paciente autenticado visualice sus recordatorios."""
    model = Recordatorio
    template_name = 'clinica/recordatorios_list.html'
    context_object_name = 'lista_recordatorios'

    def get_queryset(self):
        return Recordatorio.objects.filter(turno__paciente__usuario=self.request.user).order_by('-fecha_envio')
    
class MarcarRecordatorioLeidoView(LoginRequiredMixin, View):
    """Acción POST para mutar el estado de lectura del recordatorio de manera segura."""
    
    def post(self, request, pk):
        recordatorio = get_object_or_404(Recordatorio, pk=pk, turno__paciente__usuario=request.user)
        recordatorio.marcar_como_leido()
        return redirect('app:mis_recordatorios')

class ProcesarReprogramacionView(LoginRequiredMixin, PacienteRequiredMixin, View):
    """Maneja la aceptación/rechazo de reprogramaciones de turnos."""

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, paciente__usuario=request.user)
        accion = request.POST.get('accion')
        
        if accion == 'aceptar' and turno.nueva_fecha_hora:
            turno.fecha_hora = turno.nueva_fecha_hora
            turno.nueva_fecha_hora = None
            turno.estado = 'CONFIRMADO'
            turno.save()

            Recordatorio.new(
                turno=turno,
                fecha_envio=timezone.now(),
                tipo="SISTEMA",
                asunto="Reprogramación Aceptada",
                mensaje=f"Tu turno ha sido reprogramado para el {turno.fecha_hora.strftime('%d/%m/%Y %H:%M')} hs.",
                usuarios=[request.user]
            )

            messages.success(
                request,
                f"Ha aceptado la reprogramación del turno con éxito para {turno.fecha_hora.strftime('%d/%m/%Y %H:%M')}."
            )

        elif accion == 'rechazar':
            turno.nueva_fecha_hora = None
            turno.estado = 'CANCELADO'
            turno.save()
            
            Recordatorio.new(
                turno=turno,
                fecha_envio=timezone.now(),
                tipo="SISTEMA",
                asunto="Reprogramación Rechazada",
                mensaje=f"El paciente rechazó la reprogramación. Se mantiene el turno original: {turno.fecha_hora.strftime('%d/%m/%Y %H:%M')}",
                usuarios=[turno.medico.usuario]
            )

            messages.info(
                request,
                "Ha rechazado la reprogramación. Se mantiene tu turno original."
            )

        else:
            messages.error(request, "Acción no válida o turno sin reprogramación pendiente.")

        return redirect("app:home")

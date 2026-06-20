"""Vistas iniciales para navegar médicos y pantalla de inicio."""

from django.views.generic import ListView, TemplateView, CreateView, View, DetailView, UpdateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from .models import Medico, Turno, Paciente
from django.utils import timezone
from .forms import TurnoForm, RegistroPacienteForm, PerfilMedicoForm, PerfilPacienteForm
from django.db.models import Q
from django.contrib import messages
from app.models import Ausencia, Turno, Recordatorio
from app.forms import AusenciaForm
from datetime import datetime, time


class MedicoRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # solo los usuarios medicos pueden entrar
        return hasattr(self.request.user, "medico")

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class HomeView(LoginRequiredMixin, TemplateView):
    """Vista de inicio de la clínica potenciada con las estadísticas de tu Manager."""
    template_name = "clinica/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Estadisticas de datos base:
        context['total_medicos'] = Medico.objects.count()
        context['total_pacientes'] = Paciente.objects.count()
        context['total_turnos'] = Turno.objects.count()


        # Importación local para evitar importes circulares entre archivos
        from .models import Turno 
        
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
        queryset = super().get_queryset()
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
        from .models import Especialidad, ObraSocial
        context['especialidades'] = Especialidad.objects.all()
        context['obras_sociales'] = ObraSocial.objects.all()
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

class ListaPacientesView(LoginRequiredMixin, ListView):
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
        return Turno.objects.select_related("paciente", "medico").filter(
            paciente_id=paciente_id,
            medico=self.request.user.medico,
            estado__in=["ACEPTADO", "CONFIRMADO", "FINALIZADO"],
        ).order_by("-fecha_hora")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["paciente"] = get_object_or_404(Paciente, pk=self.kwargs["paciente_id"])
        return context


class ObservacionUpdateView(LoginRequiredMixin, MedicoRequiredMixin, UpdateView):
    model = Turno
    fields = ["observaciones"]
    template_name = "clinica/observacion_form.html"

    def get_queryset(self):
        return Turno.objects.filter(medico=self.request.user.medico)

    def get_success_url(self):
        return reverse("app:historial_paciente", kwargs={"paciente_id": self.object.paciente_id})


class TurnoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'clinica/turno_form.html'
    success_url = reverse_lazy('app:lista_turnos') 

    def test_func(self):
        #Verifica en tiempo real que el usuario logueado sea un Paciente.
        return hasattr(self.request.user, 'paciente')

    def form_valid(self, form):
        #asignamos automaticamente quien creo el turno
        form.instance.creado_por = self.request.user
        return super().form_valid(form)

class ListaTurnosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Turno
    template_name = "clinica/lista_turnos.html"
    context_object_name = "turnos"

    def test_func(self):
        #Verifica en tiempo real que el usuario logueado sea un Médico."""
        return hasattr(self.request.user, 'medico')

    def get_queryset(self):
        # Ordenamos los turnos mostrando los más recientes primero
        return Turno.objects.all().order_by('-fecha_hora')   

class CancelarTurnoView(LoginRequiredMixin, View):
    """Cancela un turno dado su pk mediante POST."""

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk)
        turno.cancelar()
        return redirect('app:lista_turnos')


'''VISTAS AUSENCIA + RECORDATORIO'''
class AusenciaListView(LoginRequiredMixin, ListView):
    """Vista para listar el historial de ausencias del personal médico."""
    from .models import Ausencia
    model = Ausencia
    template_name = "clinica/ausencias_list.html"
    context_object_name = "lista_ausencias"
    ordering = ['-fecha_inicio']

class RecordatorioListView(LoginRequiredMixin, ListView):
    """Vista para el panel de control y seguimiento de recordatorios."""
    from .models import Recordatorio
    model = Recordatorio
    template_name = "clinica/recordatorios_list.html"
    context_object_name = "lista_recordatorios"
    ordering = ['-fecha_envio']

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
        if hasattr(self.request.user, 'medico'):
            return self.request.user.medico
        # Si no es médico, asumimos que es paciente (o tirará error si es admin puro)
        return self.request.user.paciente
    
class AusenciaCreateView(LoginRequiredMixin, CreateView):
    model = Ausencia
    form_class = AusenciaForm
    template_name = 'clinica/ausencia_form.html'
    success_url = reverse_lazy('app:home')

    def form_valid(self, form):
        # Asignamos al médico logueado(Se asume la relación OneToOne con User)
        form.instance.medico = self.request.user.medico
        response = super().form_valid(form)
        
        #REPROGRAMACIÓN AUTOMÁTICA 
        #Buscamos turnos del médico que caigan en ese rango de fechas
        inicio_dt = datetime.combine(self.object.fecha_inicio, time.min)
        fin_dt = datetime.combine(self.object.fecha_fin, time.max)
        
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

class ProcesarReprogramacionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, paciente__usuario=request.user)
        accion = request.POST.get('accion')
        
        if accion == 'aceptar' and turno.nueva_fecha_hora:
            turno.fecha_hora = turno.nueva_fecha_hora
            turno.nueva_fecha_hora = None
            turno.estado = 'CONFIRMADO'
            turno.save()
            messages.success(request, "Ha aceptado la reprogramación del turno con éxito.")
        elif accion == 'rechazar':
            turno.estado = 'CANCELADO'
            turno.nueva_fecha_hora = None
            turno.save()
            messages.warning(request, "Ha rechazado la propuesta. El turno fue cancelado.")
            
        return redirect('app:home')
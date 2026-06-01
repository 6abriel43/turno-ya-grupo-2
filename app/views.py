"""Vistas iniciales para navegar médicos y pantalla de inicio."""

from django.views.generic import ListView, TemplateView, CreateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Medico, Turno, Paciente
from .forms import TurnoForm #formulario hecho en forms.py
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

class HomeView(TemplateView):
    """Vista de inicio de la clínica potenciada con las estadísticas de tu Manager."""
    template_name = "clinica/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

class DetalleMedicoView(LoginRequiredMixin, TemplateView):
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


class TurnoCreateView(LoginRequiredMixin, CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'clinica/turno_form.html'
    success_url = reverse_lazy('lista_turnos') # Cambia 'lista_turnos' por el nombre de URL de listado

    def form_valid(self, form):
        # Opcional: imprimir en consola para debug como pide la guía avanzada
        print(f"Se está creando un turno para el médico: {form.cleaned_data['medico']}")
        return super().form_valid(form)
    

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
    form_class = UserCreationForm
    template_name = 'registration/registro.html'
    success_url = reverse_lazy('app:home')

    def form_valid(self, form):
        """Pipeline de éxito cuando el formulario pasa las validaciones."""
        response = super().form_valid(form)
        return response

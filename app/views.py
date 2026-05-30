"""Vistas iniciales para navegar médicos y pantalla de inicio."""

from django.views.generic import ListView, TemplateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Medico, Turno
from .forms import TurnoForm #formulario hecho en forms.py
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm

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

class ListaMedicosView(ListView):
    """Lista todos los médicos."""

    model = Medico
    template_name = "clinica/lista_medicos.html"
    context_object_name = "medicos"


# TODO: implementar las siguientes vistas:
# class DetalleMedicoView(...): ...
# class ListaTurnosView(...): ...
# class NuevoTurnoView(...): ...
# class CancelarTurnoView(...): ...
# class ListaPacientesView(...): ...

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
class AusenciaListView(ListView):
    """Vista para listar el historial de ausencias del personal médico."""
    from .models import Ausencia
    model = Ausencia
    template_name = "clinica/ausencias_list.html"
    context_object_name = "lista_ausencias"
    ordering = ['-fecha_inicio']

class RecordatorioListView(ListView):
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
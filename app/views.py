"""Vistas iniciales para navegar médicos y pantalla de inicio."""

from django.views.generic import ListView, TemplateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Medico, Turno
from .forms import TurnoForm #formulario hecho en forms.py

class HomeView(TemplateView):
    """Vista de inicio. Por ahora vacía — completar con estadísticas."""

    template_name = "clinica/home.html"


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
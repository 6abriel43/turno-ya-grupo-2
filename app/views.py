"""Vistas iniciales para navegar medicos y pantalla de inicio."""

from django.views.generic import ListView, TemplateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Medico, Turno
from .forms import TurnoForm #formulario hecho en forms.py

class HomeView(TemplateView):
    """Vista de inicio con estadisticas generales."""

    template_name = "clinica/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_medicos"] = Medico.objects.count()
        context["total_turnos"] = Turno.objects.count()
        context["turnos_pendientes"] = Turno.objects.filter(estado="PENDIENTE").count()
        context["turnos_aceptados"] = Turno.objects.filter(estado="ACEPTADO").count()
        return context


class ListaMedicosView(LoginRequiredMixin, ListView):
    """Lista medicos con filtro por especialidad."""

    model = Medico
    template_name = "clinica/lista_medicos.html"
    context_object_name = "medicos"

    def get_queryset(self):
        medicos = Medico.objects.all().order_by("apellido", "nombre")
        especialidad = self.request.GET.get("especialidad", "")

        if especialidad:
            medicos = medicos.filter(especialidad=especialidad)

        return medicos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["especialidades"] = (
            Medico.objects.exclude(especialidad="")
            .values_list("especialidad", flat=True)
            .distinct()
            .order_by("especialidad")
        )
        context["especialidad_seleccionada"] = self.request.GET.get("especialidad", "")
        return context


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
        # comentario simple para debug
        print(f"Se esta creando un turno para el medico: {form.cleaned_data['medico']}")
        return super().form_valid(form)

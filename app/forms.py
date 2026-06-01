from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Turno


class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ["medico", "paciente", "fecha_hora", "motivo"]
        widgets = {
            "fecha_hora": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "medico": forms.Select(attrs={"class": "form-select"}),
            "paciente": forms.Select(attrs={"class": "form-select"}),
            "motivo": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha_hora")
        medico = cleaned_data.get("medico")

        # validacion 1: fecha pasada
        if fecha and fecha < timezone.now():
            raise forms.ValidationError("No se pueden solicitar turnos en fechas pasadas.")

        # validacion 2: medico ocupado
        if fecha and medico:
            fecha_formulario = self.data.get("fecha_hora")
            inicio_minuto = fecha.replace(second=0, microsecond=0)
            fin_minuto = inicio_minuto + timedelta(minutes=1)

            turno_ocupado = Turno.objects.filter(
                medico=medico,
                fecha_hora__gte=inicio_minuto,
                fecha_hora__lt=fin_minuto,
                estado="ACEPTADO",
            ).exists()

            if not turno_ocupado and fecha_formulario:
                turno_ocupado = Turno.objects.filter(
                    medico=medico,
                    estado="ACEPTADO",
                ).extra(
                    where=["strftime('%%Y-%%m-%%dT%%H:%%M', fecha_hora) = %s"],
                    params=[fecha_formulario],
                ).exists()

            if turno_ocupado:
                raise forms.ValidationError(f"El Dr./a {medico.apellido} ya tiene un turno aceptado en este horario.")

        return cleaned_data

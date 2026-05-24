from django import forms
from .models import Turno, Medico
from django.utils import timezone

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['medico', 'paciente', 'fecha_hora', 'motivo']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha_hora')
        medico = cleaned_data.get('medico')
        
        #Validacion 1: Fecha pasada
        if fecha and fecha < timezone.now():
            raise forms.ValidationError("No se pueden solicitar turnos en fechas pasadas.")
        #Validación 2: Médico ocupado (Validación personalizada)
        if fecha and medico:
            if Turno.objects.filter(medico=medico, fecha_hora=fecha, estado="ACEPTADO").exists():
                raise forms.ValidationError(f"El Dr./a {medico.apellido} ya tiene un turno aceptado en este horario.")
        
        return cleaned_data
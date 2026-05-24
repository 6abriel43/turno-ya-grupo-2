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

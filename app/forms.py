from datetime import timedelta

from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Turno ,Paciente, ObraSocial, Medico


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


class RegistroPacienteForm(UserCreationForm):
    nombre = forms.CharField(max_length=100, required=True, label="Nombre")
    apellido = forms.CharField(max_length=100, required=True, label="Apellido")
    dni = forms.CharField(max_length=20, required=True, label="DNI")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono (Opcional)")
    obra_social = forms.ModelChoiceField(
        queryset=ObraSocial.objects.all(), 
        required=True, 
        label="Obra Social",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Mantenemos los campos base de usuario de Django (como el username)
        fields = UserCreationForm.Meta.fields

    def save(self, commit=True):
        # 1. Guardamos primero el usuario base en memoria sin mandarlo a la BD todavía
        user = super().save(commit=False)
        # Le pasamos el email nativo de Django si lo requiere el modelo base
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save() # Guardamos el User real en la base de datos para generar su ID
            
            # 2. Creamos AUTOMÁTICAMENTE el Paciente usando el método .new() 
            # Pasamos todos los datos requeridos por su validador interno
            Paciente.new(
                usuario=user,
                nombre=self.cleaned_data['nombre'],
                apellido=self.cleaned_data['apellido'],
                dni=self.cleaned_data['dni'],
                email=self.cleaned_data['email'],
                telefono=self.cleaned_data['telefono'],
                obra_social=self.cleaned_data['obra_social']
            )
        return user
    

class PerfilMedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['obra_social', 'especialidad']
        widgets = {
            'obra_social': forms.Select(attrs={'class': 'form-select'}),
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
        }


class PerfilPacienteForm(forms.ModelForm):
    # Agregamos el campo email de forma manual porque vive en la tabla User, no en Paciente
    email = forms.EmailField(required=True, label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Paciente
        fields = ['obra_social', 'telefono']
        widgets = {
            'obra_social': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # Este método carga el email actual del usuario en el casillero al abrir la pantalla
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.usuario:
            self.fields['email'].initial = self.instance.usuario.email

    # Este método guarda los datos del paciente y además actualiza el mail en la tabla User
    def save(self, commit=True):
        paciente = super().save(commit=False)
        if commit:
            paciente.save()
            # Accedemos al usuario vinculado y le planchamos el nuevo email
            usuario = paciente.usuario
            usuario.email = self.cleaned_data['email']
            usuario.save()
        return paciente
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Medico, Paciente, Turno
from django.utils import timezone
from datetime import timedelta

class TurnoCreateViewTest(TestCase):
    def setUp(self):
        #creamos datos necesarios para los tests
        self.user = User.objects.create_user(username='testuser', password='password')
        self.medico = Medico.objects.create(nombre="Laura", apellido="Romero", matricula="MP-9999", especialidad="Pediatría")
        self.paciente = Paciente.objects.create(nombre="Ana", apellido="Perez")
        self.client = Client()

    def test_creacion_turno_valido(self):
        self.client.login(username='testuser', password='password')
        url = reverse('crear_turno')
        data = {
            'medico': self.medico.id,
            'paciente': self.paciente.id,
            'fecha_hora': timezone.now() + timedelta(days=2),
            'motivo': 'Consulta general'
        }
        response = self.client.post(url, data)
        self.assertEqual(Turno.objects.count(), 1)
        self.assertEqual(response.status_code, 302) # Redirección tras éxito

    def test_validacion_turno_duplicado_falla(self):
        self.client.login(username='testuser', password='password')
        fecha = timezone.now() + timedelta(days=2)
        #creamos un turno ya existente
        Turno.objects.create(medico=self.medico, paciente=self.paciente, fecha_hora=fecha, estado="ACEPTADO")
        
        url = reverse('crear_turno')
        data = {
            'medico': self.medico.id,
            'paciente': self.paciente.id,
            'fecha_hora': fecha,
            'motivo': 'Otro motivo'
        }
        response = self.client.post(url, data)
        #El form debe dar inválido
        self.assertFormError(response, 'form', None, "El Dr./a Romero ya tiene un turno aceptado en este horario.")
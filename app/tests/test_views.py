from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Especialidad, Medico, ObraSocial, Paciente, Turno
from django.utils import timezone
from datetime import timedelta

class VistasTestCase(TestCase):
    def setUp(self):
        # 1. Creamos un usuario de prueba para loguearnos
        self.user = User.objects.create_user(username="admin_test", password="123")
        
        # 2. Preparamos datos base
        self.especialidad = Especialidad.objects.create(nombre="Cardiología")
        self.obra_social = ObraSocial.objects.create(nombre="OSDE")
        
        self.medico, _ = Medico.new(
            usuario=self.user, nombre="Ana", apellido="Gómez", 
            matricula="MP-111", especialidad=self.especialidad, obra_social=self.obra_social
        )
        self.paciente, _ = Paciente.new(
            usuario=User.objects.create_user(username="paciente_test", password="123"), 
            nombre="Juan", apellido="Pérez", dni="12345678", 
            obra_social=self.obra_social
        )
        
        # 3. Preparamos URLs para los tests
        self.url_medicos = reverse('app:lista_medicos') 
        self.url_pacientes = reverse('app:lista_pacientes')

    # --- Tests de Seguridad (Login) ---

    def test_vistas_protegidas_redirigen_sin_login(self):
        """Si un usuario anónimo intenta entrar, el sistema lo patea al login (HTTP 302)."""
        response_medicos = self.client.get(self.url_medicos)
        response_pacientes = self.client.get(self.url_pacientes)
        
        self.assertEqual(response_medicos.status_code, 302)
        self.assertEqual(response_pacientes.status_code, 302)

    # --- Tests de Vistas de Médicos ---

    def test_lista_medicos_con_login_carga_bien(self):
        """Un usuario logueado recibe un HTTP 200 y el template correcto."""
        self.client.login(username="admin_test", password="123")
        response = self.client.get(self.url_medicos)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clinica/lista_medicos.html")
        self.assertIn('medicos', response.context) # Verifica que inyectamos la lista
        self.assertIn('especialidades', response.context) # Verifica que mandamos las opciones del filtro

    def test_lista_medicos_filtro_por_especialidad(self):
        """Verifica que el filtrado mediante GET (?especialidad=id) funciona."""
        self.client.login(username="admin_test", password="123")
        
        # Simulamos que el usuario eligió "Cardiología" en el select y apretó buscar
        response = self.client.get(self.url_medicos, {'especialidad': self.especialidad.id})
        
        medicos_filtrados = response.context['medicos']
        self.assertEqual(medicos_filtrados.count(), 1)
        self.assertEqual(medicos_filtrados.first(), self.medico)

    # --- Tests de Vistas de Pacientes ---

    def test_lista_pacientes_con_login_carga_bien(self):
        """Un usuario logueado ve el listado de pacientes sin error."""
        self.client.login(username="admin_test", password="123")
        response = self.client.get(self.url_pacientes)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clinica/lista_pacientes.html")

    def test_lista_pacientes_buscador_por_dni(self):
        """Verifica que este filtrando correctamente."""
        self.client.login(username="admin_test", password="123")
        
        # Simulamos escribir parte del DNI en el buscador
        response = self.client.get(self.url_pacientes, {'q': '1234'})
        
        pacientes_filtrados = response.context['pacientes']
        self.assertEqual(pacientes_filtrados.count(), 1)
        self.assertEqual(pacientes_filtrados.first().apellido, "Pérez")
    

class TurnoCreateViewTest(TestCase):
    def setUp(self):
        #creamos datos necesarios para los tests
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user_med = User.objects.create_user(username='meduser', password='password')
        self.user_pac = User.objects.create_user(username='pacuser', password='password')
        self.esp = Especialidad.objects.create(nombre="Pediatría")
        self.os = ObraSocial.objects.create(nombre="OSDE")
        self.medico = Medico.objects.create(
            usuario=self.user_med,
            nombre="Laura",
            apellido="Romero",
            matricula="MP-9999",
            especialidad=self.esp,
            obra_social=self.os,
        )
        self.paciente = Paciente.objects.create(
            usuario=self.user_pac,
            nombre="Ana",
            apellido="Perez",
            dni="11111111",
            email="ana@test.com",
            obra_social=self.os,
        )
        self.client = Client()

    def test_creacion_turno_valido(self):
        self.client.login(username='testuser', password='password')
        url = reverse('app:crear_turno')
        data = {
            'medico': self.medico.id,
            'paciente': self.paciente.id,
            'fecha_hora': (timezone.now() + timedelta(days=2)).isoformat(),
            'motivo': 'Consulta general'
        }
        response = self.client.post(url, data)
        self.assertEqual(Turno.objects.count(), 1)
        self.assertEqual(response.status_code, 302) # Redirección tras éxito

    def test_validacion_turno_duplicado_falla(self):
        self.client.login(username='testuser', password='password')
        fecha = (timezone.now() + timedelta(days=2)).replace(second=0, microsecond=0)
        #creamos un turno ya existente
        Turno.objects.create(medico=self.medico, paciente=self.paciente, fecha_hora=fecha, estado="ACEPTADO")
        
        url = reverse('app:crear_turno')
        data = {
            'medico': self.medico.id,
            'paciente': self.paciente.id,
            'fecha_hora': fecha.strftime('%Y-%m-%dT%H:%M'),
            'motivo': 'Otro motivo'
        }
        response = self.client.post(url, data)

        # Si la validación falla, el status code es 200 (re-renderiza el form con errores).
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            None,
            f"El Dr./a {self.medico.apellido} ya tiene un turno aceptado en este horario."
        )

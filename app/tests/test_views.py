from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Especialidad, FranjaHoraria, Medico, ObraSocial, Paciente, Turno, Recordatorio, Ausencia
from django.utils import timezone
from datetime import timedelta, date

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
        # Franjas horarias para todos los días (requerido por Turno.validate)
        for dia in ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]:
            franja = FranjaHoraria.objects.create(dia=dia, hora_inicio="00:00", hora_fin="23:59")
            franja.medicos.add(self.medico)

    def test_creacion_turno_valido(self):
        self.client.login(username='pacuser', password='password')
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
        self.client.login(username='pacuser', password='password')
        fecha = (timezone.now() + timedelta(days=2)).replace(second=0, microsecond=0)
# creamos un turno ya existente
        Turno.objects.create(medico=self.medico, paciente=self.paciente, fecha_hora=fecha, estado="ACEPTADO")
        
        url = reverse('app:crear_turno')
        data = {
            'medico': self.medico.id,
            'paciente': self.paciente.id,
            'fecha_hora': fecha.strftime('%Y-%m-%dT%H:%M'),
            'motivo': 'Otro motivo'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            None,
            f"El Dr./a {self.medico.apellido} ya tiene un turno aceptado en este horario."
        )


class ClinicaSeguridadTests(TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas de seguridad del Integrante 1."""
        # Creamos la infraestructura mínima que piden los validadores del modelo
        self.os = ObraSocial.objects.create(nombre="OSDE", sigla="OSDE")
        self.esp = Especialidad.objects.create(nombre="Pediatría")

        # 1. Creamos un usuario Paciente de prueba
        self.user_paciente = User.objects.create_user(username="paciente_test", password="password123")
        self.paciente = Paciente.objects.create(
            usuario=self.user_paciente,
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            email="juan@test.com",
            obra_social=self.os
        )

        # 2. Creamos un usuario Médico de prueba
        self.user_medico = User.objects.create_user(username="medico_test", password="password123")
        self.medico = Medico.objects.create(
            usuario=self.user_medico,
            nombre="Dr",
            apellido="García",
            matricula="M456",
            especialidad=self.esp,
            obra_social=self.os
        )
        # Franjas horarias para todos los días (requerido por Turno.validate)
        for dia in ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]:
            franja = FranjaHoraria.objects.create(dia=dia, hora_inicio="00:00", hora_fin="23:59")
            franja.medicos.add(self.medico)

    def test_registro_paciente_combo_exitoso(self):
        """Prueba que el formulario de registro cree correctamente tanto el User como el Paciente."""
        datos_registro = {
            'username': 'nuevo_paciente',
            'password1': 'ContraSegura123',
            'password2': 'ContraSegura123',
            'nombre': 'Carlos',
            'apellido': 'Gómez',
            'dni': '87654321',
            'email': 'carlos@test.com',
            'telefono': '2901445566',
            'obra_social': self.os.id
        }
        # Mandamos el POST a la ruta de registro
        response = self.client.post(reverse('app:registro'), data=datos_registro)
        
        # Verificamos que redirija al home (302) y que el paciente exista en la BD
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Paciente.objects.filter(dni='87654321').exists())

    def test_paciente_no_puede_ver_lista_turnos_medico(self):
        """Prueba que un Paciente sea REBOTADO (403) al intentar entrar a la lista de turnos de médicos."""
        # Logueamos al paciente de prueba
        self.client.login(username="paciente_test", password="password123")
        
        # Intentamos ir a la lista de turnos reservada para médicos
        response = self.client.get(reverse('app:lista_turnos'))
        
        # Verificamos que el candado UserPassesTestMixin lo frene con un 403 (Prohibido)
        self.assertEqual(response.status_code, 403)

    def test_auto_generacion_recordatorio_al_crear_turno(self):
        """Verifica que al instanciar un nuevo turno se genere el recordatorio automáticamente."""
        count_antes = Recordatorio.objects.count()
        
        fecha_futura = timezone.now() + timedelta(days=5)
        turno, errors = Turno.new(
            fecha_hora=fecha_futura,
            medico=self.medico,
            paciente=self.paciente,
            motivo="Control de Rutina"
        )
        
        self.assertEqual(errors, [])
        self.assertEqual(Recordatorio.objects.count(), count_antes + 1)

        ultimo_recordatorio = Recordatorio.objects.latest('id')
        self.assertEqual(ultimo_recordatorio.turno, turno)
        self.assertEqual(ultimo_recordatorio.asunto, "Turno Creado")

    def test_auto_generacion_recordatorio_al_aceptar_turno(self):
        """Verifica que al aceptar un turno se dispare la notificación correspondiente."""
        from app.models import Recordatorio, Turno
        fecha_futura = timezone.now() + timedelta(days=3)
        turno, _ = Turno.new(fecha_hora=fecha_futura, medico=self.medico, paciente=self.paciente)
        
        count_antes = Recordatorio.objects.count()
        errors = turno.aceptar()
        
        self.assertEqual(errors, [])
        self.assertEqual(turno.estado, "ACEPTADO")
        self.assertEqual(Recordatorio.objects.count(), count_antes + 1)
        
        ultimo_recordatorio = Recordatorio.objects.latest('id')
        self.assertEqual(ultimo_recordatorio.asunto, "Turno Confirmado")

class ReprogramacionSystemTest(TestCase):
    def setUp(self):
        unique_id = id(self)
        self.user_med = User.objects.create_user(username=f"med_rep_{unique_id}", password="123")
        self.user_pac = User.objects.create_user(username=f"pac_rep_{unique_id}", password="123")
        
        self.esp = Especialidad.objects.create(nombre="Cardiología")
        self.os = ObraSocial.objects.create(nombre="OSDE")
        
        self.medico = Medico.objects.create(usuario=self.user_med, nombre="Dr. Alan", apellido="Turing", matricula="MP-77", especialidad=self.esp, obra_social=self.os)
        self.paciente = Paciente.objects.create(usuario=self.user_pac, nombre="John", apellido="Doe", dni=f"99{unique_id}"[:8], email="j@j.com", obra_social=self.os)
        
        # Turno agendado para mañana a las 10:00
        mañana = timezone.now() + timedelta(days=1)
        self.fecha_turno = mañana.replace(hour=10, minute=0, second=0, microsecond=0)
        self.turno = Turno.objects.create(fecha_hora=self.fecha_turno, medico=self.medico, paciente=self.paciente, estado='CONFIRMADO')

    def test_crear_ausencia_reprograma_turnos_automaticamente(self):
        # Logueamos al médico para simular la petición de ausencia
        self.client.login(username=self.user_med.username, password="123")
        
        # El médico registra ausencia para el mismo día del turno
        fecha_ausencia = self.fecha_turno.date()
        url = reverse('app:crear_ausencia')
        data = {
            'motivo': 'Congreso de Sistemas',
            'fecha_inicio': fecha_ausencia,
            'fecha_fin': fecha_ausencia
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) #Redirección exitosa
        
        # Verificamos que el motor de reprogramación transformo el turno
        self.turno.refresh_from_db()
        self.assertEqual(self.turno.estado, 'REPROGRAMACION_PENDIENTE')
        self.assertIsNotNone(self.turno.nueva_fecha_hora)
        self.assertEqual(self.turno.nueva_fecha_hora, self.fecha_turno + timedelta(days=7))
"""Pruebas unitarias del modelo Medico."""

from django.test import TestCase
from app.models import Especialidad, Medico, ObraSocial, Turno, Paciente , Ausencia , Recordatorio  #Agregar imports de modelos faltantes
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


class MedicoModelTest(TestCase):
    """Verifica comportamiento básico y validaciones del modelo."""

    def setUp(self):
        
        self.user = User.objects.create_user(username="lromero", password="test1234")  # Usuario para el médico
        self.especialidad = Especialidad.objects.create(nombre="Pediatría")  # Especialidad para el médico
        self.obra_social = ObraSocial.objects.create(nombre="OSDE")  # Obra social para el médico

        self.medico = Medico.objects.create(
            usuario=self.user,
            nombre="Laura",
            apellido="Romero",
            matricula="MP-9999",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )

    # --- __str__ y métodos simples ---

    def test_str_incluye_apellido_y_nombre(self):
        self.assertIn("Romero", str(self.medico))
        self.assertIn("Laura", str(self.medico))

    def test_nombre_completo(self):
        self.assertEqual(self.medico.nombre_completo(), "Laura Romero")

    def test_cantidad_turnos_inicial_es_cero(self):
        self.assertEqual(self.medico.cantidad_turnos(), 0)

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        medico_test = Medico(
            usuario=self.user,
            nombre="Ana",
            apellido="García",
            matricula="MP-0001",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        errors = medico_test.validate()
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        medico_test = Medico(
            usuario=self.user,
            nombre="",
            apellido="García",
            matricula="MP-0001",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        errors = medico_test.validate()
        self.assertIn("El nombre es obligatorio.", errors)

    def test_validate_matricula_vacia_retorna_error(self):
        medico_test = Medico(
            usuario=self.user,
            nombre="Ana",
            apellido="García",
            matricula="",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        errors = medico_test.validate()
        self.assertIn("La matrícula es obligatoria.", errors)

    # --- new ---

    def test_new_crea_medico_con_datos_validos(self):
        medico, errors = Medico.new(
            usuario=self.user,
            nombre="Carlos",
            apellido="López",
            matricula="MP-1234",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(medico)
        self.assertEqual(medico.apellido, "López")
        self.assertTrue(Medico.objects.filter(matricula="MP-1234").exists())

    def test_new_con_datos_invalidos_retorna_errores_y_no_crea(self):
        count_antes = Medico.objects.count()
        medico, errors = Medico.new(
            usuario=self.user,
            nombre="",
            apellido="",
            matricula="",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        self.assertIsNone(medico)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Medico.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        nueva_especialidad = Especialidad.objects.create(nombre="Cardiología")
        errors = self.medico.update(
            nombre= "Laura",
            apellido= "Romero",
            matricula= "MP-9999",
            especialidad= nueva_especialidad,
            obra_social= self.obra_social
        )
        self.assertEqual(errors, [])
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.especialidad, "Cardiología")

    def test_update_con_datos_invalidos_no_modifica(self):
        errors = self.medico.update(nombre="")
        self.assertTrue(len(errors) > 0)
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.nombre, "Laura")  # El nombre no debería haber cambiado

    # TODO: agregar tests para Paciente y Turno cuando los implementen

class PacienteModelTest(TestCase):

    """TESTS DE MODELO PACIENTE"""

    def setUp(self):
        self.user = User.objects.create_user(username="mgomez", password="test1234")  # Usuario para el paciente
        self.obra_social = ObraSocial.objects.create(nombre="OSDE")  # Obra social para el paciente
        
        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre="Maria", 
            apellido="Gomez",
            dni="12345678",
            email="maria.gomez@mail.com",
            telefono="123456789",
            obra_social=self.obra_social
        )

    def test_str_incluye_apellido_y_nombre(self):
        """"Verifica que el método __str__ del paciente incluya su apellido y nombre."""
        self.assertIn("Gomez", str(self.paciente))
        self.assertIn("Maria", str(self.paciente))

# --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        """Verifica que el método validate retorne una lista vacía cuando los datos son correctos."""
        paciente_test = Paciente(
            usuario=self.user,
            nombre="Carlos", 
            apellido="López",
            dni="87654321",
            email="carlos.lopez@mail.com",
            telefono="987654321",
            obra_social=self.obra_social
        )
        errors = paciente_test.validate()
        self.assertEqual(errors, [])

        def test_validate_dni_con_letras_retorna_error(self):
            """Verifica que el método validate retorne un error cuando el DNI contiene letras."""
            paciente_test = Paciente(
                usuario=self.user,
                nombre="Carlos", 
                apellido="López",
                dni="ABC12345",  # DNI con letras
                email="carlos.lopez@mail.com",
                telefono="987654321",
                obra_social=self.obra_social
            )
            errors = paciente_test.validate()
            self.assertIn("El DNI debe contener solo números.", errors)

        def test_validate_campos_obligatorios_vacios_retorna_errores(self):
            """Verifica que el método validate retorne errores cuando los campos obligatorios están vacíos."""
            paciente_test = Paciente(
                usuario=self.user,
                nombre="",  # Nombre vacío
                apellido="",  # Apellido vacío
                dni="",  # DNI vacío
                email="",  # Email vacío
                telefono="",  # Teléfono vacío
                obra_social=self.obra_social
            )
            errors = paciente_test.validate()
            self.assertIn("El nombre es obligatorio.", errors)
            self.assertIn("El apellido es obligatorio.", errors)
            self.assertIn("El DNI es obligatorio.", errors)
            self.assertIn("El email es obligatorio.", errors)
            self.assertIn("El teléfono es obligatorio.", errors)
            self.assertIn("La obra social es obligatoria.", errors)

# --- new ---
    def test_new_crea_paciente_y_limpiamos_campos(self):
        paciente, errors = Paciente.new(
            usuario=self.user,
            nombre="Carlos", 
            apellido="López",
            dni="87654321",
            email="carlos.lopez@mail.com",
            telefono="987654321",
            obra_social=self.obra_social
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(paciente)

        self.assertEqual(paciente.nombre, "Carlos")
        self.assertEqual(paciente.apellido, "López")
        self.assertEqual(paciente.dni, "87654321")
        self.assertEqual(paciente.email, "carlos.lopez@mail.com")
        self.assertEqual(paciente.telefono, "987654321")
        self.assertEqual(paciente.obra_social, self.obra_social)

        self.assertTrue(Paciente.objects.filter(dni="87654321").exists())

    def test_new_invalido_retorna_errores_y_no_persiste(self):
        """Un intento de creación con datos sucios aborta el guardado y retorna errores."""
        user_falla = User.objects.create_user(username="cfalla", password="test1234")
        count_antes = Paciente.objects.count()

        paciente, errors = Paciente.new(
            usuario=user_falla,
            nombre="",  # Nombre vacío
            apellido="",  # Apellido vacío
            dni="ABC12345",  # DNI con letras
            email="",  # Email vacío
            telefono="",  # Teléfono vacío
            obra_social=self.obra_social
        )
        self.assertIsNone(paciente)
        self.assertTrue(len(errors) >= 2) # Debería haber varios errores
        self.assertEqual(Paciente.objects.count(), count_antes)

# --- update ---

    def test_update_modifica_datos_correctamente(self):
        """Modifica atributos validos y los guarda."""
        errors = self.paciente.update(
            nombre="Carlos", 
            apellido="López",
            dni="87654321",
            email="carlos.lopez@mail.com",
            telefono="987654321",
            obra_social=self.obra_social
        )
        self.assertEqual(errors, [])
        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.nombre, "Carlos")
        self.assertEqual(self.paciente.apellido, "López")
        self.assertEqual(self.paciente.dni, "87654321")
        self.assertEqual(self.paciente.email, "carlos.lopez@mail.com")
        self.assertEqual(self.paciente.telefono, "987654321")
        self.assertEqual(self.paciente.obra_social, self.obra_social)

    def test_update_invalido_retiene_datos_originales(self):
        """Un update con un DNI inválido frena la operación y no modifica los datos."""
        errors = self.paciente.update(dni="ABC12345")  # DNI con letras
        self.assertIn("El DNI debe contener solo números.", errors)

        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.dni, "12345678")  # El DNI no debería haber cambiado

class TurnoModelTest(TestCase):

    """TESTS DE MODELO TURNO"""

    def setUp(self):
        self.medico = Medico.objects.create(
            nombre="Juan", apellido="Perez", matricula="MP-1", especialidad="Cardiología"
        )
        self.paciente = Paciente.objects.create(
            nombre="Maria", apellido="Gomez"
        )

    def test_cancelar_turno_exitoso(self):
        fecha = timezone.now() + timedelta(days=1)
        turno, _ = Turno.new(fecha_hora=fecha, medico=self.medico, paciente=self.paciente)
        errors = turno.cancelar()
        self.assertEqual(len(errors), 0)
        self.assertEqual(turno.estado, "CANCELADO")

    def test_cancelar_turno_pasado_falla(self):
        # Creamos un turno en el pasado 
        fecha_pasada = timezone.now() - timedelta(days=1)
        turno, _ = Turno.new(fecha_hora=fecha_pasada, medico=self.medico, paciente=self.paciente)
        errores = turno.cancelar()
        self.assertNotEqual(len(errores), 0)
        self.assertEqual(turno.estado, "PENDIENTE")
    
    def test_aceptar_turno_exitoso(self):
        turno, _ = Turno.new(fecha_hora=timezone.now() + timedelta(days=1), medico=self.medico, paciente=self.paciente)
        errores = turno.aceptar()
        self.assertEqual(len(errores), 0)
        self.assertEqual(turno.estado, "ACEPTADO")

    def test_aceptar_turno_ya_cancelado_falla(self):
        turno, _ = Turno.new(fecha_hora=timezone.now() + timedelta(days=1), medico=self.medico, paciente=self.paciente)
        turno.cancelar() #cancelamos primero
        #Intenta aceptarlo
        errores = turno.aceptar()
        #Verifico que falle
        self.assertNotEqual(len(errores), 0)
        self.assertEqual(turno.estado, "CANCELADO")

        ''''Test Modelos Ausencia + Recordatorio'''

class AusenciaModelTest(TestCase):

    def setUp(self):
        # Infraestructura base idéntica al ejemplo del profesor
        self.medico = Medico.objects.create(
            nombre="Laura",
            apellido="Romero",
            matricula="MP-9999",
            especialidad="Pediatría",
        )
        self.fecha_i = timezone.now().date()
        self.fecha_f = timezone.now().date() + timedelta(days=2)
        
        self.ausencia, _ = Ausencia.new(
            medico=self.medico,
            motivo="Congreso",
            fecha_inicio=self.fecha_i,
            fecha_fin=self.fecha_f
        )

        # --- __str__ y métodos de negocio ---

    def test_str_incluye_medico_y_fecha(self):
        self.assertIn("Laura", str(self.ausencia))
        self.assertIn("Romero", str(self.ausencia))

    def test_es_vigente_hoy_retorna_true(self):
        """Método de negocio: caso exitoso (está ocurriendo hoy)."""
        self.assertTrue(self.ausencia.es_vigente())

    def test_es_vigente_pasada_retorna_false(self):
        """Método de negocio: caso alternativo (ausencia antigua)."""
        hace_cinco_dias = timezone.now().date() - timedelta(days=5)
        hace_dos_dias = timezone.now().date() - timedelta(days=2)
        ausencia_vieja, _ = Ausencia.new(
            medico=self.medico, motivo="Licencia", fecha_inicio=hace_cinco_dias, fecha_fin=hace_dos_dias
        )
        self.assertFalse(ausencia_vieja.es_vigente())

        # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = self.ausencia.validate()
        self.assertEqual(errors, [])

    def test_validate_fechas_invertidas_retorna_error(self):
        self.ausencia.fecha_inicio = timezone.now().date() + timedelta(days=5)
        self.ausencia.fecha_fin = timezone.now().date()  # Fin antes que inicio
        errors = self.ausencia.validate()
        self.assertTrue(len(errors) > 0)

    # --- new ---

    def test_new_crea_ausencia_con_datos_validos(self):
        inicio = timezone.now().date() + timedelta(days=10)
        fin = timezone.now().date() + timedelta(days=12)
        ausencia, errors = Ausencia.new(medico=self.medico, motivo="Vacaciones", fecha_inicio=inicio, fecha_fin=fin)
        self.assertEqual(errors, [])
        self.assertIsNotNone(ausencia)
        self.assertEqual(ausencia.motivo, "Vacaciones")
        self.assertTrue(Ausencia.objects.filter(motivo="Vacaciones").exists())

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.ausencia.update(motivo="Enfermedad")
        self.assertEqual(errors, [])
        self.ausencia.refresh_from_db()
        self.assertEqual(self.ausencia.motivo, "Enfermedad")


class RecordatorioModelTest(TestCase):
    
    def setUp(self):
        self.medico = Medico.objects.create(
            nombre="Laura", apellido="Romero", matricula="MP-9999", especialidad="Pediatría"
        )
        self.paciente = Paciente.objects.create(nombre="Maria", apellido="Gomez")
        self.turno, _ = Turno.new(
            fecha_hora=timezone.now() + timedelta(days=1), medico=self.medico, paciente=self.paciente
        )
        self.recordatorio, _ = Recordatorio.new(
            turno=self.turno,
            fecha_envio=timezone.now(),
            tipo="SMS",
            asunto="Aviso",
            mensaje="Recordatorio"
        )

    # --- __str__ y métodos de negocio ---

    def test_str_incluye_asunto(self):
        self.assertIn("Aviso", str(self.recordatorio))

    def test_marcar_como_leido_modifica_estado_exitoso(self):
        """Método de negocio: caso exitoso."""
        self.assertFalse(self.recordatorio.leido)
        errors = self.recordatorio.marcar_como_leido()
        self.assertEqual(errors, [])
        self.assertTrue(self.recordatorio.leido)

        # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = self.recordatorio.validate()
        self.assertEqual(errors, [])

    # --- new ---

    def test_new_crea_recordatorio_con_datos_validos(self):
        rec, errors = Recordatorio.new(
            turno=self.turno, fecha_envio=timezone.now(), tipo="EMAIL", asunto="Turno Mañana", mensaje="Test"
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(rec)
        self.assertTrue(Recordatorio.objects.filter(asunto="Turno Mañana").exists())

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.recordatorio.update(asunto="Nuevo Asunto")
        self.assertEqual(errors, [])
        self.recordatorio.refresh_from_db()
        self.assertEqual(self.recordatorio.asunto, "Nuevo Asunto")
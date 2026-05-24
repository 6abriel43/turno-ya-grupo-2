"""Pruebas unitarias del modelo Medico."""

from django.test import TestCase
from app.models import Medico, Turno, Paciente
from django.utils import timezone
from datetime import timedelta

class MedicoModelTest(TestCase):
    """Verifica comportamiento básico y validaciones del modelo."""

    def setUp(self):
        self.medico = Medico.objects.create(
            nombre="Laura",
            apellido="Romero",
            matricula="MP-9999",
            especialidad="Pediatría",
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
        errors = Medico.validate("Ana", "García", "MP-0001", "Cardiología")
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        errors = Medico.validate("", "García", "MP-0001", "Cardiología")
        self.assertTrue(len(errors) > 0)

    def test_validate_matricula_vacia_retorna_error(self):
        errors = Medico.validate("Ana", "García", "", "Cardiología")
        self.assertTrue(len(errors) > 0)

    # --- new ---

    def test_new_crea_medico_con_datos_validos(self):
        medico, errors = Medico.new("Carlos", "López", "MP-1234", "Clínica Médica")
        self.assertEqual(errors, [])
        self.assertIsNotNone(medico)
        self.assertEqual(medico.apellido, "López")
        self.assertTrue(Medico.objects.filter(matricula="MP-1234").exists())

    def test_new_con_datos_invalidos_retorna_errores_y_no_crea(self):
        count_antes = Medico.objects.count()
        medico, errors = Medico.new("", "", "", "")
        self.assertIsNone(medico)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Medico.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.medico.update("Laura", "Romero", "MP-9999", "Cardiología")
        self.assertEqual(errors, [])
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.especialidad, "Cardiología")

    def test_update_con_datos_invalidos_no_modifica(self):
        errors = self.medico.update("", "", "", "")
        self.assertTrue(len(errors) > 0)
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.nombre, "Laura")  # sin cambios

    # TODO: agregar tests para Paciente y Turno cuando los implementen
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